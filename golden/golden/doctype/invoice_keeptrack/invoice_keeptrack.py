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
		pass
		# self.check_invoice_summary()
		# self.update_invoice_summary()

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
		# self.make_payment()
		self.check_related_document()
		self.update_related_document()
		self.insert_customer_list()

	def check_related_document(self):
		for row in self.invoices:
			if row.si_summary:
				si_summary = frappe.db.get_value("Sales Invoice Summary", row.si_summary, "invoice_keeptrack")
				if si_summary:
					frappe.throw(_("Sales Invoice Summary {0} has been used in another Invoice KeepTrack").format(row.si_summary))
			if row.reference_doctype == "Sales Invoice":
				sinv = frappe.db.get_value("Sales Invoice", row.invoice, "invoice_keeptrack")
				if sinv:
					frappe.throw(_("Sales Invoice {0} has been used in another Invoice KeepTrack").format(row.invoice))
			elif row.reference_doctype == "Sales Return":
				sret = frappe.db.get_value("Sales Return", row.invoice, "invoice_keeptrack")
				if sret:
					frappe.throw(_("Sales Return {0} has been used in another Invoice KeepTrack").format(row.invoice))

	def update_related_document(self):
		for row in self.invoices:
			if row.si_summary:
				frappe.db.sql("""update `tabSales Invoice Summary` set status = 'Completed', invoice_keeptrack = %s where `name` = %s""", (self.name, row.si_summary))
			if row.reference_doctype == "Sales Invoice":
				frappe.db.sql("""update `tabSales Invoice` set invoice_keeptrack = %s where `name` = %s""", (self.name, row.invoice))
			elif row.reference_doctype == "Sales Return":
				frappe.db.sql("""update `tabSales Return` set invoice_keeptrack = %s where `name` = %s""", (self.name, row.invoice))

	def insert_customer_list(self):
		cust = []
		for row in self.invoices:
			if row.customer not in cust:
				cust.append(row.customer)
				plus = frappe.db.sql("""select sum(amount) from `tabInvoice Keeptrack Detail` where parent = %s and reference_doctype = 'Sales Invoice' and customer = %s""", (self.name, row.customer))[0][0]
				minus = frappe.db.sql("""select sum(amount) from `tabInvoice Keeptrack Detail` where parent = %s and reference_doctype = 'Sales Return' and customer = %s""", (self.name, row.customer))[0][0]
				value = flt(plus) - flt(minus)
				self.append("customer_list", {
					'customer': row.customer,
					'customer_name': row.customer_name,
					'total_amount': value
				}).save()

	def on_cancel(self):
		self.check_payment()
		# self.delete_payment()
		for row in self.invoices:
			if row.si_summary:
				frappe.db.sql("""update `tabSales Invoice Summary` set status = 'Submitted', invoice_keeptrack = null where `name` = %s""", row.si_summary)
			if row.reference_doctype == "Sales Invoice":
				frappe.db.sql("""update `tabSales Invoice` set invoice_keeptrack = null where `name` = %s""", row.invoice)
			elif row.reference_doctype == "Sales Return":
				frappe.db.sql("""update `tabSales Return` set invoice_keeptrack = null where `name` = %s""", row.invoice)

	# def on_trash(self):
	# 	frappe.db.sql("""update `tabSales Invoice Summary` set invoice_keeptrack = null where invoice_keeptrack = %s""", self.name)

	def make_payment(self):
		for row in self.invoices:
			if flt(row.payment_amount) >= 1:
				account = frappe.db.sql("""select default_cash_account from `tabCompany` where `name` = %s""", self.company)[0][0]
				pe = frappe.get_doc({
					"doctype": "Payment Entry Receive",
					"payment_type": "Receive",
		            "posting_date": self.posting_date,
		            "mode_of_payment": row.mode_of_payment,
					"invoice_keeptrack": self.name,
					"party_type": "Customer",
					"party": row.customer,
					"party_name": row.customer_name,
					"paid_to": account,
					"paid_amount": row.payment_amount,
					"received_amount": row.payment_amount
				})
				pe.insert()

	def check_payment(self):
		count = frappe.db.sql("""select count(*) from `tabPayment Entry Receive` where invoice_keeptrack = %s and docstatus = '1'""", self.name)[0][0]
		if flt(count) >= 1:
			frappe.throw(_("Payment Entry Receive has been submitted"))

	def delete_payment(self):
		pe = frappe.db.sql("""select `name` from `tabPayment Entry Receive` where invoice_keeptrack = %s""", self.name, as_dict=1)
		for row in pe:
			payment_entry = frappe.get_doc("Payment Entry Receive", row.name)
			payment_entry.delete()

