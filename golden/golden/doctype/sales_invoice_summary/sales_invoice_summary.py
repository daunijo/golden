# -*- coding: utf-8 -*-
# Copyright (c) 2018, RSS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import nowdate, cstr, flt, now, getdate, add_months
from frappe import msgprint, _
from frappe.model.mapper import get_mapped_doc

class SalesInvoiceSummary(Document):
	def validate(self):
		frappe.db.set(self, 'status', 'Draft')
		self.check_is_invoice_summary()

	def check_is_invoice_summary(self):
		for row in self.invoices:
			check_si = frappe.db.sql("""select invoice_keeptrack from `tabSales Invoice` where docstatus = '1' and `name` = %s""", row.sales_invoice)[0][0]
			if check_si:
				frappe.throw(_("Invoice {0} already used in Invoice Keeptrack").format(row.sales_invoice))

	def on_submit(self):
		frappe.db.set(self, 'status', 'Submitted')
		for row in self.invoices:
			frappe.db.sql("""update `tabSales Invoice` set sales_invoice_summary = %s where `name` = %s""", (self.name, row.sales_invoice))

	def on_cancel(self):
		frappe.db.set(self, 'status', 'Cancelled')
		for row in self.invoices:
			frappe.db.sql("""update `tabSales Invoice` set sales_invoice_summary = null where `name` = %s""", row.sales_invoice)

@frappe.whitelist()
def get_sales_invoice(sales_person):
    si_list = []
    invoice_list = frappe.db.sql("""select * from `tabSales Invoice` where docstatus = '1' and status != 'Paid' and rss_sales_person = %s and sales_invoice_summary is null""", sales_person, as_dict=True)
    for d in invoice_list:
		count_payment = frappe.db.sql("""select count(*) from `tabPayment Entry Reference` where docstatus = '1' and reference_name = %s""", d.name)[0][0]
		si_list.append(frappe._dict({
            'customer': d.customer,
            'customer_name': d.customer_name,
			'si_name': d.name,
			'posting_date': d.posting_date,
			'amount': d.grand_total,
			'due_date': d.due_date,
        }))
    return si_list
