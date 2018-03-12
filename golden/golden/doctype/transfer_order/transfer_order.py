# -*- coding: utf-8 -*-
# Copyright (c) 2018, RSS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import msgprint, _

class TransferOrder(Document):
	def validate(self):
		pass
#		self.check_qty()

	def on_submit(self):
		frappe.db.set(self, 'status', 'Submitted')
		self.update_bin()
		self.check_picker()

	def on_cancel(self):
		frappe.db.set(self, 'status', 'Cancelled')
		self.cancel_bin()

	def update_bin(self):
		for row in self.items:
			if row.bin:
				bins = frappe.get_doc("Bin", row.bin)
				bins.ito = self.name
				bins.ito_qty = row.qty
				bins.save()

	def cancel_bin(self):
		for row in self.items:
			if row.bin:
				bins = frappe.get_doc("Bin", row.bin)
				bins.ito = None
				bins.ito_qty = 0
				bins.save()

	def check_qty(self):
		for row in self.items:
			if row.qty <= 0:
				frappe.throw(_("Qty is mandatory"))

	def check_picker(self):
		if not self.picker:
			frappe.throw(_("Picker Name is mandatory"))
