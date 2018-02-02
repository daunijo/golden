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

	def check_items(self):
		for row in self.items:
			if flt(row.qty_packing) <= 0:
				frappe.throw(_("Qty Packing is mandatory in item line {0}").format(row.idx))

	def update_so(self):
		if self.is_new() and self.sales_order:
			frappe.db.sql("""update `tabSales Order` set golden_status = 'Pack' where `name` = %s""", self.sales_order)

	def on_submit(self):
		self.delivery_note_insert()

	def delivery_note_insert(self):
		delivery_note = frappe.get_doc({
			"doctype": "Delivery Note",
			"customer": self.customer,
			"posting_date": self.posting_date,
			"posting_time": self.posting_time,
			"set_posting_time": self.set_posting_time,
			"taxes_and_charges": self.taxes_and_charges
		})
		delivery_note.insert()
		for row in self.items:
			dni = frappe.get_doc({
				"doctype": "Delivery Note Item",
				"parent": delivery_note.name,
				"parentfield": "items",
				"parenttype": "Delivery Note",
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
			dni.insert()
		if not self.taxes_and_charges and flt(self.total_taxes_and_charges) != 0:
			for tax in self.taxes:
				dnt = frappe.get_doc({
					"doctype": "Sales Taxes and Charges",
					"parent": delivery_note.name,
					"parentfield": "taxes",
					"parenttype": "Delivery Note",
					"charge_type": tax.charge_type,
					"account_head": tax.account_head,
					"cost_center": tax.cost_center,
					"description": tax.description,
					"rate": tax.rate,

				})
				dnt.insert()
		dn = frappe.get_doc("Delivery Note", delivery_note.name)
		dn.submit()

	def on_cancel(self):
		if self.sales_order:
			frappe.db.sql("""update `tabSales Order` set golden_status = 'Pick' where `name` = %s""", self.sales_order)
