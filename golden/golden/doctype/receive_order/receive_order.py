# -*- coding: utf-8 -*-
# Copyright (c) 2018, RSS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import nowdate, cstr, flt
from frappe import msgprint, _
from frappe.model.mapper import get_mapped_doc

class ReceiveOrder(Document):
	def validate(self):
		self.check_item()

	def on_submit(self):
		self.create_purchase_receipt()
		self.insert_pr_item()
		self.submit_purchase_receipt()

	def on_cancel(self):
		self.delete_purchase_receipt()

	def check_item(self):
		temp = []
		for row in self.items:
			if row.po_detail in temp:
				frappe.throw(_("Purchase Order {0} is duplicate").format(row.purchase_order))
			else:
				temp.append(row.po_detail)

	def create_purchase_receipt(self):
		purchase_order = frappe.db.sql("""select distinct(purchase_order) as po_name from `tabReceive Order Item` where parent = %s and qty != 0""", self.name, as_dict=1)
		for po in purchase_order:
			source = frappe.db.get_value("Purchase Order", po.po_name, ["supplier", "supplier_name"], as_dict=1)
			pr = frappe.get_doc({
            	"doctype": "Purchase Receipt",
            	"supplier": source.supplier,
				"supplier_name": source.supplier_name,
				"receive_order": self.name,
				"rss_po": po.po_name,
            	"posting_date": self.posting_date,
				"posting_time": self.posting_time,
				"set_posting_time": self.set_posting_time
            })
			pr.save()

	def insert_pr_item(self):
		for row in self.items:
			if flt(row.qty) >= 1:
				pr = frappe.get_doc("Purchase Receipt", {"receive_order": self.name, "rss_po": row.purchase_order})
				po = frappe.db.get_value("Purchase Order", row.purchase_order, ["schedule_date"], as_dict=1)
				pr.append("items", {
					"item_code": row.item_code,
					"item_name": row.item_name,
					"description": row.description,
					"qty": row.qty,
					"uom": row.uom,
					"stock_uom": row.stock_uom,
					"conversion_factor": row.conversion_factor,
					"warehouse": self.accepted_location,
					"purchase_order": row.purchase_order,
					"purchase_order_item": row.po_detail,
					"schedule_date": po.schedule_date,
					"stock_qty": row.qty
				})
				pr.save()

	def submit_purchase_receipt(self):
		count = frappe.db.sql("""select count(*) from `tabPurchase Receipt` where docstatus = '0' and receive_order = %s""", self.name)[0][0]
		if flt(count) >= 1:
			purchase_receipt = frappe.db.sql("""select * from `tabPurchase Receipt` where docstatus = '0' and receive_order = %s""", self.name, as_dict=1)
			for pr in purchase_receipt:
				submit_pr = frappe.get_doc("Purchase Receipt", pr.name)
				submit_pr.submit()

	def delete_purchase_receipt(self):
		count = frappe.db.sql("""select count(*) from `tabPurchase Receipt` where docstatus = '1' and receive_order = %s""", self.name)[0][0]
		if flt(count) >= 1:
			purchase_receipt = frappe.db.sql("""select * from `tabPurchase Receipt` where docstatus = '1' and receive_order = %s""", self.name, as_dict=1)
			for pr in purchase_receipt:
				submit_pr = frappe.get_doc("Purchase Receipt", pr.name)
				submit_pr.cancel()
				submit_pr.delete()

@frappe.whitelist()
def get_purchase_order(source_name, target_doc=None):
	def set_missing_values(source, target):
		target.run_method("set_missing_values")

	def update_item(source, target, source_parent):
		target.supplier = frappe.db.sql("""select supplier from `tabPurchase Order` where `name` = %s""", source.parent)[0][0]
		target.supplier_name = frappe.db.sql("""select supplier_name from `tabPurchase Order` where `name` = %s""", source.parent)[0][0]

	doclist = get_mapped_doc("Purchase Order", source_name, {
		"Purchase Order": {
			"doctype": "Receive Order",
			"validation": {
				"docstatus": ["=", 1],
			},
            "field_no_map": ["naming_series", "posting_date", "posting_time", "set_posting_time"]
		},
		"Purchase Order Item": {
			"doctype": "Receive Order Item",
			"field_map": {
				"parent": "purchase_order",
				"name": "po_detail"
			},
			"field_no_map": ["qty"],
			"postprocess": update_item
		},
	}, target_doc, set_missing_values)

	return doclist
