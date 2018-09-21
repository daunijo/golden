# -*- coding: utf-8 -*-
# Copyright (c) 2018, RSS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import cstr, flt
from frappe import msgprint, _

class SummaryGenerator(Document):
	def validate(self):
		self.check_is_invoice_summary()
		self.insert_sales()

	def check_is_invoice_summary(self):
		for row in self.details:
			if row.reference_doctype == "Sales Invoice":
				check_si = frappe.db.sql("""select invoice_keeptrack from `tabSales Invoice` where docstatus = '1' and `name` = %s""", row.reference_name)[0][0]
				if check_si:
					frappe.throw(_("Invoice {0} already used in Invoice Keeptrack").format(row.reference_name))
			elif row.reference_doctype == "Sales Return":
				check_si = frappe.db.sql("""select sales_invoice_summary from `tabSales Return` where docstatus = '1' and `name` = %s""", row.reference_name)[0][0]
				if check_si:
					frappe.throw(_("Sales Return {0} already used in other Sales Invoice Summary").format(row.reference_name))

	def insert_sales(self):
		for row in self.customers:
			sales = []
			for det in self.details:
				if det.customer == row.customer and det.reference_doctype == "Sales Invoice":
					if det.sales_name != "" and det.sales_name not in sales:
						sales.append(det.sales_name)
				sales_list = ", ".join(sales)
				row.sales = sales_list

	def on_submit(self):
		for row in self.customers:
			summary = frappe.get_doc({
				"doctype": "Sales Invoice Summary",
				"customer": row.customer,
				"customer_name": row.customer_name,
				"start_date": self.start_date,
				"end_date": self.end_date,
				"posting_date": self.posting_date,
				"posting_time": self.posting_time,
				"set_posting_time": self.set_posting_time,
				"company": self.company,
				"status": "Draft",
				"summary_generator": self.name,
				"sales_name": row.sales
			})
			summary.save()
			si_summary = frappe.get_doc("Sales Invoice Summary", summary.name)
			total_invoice = 0
			for det in self.details:
				if det.customer == row.customer:
					if det.reference_doctype == "Sales Invoice":
						total_invoice = flt(total_invoice) + flt(det.amount)
					else:
						total_invoice = flt(total_invoice) - flt(det.amount)
					si_summary.append("invoices", {
						"customer": det.customer,
						"customer_name": det.customer_name,
						"reference_doctype": det.reference_doctype,
						"reference_name": det.reference_name,
						"invoice_date": det.invoice_date,
						"amount": det.amount,
						"due_date": det.due_date,
						"sales_name": det.sales_name
					})
					si_summary.save()
			si_summary.total_invoice = total_invoice
			si_summary.save()
			si_summary.submit()
			frappe.db.sql("""update `tabSummary Generator Customer` set si_summary = %s where `name` = %s""", (summary.name, row.name))

	def on_cancel(self):
		for row in self.customers:
			si_summary = frappe.get_doc("Sales Invoice Summary", {"customer": row.customer, "summary_generator": self.name})
			si_summary.cancel()
			si_summary.delete()

@frappe.whitelist()
def get_customers(start, end, territory):
	temp = []
	customer_list = []
	conditions = ""
	conditions += " and si.posting_date >= '%s'" % frappe.db.escape(start)
	conditions += " and si.posting_date <= '%s'" % frappe.db.escape(end)
	if territory != "":
		conditions += " and c.territory = '%s'" % frappe.db.escape(territory)
	invoice_list = frappe.db.sql("""select distinct(si.customer), si.customer_name from `tabSales Invoice` si inner join `tabCustomer` c on c.`name` = si.customer where si.docstatus = '1' and si.`status` != 'Paid' and si.sales_invoice_summary is null %s""" % conditions, as_dict=True)
	for d in invoice_list:
		if d.customer not in temp:
			temp.append(d.customer)
			customer_list.append(frappe._dict({
				'customer': d.customer,
				'customer_name': d.customer_name,
	        }))
	return_list = frappe.db.sql("""select distinct(si.customer), si.customer_name from `tabSales Return` si inner join `tabCustomer` c on c.`name` = si.customer where si.docstatus = '1' and si.sales_invoice_summary is null %s""" % conditions, as_dict=True)
	for e in return_list:
		if e.customer not in temp:
			temp.append(e.customer)
			customer_list.append(frappe._dict({
				'customer': e.customer,
				'customer_name': e.customer_name,
	        }))
	return customer_list

@frappe.whitelist()
def get_details(start, end, territory):
	si_list = []
	conditions = ""
	conditions += " and si.posting_date >= '%s'" % frappe.db.escape(start)
	conditions += " and si.posting_date <= '%s'" % frappe.db.escape(end)
	if territory != "":
		conditions += " and c.territory = '%s'" % frappe.db.escape(territory)
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
	return_list = frappe.db.sql("""select si.`name` as si_name, si.customer, si.customer_name, si.posting_date, si.total_2 from `tabSales Return` si inner join `tabCustomer` c on c.`name` = si.customer where si.docstatus = '1' and si.sales_invoice_summary is null %s""" % conditions, as_dict=True)
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
