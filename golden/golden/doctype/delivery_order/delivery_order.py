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

class DeliveryOrder(Document):
	def on_submit(self):
		self.check_detail()

	def check_detail(self):
		temp = []
		for row in self.details:
			temp.append(row.packing)
			if row.packing in temp:
				frappe.throw(_("Packing <b>{0}</b> is double").format(row.packing))

@frappe.whitelist()
def get_packing_list(source_name, target_doc=None):
	def set_missing_values(source, target):
		target.run_method("set_missing_values")

	def update_item(source, target, source_parent):
		st = frappe.db.get_value("Packing", source.parent, ["customer", "customer_name", "posting_date", "total_box"], as_dict=1)
		target.customer = st.customer
		target.customer_name = st.customer_name
		target.packing_date = st.posting_date
		target.total_box = st.total_box

	doclist = get_mapped_doc("Packing", source_name, {
		"Packing": {
			"doctype": "Delivery Order",
			"validation": {
				"docstatus": ["=", 1],
			},
            "field_no_map": ["naming_series", "posting_date", "posting_time", "set_posting_time"]
		},
		"Packing Item": {
			"doctype": "Delivery Order Detail",
			"field_map": {
				"location": "warehouse",
			},
			"condition":lambda doc: doc.idx == 1,
			"postprocess": update_item
		},
	}, target_doc, set_missing_values)

	return doclist
