# -*- coding: utf-8 -*-
# Copyright (c) 2018, RSS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import msgprint, _
from frappe.utils import flt, comma_or, nowdate, flt, cstr

class PaymentEntryReceive(Document):
	def on_submit(self):
		self.check_reference()
		self.insert_payment_entry()
		self.add_allocated_amount()

	def on_cancel(self):
		self.delete_payment_entry()
		self.rem_allocated_amount()

	def check_reference(self):
		if self.need_reference:
			if self.reference_no == None or self.reference_date == None:
				frappe.throw(_("Check/Reference No and Date is mandatory"))

	def insert_payment_entry(self):
		pe = frappe.get_doc({
			"doctype": "Payment Entry",
			"payment_type": self.payment_type,
			"posting_date": self.posting_date,
			"party_type": self.party_type,
			"party": self.party,
			"party_name": self.party_name,
			"party_balance": self.party_balance,
			"paid_from": self.paid_from,
			"paid_from_account_currency": self.paid_from_account_currency,
			"paid_from_account_balance": self.paid_from_account_balance,
			"paid_to": self.paid_to,
			"paid_to_account_currency": self.paid_to_account_currency,
			"paid_to_account_balance": self.paid_to_account_balance,
			"paid_amount": self.paid_amount,
			"received_amount": self.received_amount,
			"target_exchange_rate": self.target_exchange_rate,
			"base_received_amount": self.base_received_amount,
			"allocate_payment_amount": self.allocate_payment_amount,
			"references": self.references,
			"total_allocated_amount": self.total_allocated_amount,
			"unallocated_amount": self.unallocated_amount,
			"difference_amount": self.difference_amount,
			"deductions": self.deductions,
			"reference_no": self.reference_no,
			"reference_date": self.reference_date,
			"payment_entry_receive": self.name
		})
		pe.save()
		pe.submit()

	def add_allocated_amount(self):
		for row in self.deductions:
			if row.journal_entry_detail:
				allocated = frappe.db.sql("""select allocated_amount from `tabJournal Entry Account` where `name` = %s""", row.journal_entry_detail)[0][0]
				update_allocated = flt(allocated) + flt(row.amount)
				frappe.db.sql("""update `tabJournal Entry Account` set allocated_amount = %s where `name` = %s""", (update_allocated, row.journal_entry_detail))

	def delete_payment_entry(self):
		pe = frappe.get_doc("Payment Entry", {"payment_entry_receive": self.name})
		pe.cancel(ignore_permissions=True)
		pe.delete(ignore_permissions=True)

	def rem_allocated_amount(self):
		for row in self.deductions:
			if row.journal_entry_detail:
				allocated = frappe.db.sql("""select allocated_amount from `tabJournal Entry Account` where `name` = %s""", row.journal_entry_detail)[0][0]
				update_allocated = flt(allocated) - flt(row.amount)
				frappe.db.sql("""update `tabJournal Entry Account` set allocated_amount = %s where `name` = %s""", (update_allocated, row.journal_entry_detail))

@frappe.whitelist()
def get_deductions(customer):
	si_list = []
	journal_entry = frappe.db.sql("""select `name`, account, cost_center, credit_in_account_currency, allocated_amount from `tabJournal Entry Account` where docstatus = '1' and customer_code = %s and credit_in_account_currency > allocated_amount""", (customer), as_dict=True)
	for je in journal_entry:
		nominal = flt(je.credit_in_account_currency) - flt(je.allocated_amount)
		si_list.append(frappe._dict({
	        'account': je.account,
	        'cost_center': je.cost_center,
	        'amount': nominal,
			'journal_entry_detail': je.name
	    }))
	return si_list
