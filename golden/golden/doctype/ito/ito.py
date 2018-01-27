# -*- coding: utf-8 -*-
# Copyright (c) 2018, RSS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import msgprint, _

class ITO(Document):
	def on_submit(self):
		frappe.db.set(self, 'status', 'Submitted')
		self.update_bin()

	def on_cancel(self):
		frappe.db.set(self, 'status', 'Cancelled')

	def update_bin(self):
		for row in self.items:
			if row.bin:
                bins = frappe.get_doc("Bin", row.bin)
                bins.ito = self.name
				bins.ito_qty = row.qty
                bins.save()
