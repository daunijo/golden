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
		self.check_overlapping_value()
		self.check_duplicate_doc()

	def on_submit(self):
		self.update_other_doc()

	def on_update_after_submit(self):
		self.update_other_doc()

	def check_overlapping_value(self):
		if self.details:
			start = 0
			end = 0
			for row in self.details:
				if row.from_range > row.to_range:
					frappe.throw(_("From Range is bigger than To Range in row {0}").format(row.idx))
				if row.idx >= 2:
					if start <= row.from_range <= end:
						frappe.throw(_("From Range in row {0} is overlap").format(row.idx))
				start = row.from_range
				end = row.to_range
		if self.collects:
			start = 0
			end = 0
			for row in self.collects:
				if row.from_day > row.to_day:
					frappe.throw(_("From Day is bigger than To Day in row {0}").format(row.idx))
				if row.idx >= 2:
					if start <= row.from_day <= end:
						frappe.throw(_("From Day in row {0} is overlap").format(row.idx))
				start = row.from_day
				end = row.to_day

	def check_duplicate_doc(self):
		if self.sales:
			doc = frappe.db.sql("""select count(*) from `tabCommission Percentage` where docstatus= '1' and commission_type = %s and disabled = %s and sales = %s""", (self.commission_type, self.disabled, self.sales))[0][0]
			if flt(doc) >= 1:
				cp = frappe.db.sql("""select `name` from `tabCommission Percentage` where docstatus= '1' and commission_type = %s and disabled = %s and sales = %s order by `name` desc limit 1""", (self.commission_type, self.disabled, self.sales))[0][0]
				frappe.throw(_("Document is duplicated with Commission Percentage {0}").format(cp))
		else:
			doc = frappe.db.sql("""select count(*) from `tabCommission Percentage` where docstatus= '1' and commission_type = %s and disabled = %s and sales is null""", (self.commission_type, self.disabled))[0][0]
			if flt(doc) >= 1:
				cp = frappe.db.sql("""select `name` from `tabCommission Percentage` where docstatus= '1' and commission_type = %s and disabled = %s and sales is null order by `name` desc limit 1""", (self.commission_type, self.disabled))[0][0]
				frappe.throw(_("Document is duplicated with Commission Percentage {0}").format(cp))

	def update_other_doc(self):
		if not self.sales:
			frappe.db.sql("""update `tabCommission Percentage` set disabled = '1' where docstatus = '1' and `name` != %s and sales is null and commission_type = %s""", (self.name, self.commission_type))
		else:
			frappe.db.sql("""update `tabCommission Percentage` set disabled = '1' where docstatus = '1' and `name` != %s and sales = %s and commission_type = %s""", (self.name, self.sales, self.commission_type))
