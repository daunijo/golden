# -*- coding: utf-8 -*-
# Copyright (c) 2018, RSS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import cstr, flt
from frappe import msgprint, _
from frappe.model.mapper import get_mapped_doc

class DeliveryKeeptrack(Document):
	def validate(self):
		self.update_transaction_date()

	def update_transaction_date(self):
		self.transaction_date = self.posting_date
		self.is_completed = 0
		# frappe.db.set(self, 'transaction_date', self.posting_date)
		# frappe.db.set(self, 'is_completed', 0)

	def on_submit(self):
		self.check_km()
		self.check_packing()
		self.update_status_so()
		self.update_delivery_order()

	def check_km(self):
		if self.km_begin <= 0 or self.km_end <= 0:
			frappe.throw(_("KM Begin & KM End is mandatory"))

	def update_status_so(self):
		for row in self.details:
			frappe.db.sql("""update `tabSales Order` set previous_golden_status = golden_status, golden_status = 'Delivering' where `name` = %s""", row.sales_order)

	def update_delivery_order(self):
		for row in self.details:
			if row.delivery_order:
				frappe.db.sql("""update `tabDelivery Order Detail` set delivery_keeptrack = %s where `name` = %s""", (self.name, row.delivery_order))

	def on_cancel(self):
		self.cancel_so_status()
		self.cancel_do_status()

	def cancel_so_status(self):
		for row in self.details:
			frappe.db.sql("""update `tabSales Order` set golden_status = previous_golden_status, previous_golden_status = null, delivery_keeptrack = null where `name` = %s""", row.sales_order)

	def cancel_do_status(self):
		for row in self.details:
			frappe.db.sql("""update `tabDelivery Order Detail` set delivery_keeptrack = null where `name` = %s""", row.delivery_order)

	# def on_trash(self):
	# 	frappe.db.sql("""update `tabSales Order` set golden_status = previous_golden_status, previous_golden_status = null, delivery_keeptrack = null where delivery_keeptrack = %s""", self.name)

	def update_sales_order(self):
		pass
		# if self.is_new():
		# 	for row in self.details:
		# 		so_status = frappe.db.sql("""select golden_status from `tabSales Order` where `name` = %s""", row.sales_order)[0][0]
		# 		frappe.db.sql("""update `tabSales Order` set golden_status = 'Delivering', previous_golden_status = %s, delivery_keeptrack = %s where `name` = %s""", (so_status, self.name, row.sales_order))
		# else:
		# 	frappe.db.sql("""update `tabSales Order` set golden_status = previous_golden_status, previous_golden_status = null, delivery_keeptrack = null where delivery_keeptrack = %s""", self.name)
		# 	for row in self.details:
		# 		so_status = frappe.db.sql("""select golden_status from `tabSales Order` where `name` = %s""", row.sales_order)[0][0]
		# 		frappe.db.sql("""update `tabSales Order` set golden_status = 'Delivering', previous_golden_status = %s, delivery_keeptrack = %s where `name` = %s""", (so_status, self.name, row.sales_order))

	def check_packing(self):
		for row in self.details:
			check1 = frappe.db.sql("""select count(*) from `tabDelivery Order Detail` where docstatus = '1' and delivery_keeptrack is not null and delivery_return is null and `name` = %s""", row.delivery_order)[0][0]
			if flt(check1) != 0:
				frappe.throw(_("Delivery Order {0} already used in other Delivery Keeptrack").format(row.delivery_order))
			else:
				frappe.db.sql("""update `tabDelivery Order Detail` set delivery_return = null where `name` = %s""", row.delivery_order)
		# if self.is_new():
		# 	for row in self.details:
		# 		check_pl = frappe.db.sql("""select count(*) from `tabDelivery Keeptrack Detail` where packing = %s and docstatus != '2'""", row.packing)[0][0]
		# 		if flt(check_pl) != 0:
		# 			frappe.throw(_("Packing List {0} already used in other Delivery Keeptrack").format(row.packing))
		# else:
		# 	for row in self.details:
		# 		check_pl = frappe.db.sql("""select count(*) from `tabDelivery Keeptrack Detail` where parent != %s and packing = %s and docstatus != '2'""", (self.name, row.packing))[0][0]
		# 		if flt(check_pl) != 0:
		# 			frappe.throw(_("Packing List {0} already used in other Delivery Keeptrack").format(row.packing))

