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
	def validate(self):
		pass

	def on_submit(self):
		self.check_expedition()
		self.check_barcode()
		self.check_barcode2()
		self.update_barcode()
		self.check_detail()
		self.check_packing()
		self.update_packing()
		self.update_detail()
		self.update_sales_order()

	def check_expedition(self):
		for row in self.details:
			if not row.expedition:
				frappe.throw(_("Expedition is mandatory in row {0}").format(row.idx))

	def check_barcode(self):
		if self.bcode:
			packing = []
			for row in self.bcode:
				if row.packing not in packing:
					packing.append(row.packing)

			for i in packing:
				count_packing = frappe.db.sql("""select total_box from `tabPacking` where `name` = %s""", i)[0][0]
				count_barcode = frappe.db.sql("""select count(*) from `tabDelivery Order Barcode` where parent = %s and packing = %s""", (self.name, i))[0][0]
				if flt(count_packing != count_barcode):
					frappe.throw(_("Packing {0} have {1} box(s) but you only insert {2} box(s) in barcode").format(i, int(count_packing), int(count_barcode)))

	def check_barcode2(self):
		if self.bcode:
			for row in self.bcode:
				check_do = frappe.db.sql("""select count(*) from `tabPacking Barcode` where `name` = %s and delivery_order is not null""", row.barcode_1)[0][0]
				if flt(check_do) == 1:
					frappe.throw(_("Barcode {0} in row {1} already delivered").format(row.barcode, row.idx))

	def update_barcode(self):
		if self.bcode:
			for row in self.bcode:
				frappe.db.sql("""update `tabPacking Barcode` set delivery_order = %s where `name` = %s""", (self.name, row.barcode_1))

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

	def update_sales_order(self):
		for row in self.details:
			if row.sales_order:
				frappe.db.sql("""update `tabSales Order` set golden_status = 'Wait for Delivery and Bill' where `name` = %s""", row.sales_order)
				frappe.db.sql("""update `tabPacking` set delivery_order = %s, is_completed = '1' where `name` = %s""", (self.name, row.packing))

	def on_cancel(self):
		self.delete_barcode()
		self.delete_packing()
		self.cancel_sales_order()

	def delete_barcode(self):
		if self.bcode:
			for row in self.bcode:
				frappe.db.sql("""update `tabPacking Barcode` set delivery_order = null where `name` = %s""", row.barcode_1)

	def delete_packing(self):
		for row in self.details:
			frappe.db.sql("""update `tabPacking` set delivery_order = null where `name` = %s""", row.packing)

	def cancel_sales_order(self):
		for row in self.details:
			if row.sales_order:
				frappe.db.sql("""update `tabSales Order` set golden_status = 'Packed' where `name` = %s""", row.sales_order)
				frappe.db.sql("""update `tabPacking` set delivery_order = null, is_completed = '0' where `name` = %s""", row.packing)

@frappe.whitelist()
def get_packing_list(source_name, target_doc=None):
	def set_missing_values(source, target):
		target.run_method("set_missing_values")

	def update_item(source, target, source_parent):
		st = frappe.db.get_value("Packing", source.parent, ["customer", "customer_name", "posting_date", "total_box", "sales_order"], as_dict=1)
		target.packing_date = st.posting_date
		# target.do_no = "DO-"+source.parent[3::]
		target.customer = st.customer
		target.customer_name = st.customer_name
		target.total_box = st.total_box
		target.sales_order = st.sales_order

	doclist = get_mapped_doc("Packing", source_name, {
		"Packing": {
			"doctype": "Delivery Order",
			"validation": {
				"docstatus": ["=", 1],
			},
            "field_no_map": ["naming_series", "posting_date", "posting_time", "set_posting_time", "customer", "sales_order"]
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

def packing_query(doctype, txt, searchfield, start, page_len, filters):
    return frappe.db.sql("""select `name`, concat('Customer: ', customer), concat('<br>Sales Order: ', sales_order) from `tabPacking`
        where docstatus = '1' and delivery_order is null
            and (`name` like %(txt)s or customer like %(txt)s)
			and `name` not in (%(cond)s)
            {mcond}
        limit %(start)s, %(page_len)s""".format(**{
            'key': searchfield,
            'mcond':get_match_cond(doctype)
        }), {
            'txt': "%%%s%%" % txt,
            '_txt': txt.replace("%", ""),
            'start': start,
            'page_len': page_len,
            'cond': filters.get("not_in")
        })

@frappe.whitelist()
def get_expedition_detail(name):
	exp = frappe.db.get_value("Expedition Detail", name, ["contact_name", "handphone", "email_id"], as_dict=1)
	si_rate = {
		'contact_name': exp.contact_name,
		'phone': exp.handphone,
		'email_id': exp.email_id
	}
	return si_rate

@frappe.whitelist()
def get_packing_barcode(barc, notin):
	si_list = []
	bcode = barc[0:12]
	if notin != "-":
		check_bcode = frappe.db.sql("select count(*) from `tabPacking Barcode` where docstatus = '1' and delivery_order is null and barcode_1 = %s and barcode_1 not in ("+notin+")", bcode)[0][0]
	else:
		check_bcode = frappe.db.sql("select count(*) from `tabPacking Barcode` where docstatus = '1' and delivery_order is null and barcode_1 = %s", bcode)[0][0]
	if flt(check_bcode) == 1:
		list = frappe.db.get_value("Packing Barcode", bcode, ["barcode_1", "box", "parent"], as_dict=1)
		si_list.append(frappe._dict({
			'barcode': barc,
			'barcode_1': list.barcode_1,
			'box': list.box,
			'packing': list.parent
		}))
	return si_list

@frappe.whitelist()
def get_packing_from_barcode(bcode, pl):
	si_list = []
	bcode = bcode[0:12]
	if pl != "-":
		check_packing = frappe.db.sql("select count(*) from `tabPacking Barcode` where parent in ("+pl+") and barcode_1 = %s", bcode)[0][0]
		if flt(check_packing) == 0:
			parent = frappe.db.get_value("Packing Barcode", bcode, "parent")
			packing = frappe.db.get_value("Packing", parent, ["customer", "customer_name", "posting_date", "total_box", "sales_order"], as_dict=1)
			si_list.append(frappe._dict({
				'packing': parent,
				'customer': packing.customer,
				'customer_name': packing.customer_name,
				'packing_date': packing.posting_date,
				'total_box': packing.total_box,
				'sales_order': packing.sales_order
			}))
	else:
		parent = frappe.db.get_value("Packing Barcode", bcode, "parent")
		packing = frappe.db.get_value("Packing", parent, ["customer", "customer_name", "posting_date", "total_box", "sales_order"], as_dict=1)
		si_list.append(frappe._dict({
			'packing': parent,
			'customer': packing.customer,
			'customer_name': packing.customer_name,
			'packing_date': packing.posting_date,
			'total_box': packing.total_box,
			'sales_order': packing.sales_order
		}))
	return si_list
