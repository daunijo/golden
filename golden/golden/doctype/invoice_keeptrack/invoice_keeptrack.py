# -*- coding: utf-8 -*-
# Copyright (c) 2018, RSS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import nowdate, cstr, flt, now, getdate, add_months
from frappe import msgprint, _
from frappe.model.mapper import get_mapped_doc

class InvoiceKeeptrack(Document):
	def validate(self):
		self.check_invoice_summary()
		self.update_invoice_summary()

	def check_invoice_summary(self):
		temp = []
		for row in self.invoices:
			if row.si_summary not in temp:
				temp.append(row.si_summary)
			else:
				frappe.throw(_("SI Summary {0} is duplicate").format(row.si_summary))

	def update_invoice_summary(self):
		if not self.is_new():
			frappe.db.sql("""update `tabSales Invoice Summary` set invoice_keeptrack = null where invoice_keeptrack = %s""", self.name)
		for row in self.invoices:
			frappe.db.sql("""update `tabSales Invoice Summary` set invoice_keeptrack = %s where `name` = %s""", (self.name, row.si_summary))

	def on_submit(self):
		self.make_payment()
		for row in self.invoices:
			frappe.db.sql("""update `tabSales Invoice Summary` set status = 'Completed' where `name` = %s""", row.si_summary)

	def on_cancel(self):
		for row in self.invoices:
			frappe.db.sql("""update `tabSales Invoice Summary` set status = 'Submitted' where `name` = %s""", row.si_summary)

	def on_trash(self):
		frappe.db.sql("""update `tabSales Invoice Summary` set invoice_keeptrack = null where invoice_keeptrack = %s""", self.name)

	def make_payment(self):
		for row in self.invoices:
			if flt(row.payment_amount) >= 1:
				pe = frappe.get_doc({
					"doctype": "Payment Entry",
					"payment_type": "Receive",
		            "posting_date": self.posting_date,
		            "mode_of_payment": row.mode_of_payment,
					"invoice_keeptrack": self.name,
					"party_type": "Customer",
					"party": row.customer,
					"party_name": row.customer_name,
					"paid_to": "Cash - GT",
					"paid_amount": row.payment_amount,
					"received_amount": row.payment_amount
				})
				pe.insert()

@frappe.whitelist()
def get_sales_invoice(docstatus):
    si_list = []
    invoice_list = frappe.db.sql("""select * from `tabSales Invoice Summary` where docstatus = '1' and status = 'Submitted' and invoice_keeptrack is null""", as_dict=True)
    for d in invoice_list:
		si_list.append(frappe._dict({
            'customer': d.customer,
            'customer_name': d.customer_name,
			'si_summary': d.name,
			'amount': d.total_invoice,
        }))
    return si_list
