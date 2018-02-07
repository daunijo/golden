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
		self.check_is_invoice_summary()

	def check_is_invoice_summary(self):
		for row in self.invoices:
			check_si = frappe.db.sql("""select sales_invoice_summary from `tabSales Invoice` where docstatus = '1' and `name` = %s""", row.sales_invoice)[0][0]
			if check_si:
				frappe.throw(_("Invoice {0} already used in Sales Invoice Summary").format(row.sales_invoice))

	def on_submit(self):
		for row in self.invoices:
			frappe.db.sql("""update `tabSales Invoice` set invoice_keeptrack = %s where `name` = %s""", (self.name, row.sales_invoice))

	def on_cancel(self):
		for row in self.invoices:
			frappe.db.sql("""update `tabSales Invoice` set invoice_keeptrack = null where `name` = %s""", row.sales_invoice)

@frappe.whitelist()
def get_sales_invoice(docstatus):
    si_list = []
    invoice_list = frappe.db.sql("""select * from `tabSales Invoice` where docstatus = '1' and status != 'Paid' and sales_invoice_summary is null and invoice_keeptrack is null""", as_dict=True)
    for d in invoice_list:
		count_payment = frappe.db.sql("""select count(*) from `tabPayment Entry Reference` where docstatus = '1' and reference_name = %s""", d.name)[0][0]
		if flt(count_payment) != 0:
			payment_date = frappe.db.sql("""select b.posting_date from `tabPayment Entry Reference` a inner join `tabPayment Entry` b on a.parent = b.name where a.reference_name = %s order by b.posting_date desc limit 1""", d.name)[0][0]
			payment_amount = frappe.db.sql("""select sum(allocated_amount) from `tabPayment Entry Reference` where docstatus = '1' and reference_name = %s""", d.name)[0][0]
		else:
			payment_date = ''
			payment_amount = 0

		si_list.append(frappe._dict({
            'customer': d.customer,
            'customer_name': d.customer_name,
			'si_name': d.name,
			'posting_date': d.posting_date,
			'amount': d.grand_total,
			'due_date': d.due_date,
			'payment_date': payment_date,
			'payment_amount': payment_amount,
			'outstanding_amount': d.outstanding_amount
        }))
    return si_list
