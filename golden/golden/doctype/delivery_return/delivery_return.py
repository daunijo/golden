# -*- coding: utf-8 -*-
# Copyright (c) 2018, RSS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import msgprint, _
from frappe.model.mapper import get_mapped_doc

class DeliveryReturn(Document):
	def validate(self):
		self.update_transaction_date()
		self.check_delivery_keeptrack()

	def update_transaction_date(self):
		frappe.db.set(self, 'transaction_date', self.posting_date)

	def check_delivery_keeptrack(self):
		for row in self.details:
			dk = frappe.db.get_value("Delivery Keeptrack", row.delivery_keeptrack, "delivery_return")
			if dk:
				frappe.throw(_("This Delivery Keeptrack already has a Delivery Return"))

	def on_submit(self):
		self.update_delivery_order()
		self.update_delivery_keeptrack()
		self.update_status_so()

	def update_delivery_order(self):
		for row in self.details:
			if row.delivery_order:
				frappe.db.sql("""update `tabDelivery Order Detail` set delivery_return = %s where `name` = %s""", (self.name, row.delivery_order))

	def update_delivery_keeptrack(self):
		for row in self.details:
			frappe.db.sql("""update `tabDelivery Keeptrack Detail` set delivery_return = %s where `name` = %s""", (self.name, row.delivery_keeptrack_detail))
			frappe.db.sql("""update `tabDelivery Keeptrack` set delivery_return = %s where `name` = %s""", (self.name, row.delivery_keeptrack))

	def update_status_so(self):
		for row in self.details:
			if row.sales_order:
				frappe.db.sql("""update `tabSales Order` set previous_golden_status = golden_status, golden_status = 'Delivery Return' where `name` = %s""", row.sales_order)

	def on_cancel(self):
		self.cancel_delivery_order()
		self.cancel_status_so()
		self.cancel_delivery_keeptrack()

	def cancel_delivery_order(self):
		for row in self.details:
			frappe.db.sql("""update `tabDelivery Order Detail` set delivery_return = null where `name` = %s""", row.delivery_order)

	def cancel_status_so(self):
		for row in self.details:
			if row.sales_order:
				frappe.db.sql("""update `tabSales Order` set golden_status = previous_golden_status, previous_golden_status = 'Wait for Delivery and Bill' where `name` = %s""", row.sales_order)

	def cancel_delivery_keeptrack(self):
		for row in self.details:
			frappe.db.sql("""update `tabDelivery Keeptrack Detail` set delivery_return = null where `name` = %s""", row.delivery_keeptrack_detail)
			frappe.db.sql("""update `tabDelivery Keeptrack` set delivery_return = null where `name` = %s""", row.delivery_keeptrack)