@frappe.whitelist()
def get_delivery_order(source_name, target_doc=None):
	def set_missing_values(source, target):
		target.run_method("set_missing_values")

	packing = frappe.db.get_value("Delivery Order Detail", source_name, "packing")

	def update_item(source, target, source_parent):
		target.delivery_order = source_name
		target.expedition = frappe.db.get_value("Delivery Order Detail", source_name, "expedition")

	doc = get_mapped_doc("Packing", packing, {
		"Packing": {
			"doctype": "Delivery Keeptrack",
			"validation": {
				"docstatus": ["=", 1],
			},
            "field_no_map": ["posting_date", "posting_time", "set_posting_time", "total_box", "customer", "sales_order"]
		},
		"Packing Simple": {
			"doctype": "Delivery Keeptrack Detail",
			"postprocess": update_item
		},
	}, target_doc, set_missing_values)
	return doc

@frappe.whitelist()
def make_delivery_return(source_name, target_doc=None):
    def set_missing_values(source, target):
        target.run_method("set_missing_values")

    doc = get_mapped_doc("Delivery Keeptrack", source_name, {
		"Delivery Keeptrack": {
			"doctype": "Delivery Return",
			"validation": {
				"docstatus": ["=", 1],
			},
		},
		"Delivery Keeptrack Detail": {
			"doctype": "Delivery Return Detail",
			"field_map": {
				"parent": "delivery_keeptrack",
				"name": "delivery_keeptrack_detail",
			},
		},
	}, target_doc, set_missing_values)
    return doc

@frappe.whitelist()
def set_complete(name):
	frappe.db.sql("""update `tabDelivery Keeptrack` set is_completed = '1' where `name` = %s""", name)
	so_list = frappe.db.sql("""select * from `tabDelivery Keeptrack Detail` where parent = %s""", name, as_dict=1)
	for row in so_list:
		if not row.delivery_return:
			frappe.db.sql("""update `tabSales Order` set golden_status = 'Finished' where `name` = %s""", row.sales_order)

@frappe.whitelist()
def get_packing_barcode(barc, notin):
	si_list = []
	bcode = barc[0:12]
	if notin != "-":
		check_bcode = frappe.db.sql("select count(*) from `tabDelivery Order Barcode` where docstatus = '1' and delivery_keeptrack is null and barcode_1 = %s and barcode_1 not in ("+notin+")", bcode)[0][0]
	else:
		check_bcode = frappe.db.sql("select count(*) from `tabDelivery Order Barcode` where docstatus = '1' and delivery_keeptrack is null and barcode_1 = %s", bcode)[0][0]
	if flt(check_bcode) == 1:
		list = frappe.db.get_value("Delivery Order Barcode", {"barcode_1": bcode}, ["barcode_1", "box", "parent", "packing"], as_dict=1)
		a = frappe.db.get_value("Delivery Order Detail", {"packing": list.packing}, "do_no")
		si_list.append(frappe._dict({
			'barcode': barc,
			'barcode_1': list.barcode_1,
			'box': list.box,
			'delivery_order': list.parent,
			'do_no': a
		}))
	return si_list

@frappe.whitelist()
def get_packing_from_barcode(bcode, do):
	si_list = []
	bcode = bcode[0:12]
	a = frappe.db.sql("select customer, customer_name, total_box, expedition, sales_order, `name`, packing from `tabDelivery Order Detail` where `name` in ("+do+")", as_dict=1)
	for b in a:
		si_list.append(frappe._dict({
			'delivery_order': b.name,
			'packing': b.packing,
			'customer': b.customer,
			'customer_name': b.customer_name,
			'box': b.total_box,
			'sales_order': b.sales_order,
			'expedition': b.expedition
		}))
	return si_list
