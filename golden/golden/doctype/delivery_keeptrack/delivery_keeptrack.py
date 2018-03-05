# -*- coding: utf-8 -*-
# Copyright (c) 2018, RSS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import cstr, flt
from frappe import msgprint, _

class DeliveryKeeptrack(Document):
	def validate(self):
		self.update_sales_order()
		self.check_packing()

	def on_submit(self):
		for row in self.details:
			frappe.db.sql("""update `tabSales Order` set golden_status = 'Finished' where `name` = %s""", row.sales_order)

	def on_cancel(self):
		for row in self.details:
			frappe.db.sql("""update `tabSales Order` set golden_status = 'Wait for Delivery and Bill', delivery_keeptrack = null where `name` = %s""", row.sales_order)

	def on_trash(self):
		frappe.db.sql("""update `tabSales Order` set golden_status = previous_golden_status, previous_golden_status = null, delivery_keeptrack = null where delivery_keeptrack = %s""", self.name)

	def update_sales_order(self):
		if self.is_new():
			for row in self.details:
				so_status = frappe.db.sql("""select golden_status from `tabSales Order` where `name` = %s""", row.sales_order)[0][0]
				frappe.db.sql("""update `tabSales Order` set golden_status = 'Delivering', previous_golden_status = %s, delivery_keeptrack = %s where `name` = %s""", (so_status, self.name, row.sales_order))
		else:
			frappe.db.sql("""update `tabSales Order` set golden_status = previous_golden_status, previous_golden_status = null, delivery_keeptrack = null where delivery_keeptrack = %s""", self.name)
			for row in self.details:
				so_status = frappe.db.sql("""select golden_status from `tabSales Order` where `name` = %s""", row.sales_order)[0][0]
				frappe.db.sql("""update `tabSales Order` set golden_status = 'Delivering', previous_golden_status = %s, delivery_keeptrack = %s where `name` = %s""", (so_status, self.name, row.sales_order))

	def check_packing(self):
		if self.is_new():
			for row in self.details:
				check_pl = frappe.db.sql("""select count(*) from `tabDelivery Keeptrack Detail` where packing = %s and docstatus != '2'""", row.packing)[0][0]
				if flt(check_pl) != 0:
					frappe.throw(_("Packing List {0} already used in other Delivery Keeptrack").format(row.packing))
		else:
			for row in self.details:
				check_pl = frappe.db.sql("""select count(*) from `tabDelivery Keeptrack Detail` where parent != %s and packing = %s and docstatus != '2'""", (self.name, row.packing))[0][0]
				if flt(check_pl) != 0:
					frappe.throw(_("Packing List {0} already used in other Delivery Keeptrack").format(row.packing))
