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

	def update_transaction_date(self):
		frappe.db.set(self, 'transaction_date', self.posting_date)

	def on_submit(self):
		self.update_delivery_order()

	def update_delivery_order(self):
		for row in self.details:
			if row.delivery_order:
				frappe.db.sql("""update `tabDelivery Order Detail` set delivery_return = %s where `name` = %s""", (self.name, row.delivery_order))

	def on_cancel(self):
		self.cancel_delivery_order()

	def cancel_delivery_order(self):
		for row in self.details:
			frappe.db.sql("""update `tabDelivery Order Detail` set delivery_return = null where `name` = %s""", row.delivery_order)
