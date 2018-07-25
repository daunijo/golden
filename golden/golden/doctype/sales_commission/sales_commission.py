# -*- coding: utf-8 -*-
# Copyright (c) 2018, RSS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt
from frappe import msgprint, _

class SalesCommission(Document):
	pass

@frappe.whitelist()
def get_invoices(sales, sales_target, start_date, end_date):
	si_list = []
	std = frappe.db.sql("""select * from `tabSales Target Detail` where docstatus = '1' and parent = %s order by sales_invoice_date asc""", (sales_target), as_dict=True)
	for si in std:
		si_list.append(frappe._dict({
	        'sales_invoice_date': si.sales_invoice_date,
	        'sales_invoice': si.sales_invoice,
	        'amount': si.invoice_amount,
	    }))
	return si_list

@frappe.whitelist()
def get_returns(sales, sales_target, start_date, end_date):
	si_list = []
	std = frappe.db.sql("""select distinct(sr.`name`), sr.posting_date from `tabSales Return` sr inner join `tabSales Return Detail` srd on srd.parent = sr.`name` where sr.docstatus = '1' and srd.sales_person = %s and sr.posting_date >= %s and sr.posting_date <= %s""", (sales, start_date, end_date), as_dict=True)
	for si in std:
		amt = frappe.db.sql("""select sum(si_rate * qty) as amount from `tabSales Return Detail` where parent = %s and sales_person = %s""", (si.name, sales))[0][0]
		si_list.append(frappe._dict({
	        'return_date': si.posting_date,
	        'sales_return': si.name,
			'amount': flt(amt)
	    }))
	return si_list
