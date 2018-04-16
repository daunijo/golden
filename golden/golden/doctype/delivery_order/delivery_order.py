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
from frappe.desk.reportview import get_match_cond, get_filters_cond

class DeliveryOrder(Document):
	def on_update(self):
		for row in self.details:
			row.do_no = row.name
			# frappe.db.sql("""update `tabDelivery Order Detail` set do_no = %s where `name` = %s""", (row.name, row.name))

	def on_submit(self):
		self.check_detail()
		self.check_packing()
		self.update_packing()
		self.update_detail()

	def check_detail(self):
		temp = []
		for row in self.details:
			if row.packing in temp:
				frappe.throw(_("Packing <b>{0}</b> is double").format(row.packing))
			temp.append(row.packing)

	def check_packing(self):
		for row in self.details:
			count_do = frappe.db.sql("""select count(*) from `tabPacking` where `name`= %s and delivery_order = %s""", (row.packing, self.name))[0][0]
			if flt(count_do) != 0:
				frappe.throw(_("Packing {0} is already used by another Delivery Order").format(row.packing))

	def update_packing(self):
		for row in self.details:
			frappe.db.sql("""update `tabPacking` set delivery_order = %s where `name` = %s""", (self.name, row.packing))

	def update_detail(self):
		for row in self.details:
			frappe.db.sql("""update `tabDelivery Order Detail` set transaction_date = %s where `name` = %s""", (row.packing_date, row.name))

	def on_cancel(self):
		self.delete_packing()

	def delete_packing(self):
		for row in self.details:
			frappe.db.sql("""update `tabPacking` set delivery_order = null where `name` = %s""", row.packing)

@frappe.whitelist()
def get_packing_list(source_name, target_doc=None):
	def set_missing_values(source, target):
		target.run_method("set_missing_values")

	def update_item(source, target, source_parent):
		st = frappe.db.get_value("Packing", source.parent, ["customer", "customer_name", "posting_date", "total_box"], as_dict=1)
		target.packing_date = st.posting_date
		# target.do_no = "DO-"+source.parent[3::]
		target.customer = st.customer
		target.customer_name = st.customer_name
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

def contact_query(doctype, txt, searchfield, start, page_len, filters):
    return frappe.db.sql("""select `name`, handphone, email_id from `tabExpedition Detail`
        where docstatus != '2'
            and contact_name like %(txt)s
            and parent = %(cond)s
            {mcond}
        limit %(start)s, %(page_len)s""".format(**{
            'key': searchfield,
            'mcond':get_match_cond(doctype)
        }), {
            'txt': "%%%s%%" % txt,
            '_txt': txt.replace("%", ""),
            'start': start,
            'page_len': page_len,
            'cond': filters.get("link_name")
        })
