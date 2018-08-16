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
			if row.reference_doctype == "Sales Invoice":
				check_si = frappe.db.sql("""select invoice_keeptrack from `tabSales Invoice` where docstatus = '1' and `name` = %s""", row.reference_name)[0][0]
				if check_si:
					frappe.throw(_("Invoice {0} already used in Invoice Keeptrack").format(row.reference_name))
			elif row.reference_doctype == "Sales Return":
				check_si = frappe.db.sql("""select sales_invoice_summary from `tabSales Return` where docstatus = '1' and `name` = %s""", row.reference_name)[0][0]
				if check_si:
					frappe.throw(_("Sales Return {0} already used in other Sales Invoice Summary").format(row.reference_name))

	def on_submit(self):
		frappe.db.set(self, 'status', 'Submitted')
		for row in self.invoices:
			if row.reference_doctype == "Sales Invoice":
				frappe.db.sql("""update `tabSales Invoice` set sales_invoice_summary = %s where `name` = %s""", (self.name, row.reference_name))
			elif row.reference_doctype == "Sales Return":
				frappe.db.sql("""update `tabSales Return` set sales_invoice_summary = %s where `name` = %s""", (self.name, row.reference_name))

	def on_cancel(self):
		frappe.db.set(self, 'status', 'Cancelled')
		for row in self.invoices:
			if row.reference_doctype == "Sales Invoice":
				frappe.db.sql("""update `tabSales Invoice` set sales_invoice_summary = null where `name` = %s""", row.reference_name)
			elif row.reference_doctype == "Sales Return":
				frappe.db.sql("""update `tabSales Return` set sales_invoice_summary = null where `name` = %s""", row.reference_name)

@frappe.whitelist()
def get_sales_invoice(customer, start, end, sales):
	si_list = []
	conditions = ""
	conditions += " and si.customer = '%s'" % frappe.db.escape(customer)
	conditions += " and si.posting_date >= '%s'" % frappe.db.escape(start)
	conditions += " and si.posting_date <= '%s'" % frappe.db.escape(end)
	if sales != "":
		conditions += " and si.rss_sales_person = '%s'" % frappe.db.escape(sales)

	invoice_list = frappe.db.sql("""select si.`name` as si_name, si.customer, si.customer_name, si.posting_date, si.grand_total, si.due_date, si.rss_sales_name from `tabSales Invoice` si inner join `tabCustomer` c on c.`name` = si.customer where si.docstatus = '1' and si.`status` != 'Paid' and si.sales_invoice_summary is null %s""" % conditions, as_dict=True)
	for d in invoice_list:
		# count_payment = frappe.db.sql("""select count(*) from `tabPayment Entry Reference` where docstatus = '1' and reference_name = %s""", d.name)[0][0]
		si_list.append(frappe._dict({
			'customer': d.customer,
			'customer_name': d.customer_name,
			'reference_doctype': "Sales Invoice",
			'reference_name': d.si_name,
			'posting_date': d.posting_date,
			'amount': d.grand_total,
			'due_date': d.due_date,
			'sales_name': d.rss_sales_name
		}))
	conditions2 = ""
	conditions2 += " and si.customer = '%s'" % frappe.db.escape(customer)
	conditions2 += " and si.posting_date >= '%s'" % frappe.db.escape(start)
	conditions2 += " and si.posting_date <= '%s'" % frappe.db.escape(end)
	if sales != "":
		conditions2 += " and si.sales_person = '%s'" % frappe.db.escape(sales)
	return_list = frappe.db.sql("""select si.`name` as si_name, si.customer, si.customer_name, si.posting_date, si.total_2 from `tabSales Return` si inner join `tabCustomer` c on c.`name` = si.customer where si.docstatus = '1' and si.sales_invoice_summary is null %s""" % conditions2, as_dict=True)
	for e in return_list:
		si_list.append(frappe._dict({
			'customer': e.customer,
			'customer_name': e.customer_name,
			'reference_doctype': "Sales Return",
			'reference_name': e.si_name,
			'posting_date': e.posting_date,
			'amount': e.total_2,
			'due_date': "",
			'sales_name': ""
		}))
	return si_list
