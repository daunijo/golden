# -*- coding: utf-8 -*-
# Copyright (c) 2018, RSS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import nowdate, cstr, flt
from frappe import msgprint, _
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe.model import display_fieldtypes

class Packing(Document):
	def validate(self):
		self.check_items()
		self.update_so()
		self.update_total_box()
		self.check_completed()

	def check_items(self):
		for row in self.items:
			if flt(row.qty_packing) <= 0:
				frappe.throw(_("Qty Packing is mandatory in item line {0}").format(row.idx))

	def update_so(self):
		if self.is_new() and self.sales_order:
			frappe.db.sql("""update `tabSales Order` set golden_status = 'Pack' where `name` = %s""", self.sales_order)

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

	def delivery_note_insert(self):
		delivery_note = frappe.get_doc({
			"doctype": "Delivery Note",
			"customer": self.customer,
			"packing": self.name,
			"posting_date": self.posting_date,
			"posting_time": self.posting_time,
			"set_posting_time": self.set_posting_time,
			"taxes_and_charges": self.taxes_and_charges
		})
		delivery_note.insert()
		dn = frappe.get_doc("Delivery Note", delivery_note.name)
		for row in self.items:
			dn.append("items", {
				"item_code": row.item_code,
				"item_name": row.item_name,
				"description": row.description,
				"qty": row.qty,
				"uom": row.uom,
				"conversion_factor": row.conversion_factor,
				"rate": row.rate,
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
			"expedition": self.expedition,
			"box": self.total_box,
			"sales_order": self.sales_order
		})
		self.save()

	def on_cancel(self):
		if self.status == "Submitted":
			frappe.db.set(self, 'status', 'Cancelled')
			ps = frappe.get_doc("Packing Simple", {"parent": self.name})
			ps.delete()
#			frappe.db.sql("""delete from `tabPacking Simple` where parent = %s""", self.name)
			if self.sales_order:
				frappe.db.sql("""update `tabSales Order` set golden_status = 'Pick' where `name` = %s""", self.sales_order)
			dn = frappe.get_doc("Delivery Note", {"packing": self.name})
			dn.cancel()
			dn.delete()
		else:
			frappe.throw(_("You can't cancel this document if status is sent"))

	def check_completed(self):
		if self.is_completed:
			frappe.throw(_("You cannot create Packing from completed Sales Order"))

@frappe.whitelist()
def get_picking_list(source_name, target_doc=None):
    def set_missing_values(source, target):
        target.run_method("set_missing_values")

    doc = get_mapped_doc("Picking", source_name, {
		"Picking": {
			"doctype": "Packing",
			"validation": {
				"docstatus": ["=", 1],
			},
            "field_no_map": ["naming_series", "posting_date", "posting_time", "set_posting_time", "total_box"]
		},
		"Picking Item": {
			"doctype": "Packing Picking",
			"condition":lambda doc: doc.idx == 1,
		},
	}, target_doc, set_missing_values)
    return doc
