# -*- coding: utf-8 -*-
# Copyright (c) 2018, RSS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import nowdate, cstr, flt
from frappe import msgprint, _
from frappe.model.mapper import get_mapped_doc
from frappe.model import display_fieldtypes

class Packing(Document):
	def validate(self):
		self.check_items()
		self.update_so()
		self.update_total_box()
		self.box_shorted()
		self.check_completed()
		self.check_picking()

	def check_items(self):
		for row in self.items:
			if flt(row.qty_packing) <= 0:
				frappe.throw(_("Qty Packing is mandatory in item line {0}").format(row.idx))

	def update_so(self):
		if self.is_new() and self.sales_order:
			frappe.db.sql("""update `tabSales Order` set golden_status = 'In Packing' where `name` = %s""", self.sales_order)

	def box_shorted(self):
		temp = []
		for row in self.items:
			data = row.box.split(",")
			for i in data:
				a = int(i)
				b = str(a)
				temp.append(a)

		for t in range(1,int(self.total_box)):
			if t not in temp:
				frappe.throw(_("There is no box number {0} in the Box").format(t))

	def update_total_box(self):
		maks = 0
		for row in self.items:
			if flt(row.maks_box) >= flt(maks):
				maks = row.maks_box

		frappe.db.set(self, 'total_box', maks)

	def on_submit(self):
		self.delivery_note_insert()
		self.update_status()
		self.update_packing_simple()
		self.update_bin()
		self.update_picking()

	def delivery_note_insert(self):
		so = frappe.db.get_value("Sales Order", self.sales_order, ["rss_sales_person", "rss_sales_name"], as_dict=1)
		delivery_note = frappe.get_doc({
			"doctype": "Delivery Note",
			"customer": self.customer,
			"rss_sales_person": so.rss_sales_person,
			"rss_sales_name": so.rss_sales_name,
			"packing": self.name,
			"posting_date": self.posting_date,
			"posting_time": self.posting_time,
			"set_posting_time": self.set_posting_time,
			"taxes_and_charges": self.taxes_and_charges
		})
		delivery_note.save()
		dn = frappe.get_doc("Delivery Note", delivery_note.name)
		for row in self.items:
			soi = frappe.db.get_value("Sales Order Item", row.so_detail, ["rate"], as_dict=1)
			dn.append("items", {
				"item_code": row.item_code,
				"item_name": row.item_name,
				"description": row.description,
				"qty": row.qty_packing,
				"uom": row.uom,
				"stock_uom": row.stock_uom,
				"conversion_factor": row.conversion_factor,
				"rate": soi.rate,
				"warehouse": row.warehouse,
				"against_sales_order": row.against_sales_order,
				"so_detail": row.so_detail
			})
			dn.save()
		if not self.taxes_and_charges and flt(self.total_taxes_and_charges) != 0:
			for tax in self.taxes:
				dn.append("taxes", {
					"charge_type": tax.charge_type,
					"account_head": tax.account_head,
					"cost_center": tax.cost_center,
					"description": tax.description,
					"rate": tax.rate
				})
				dn.save()
		dn.submit()

	def update_status(self):
		frappe.db.set(self, 'status', 'Submitted')

	def update_packing_simple(self):
		self.append("simple", {
			"customer": self.customer,
			"customer_name": self.customer_name,
			"expedition": self.expedition or None,
			"box": self.total_box,
			"sales_order": self.sales_order
		})
		self.save()

	def update_bin(self):
		for row in self.items:
			if row.picking:
				bin = frappe.db.get_value("Bin", {"item_code": row.item_code, "warehouse": row.warehouse}, ["name", "ito", "ito_qty"], as_dict=1)
				if bin.ito:
					if flt(bin.ito_qty) >= flt(row.qty_packing):
						diff = flt(bin.ito_qty) - flt(row.qty_packing)
						frappe.db.sql("""update `tabBin` set ito = null, ito_qty = %s where `name` = %s""", (diff, bin.name))
					else:
						frappe.db.sql("""update `tabBin` set ito = null, ito_qty = 0 where `name` = %s""", bin.name)

	def update_picking(self):
		for row in self.picking_list:
			frappe.db.sql("""update `tabPicking` set packing = %s where `name` = %s""", (self.name, row.picking))

	def on_cancel(self):
		self.delete_dn()
		self.delete_picking()

	def delete_dn(self):
		if self.status == "Submitted":
			frappe.db.set(self, 'status', 'Cancelled')
			ps = frappe.get_doc("Packing Simple", {"parent": self.name})
			ps.delete()
			if self.sales_order:
				frappe.db.sql("""update `tabSales Order` set golden_status = 'In Picking' where `name` = %s""", self.sales_order)
			dn = frappe.get_doc("Delivery Note", {"packing": self.name})
			dn.cancel()
			dn.delete()
		else:
			frappe.throw(_("You can't cancel this document if status is sent"))

	def delete_picking(self):
		for row in self.picking_list:
			frappe.db.sql("""update `tabPicking` set packing = null where `name` = %s""", row.picking)

	def on_trash(self):
		if self.sales_order and self.docstatus == 0:
			frappe.db.sql("""update `tabSales Order` set golden_status = 'In Picking' where `name` = %s""", self.sales_order)

	def check_completed(self):
		if self.is_completed:
			frappe.throw(_("You cannot create Packing from completed Sales Order"))

	def check_picking(self):
		if self.picking_list:
			temp = []
			for pick in self.picking_list:
				if pick.picking in temp:
					frappe.throw(_("Picking {0} double").format(pick.picking))
				temp.append(pick.picking)

@frappe.whitelist()
def get_picking_list(source_name, target_doc=None):
	def set_missing_values(source, target):
		target.run_method("set_missing_values")

	def update_item(source, target, source_parent):
		target.description = frappe.db.sql("""select description from `tabSales Order Item` where `name` = %s""", source.so_detail)[0][0]

	doclist = get_mapped_doc("Picking", source_name, {
		"Picking": {
			"doctype": "Packing",
			"validation": {
				"docstatus": ["=", 1],
			},
            "field_no_map": ["naming_series", "posting_date", "posting_time", "set_posting_time", "total_box"]
		},
		"Picking Item": {
			"doctype": "Packing Item",
			"field_map": {
				"location": "warehouse",
				"sales_order": "against_sales_order",
				"so_detail": "so_detail",
				"name": "picking_detail"
			},
			"postprocess": update_item
		},
		"Picking Simple": {
			"doctype": "Packing Picking",
		}
	}, target_doc, set_missing_values)

	return doclist