@frappe.whitelist()
def get_sales_invoice(docstatus):
	si_list = []
	reff_name = []
	summary = frappe.db.sql("""select * from `tabSales Invoice Summary` where docstatus = '1' and status = 'Submitted' and invoice_keeptrack is null""", as_dict=True)
	for d in summary:
		summary_detail = frappe.db.sql("""select * from `tabSales Invoice Summary Detail` where parent = %s order by idx asc""", d.name, as_dict=1)
		for sd in summary_detail:
			if sd.reference_doctype == "Sales Invoice":
				si_status = frappe.db.get_value(sd.reference_doctype, sd.reference_name, "status")
				if si_status == "Paid":
					action = "Stop"
				else:
					action = "Start"
				count_pe = frappe.db.sql("""select count(*) from `tabPayment Entry Reference` a inner join `tabPayment Entry` b on a.parent = b.`name` where b.docstatus = '1' and a.reference_name =  %s""", sd.reference_name)[0][0]
				if flt(count_pe) != 0:
					pe_date = frappe.db.sql("""select b.posting_date from `tabPayment Entry Reference` a inner join `tabPayment Entry` b on a.parent = b.`name` where b.docstatus = '1' and a.reference_name = %s order by b.posting_date desc limit 1""", sd.reference_name)
					pe_amount = frappe.db.sql("""select sum(a.total_amount) from `tabPayment Entry Reference` a inner join `tabPayment Entry` b on a.parent = b.`name` where b.docstatus = '1' and a.reference_name = %s""", sd.reference_name)
				else:
					pe_date = ""
					pe_amount = ""
			else:
				action = "Start"
				pe_date = ""
				pe_amount = ""
			if action == "Start":
				reff_name.append(sd.reference_name)
				si_list.append(frappe._dict({
		            'customer': d.customer,
		            'customer_name': d.customer_name,
		            'reference_doctype': sd.reference_doctype,
					'invoice': sd.reference_name,
					'invoice_date': sd.invoice_date,
					'due_date': sd.due_date,
					'payment_date': pe_date,
					'payment_amount': pe_amount,
					'si_summary': d.name,
					'amount': sd.amount,
		        }))
	sales_return = frappe.db.sql("""select * from `tabSales Return` where docstatus = '1' and invoice_keeptrack is null""", as_dict=True)
	for sr in sales_return:
		if sr.name not in reff_name:
			reff_name.append(sr.name)
			si_list.append(frappe._dict({
	            'customer': sr.customer,
	            'customer_name': sr.customer_name,
	            'reference_doctype': "Sales Return",
				'invoice': sr.name,
				'invoice_date': sr.posting_date,
				'due_date': "",
				'payment_date': "",
				'payment_amount': "",
				'si_summary': "",
				'amount': sr.total_2,
	        }))
	sales_invoice = frappe.db.sql("""select * from `tabSales Invoice` where docstatus = '1' and `status` != 'Paid' and invoice_keeptrack is null""", as_dict=True)
	for si in sales_invoice:
		if si.name not in reff_name:
			count_pe = frappe.db.sql("""select count(*) from `tabPayment Entry Reference` a inner join `tabPayment Entry` b on a.parent = b.`name` where b.docstatus = '1' and a.reference_name =  %s""", sd.reference_name)[0][0]
			if flt(count_pe) != 0:
				pe_date = frappe.db.sql("""select b.posting_date from `tabPayment Entry Reference` a inner join `tabPayment Entry` b on a.parent = b.`name` where b.docstatus = '1' and a.reference_name = %s order by b.posting_date desc limit 1""", sd.reference_name)
				pe_amount = frappe.db.sql("""select sum(a.total_amount) from `tabPayment Entry Reference` a inner join `tabPayment Entry` b on a.parent = b.`name` where b.docstatus = '1' and a.reference_name = %s""", sd.reference_name)
			else:
				pe_date = ""
				pe_amount = ""
			reff_name.append(sr.name)
			si_list.append(frappe._dict({
	            'customer': si.customer,
	            'customer_name': si.customer_name,
	            'reference_doctype': "Sales Invoice",
				'invoice': si.name,
				'invoice_date': si.posting_date,
				'due_date': si.due_date,
				'payment_date': pe_date,
				'payment_amount': pe_amount,
				'si_summary': "",
				'amount': si.grand_total,
	        }))
	return si_list
