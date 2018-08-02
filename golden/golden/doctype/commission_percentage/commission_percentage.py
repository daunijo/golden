# -*- coding: utf-8 -*-
# Copyright (c) 2018, RSS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt
from frappe import msgprint, _

class CommissionPercentage(Document):
	def validate(self):
		if self.details:
			start = 0
			end = 0
			for row in self.details:
				if flt(start) != 0 and flt(end) != 0:
					if start <= row.from_range <= end:
						frappe.throw(_("From Range in row {0} is overlap").format(row.idx))
				start = row.from_range
				end = row.to_range

	def on_submit(self):
		self.update_other_doc()

	def update_other_doc(self):
		if not self.sales:
			frappe.db.sql("""update `tabCommission Percentage` set disabled = '1' where docstatus = '1' and `name` != %s and sales is null and commission_type = %s""", (self.name, self.commission_type))
		else:
			frappe.db.sql("""update `tabCommission Percentage` set disabled = '1' where docstatus = '1' and `name` != %s and sales = %s and commission_type = %s""", (self.name, self.sales, self.commission_type))

	def on_update_after_submit(self):
		self.update_other_doc()
