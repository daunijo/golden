# -*- coding: utf-8 -*-
# Copyright (c) 2018, RSS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import nowdate, cstr, flt, now, getdate, add_months
from frappe import msgprint, _
from frappe.model.mapper import get_mapped_doc
from datetime import datetime

class SalesTarget(Document):
	pass

@frappe.whitelist()
def get_sales_invoice(sales, start_date, end_date, target1, target2):
	if flt(target2) >= 1:
		target = target2
	else:
		target = target1
	si_list = []
	sales_invoice = frappe.db.sql("""select * from `tabSales Invoice` where docstatus = '1' and rss_sales_person = %s and posting_date between %s and %s""", (sales, start_date, end_date), as_dict=True)
	for si in sales_invoice:
		count_payment = frappe.db.sql("""select count(*) from `tabPayment Entry Reference` a inner join `tabPayment Entry` b on a.parent = b.`name` where b.docstatus = '1' and a.reference_name = %s order by posting_date desc limit 1""", si.name)[0][0]
		contribution = (flt(si.net_total) / flt(target)) * 100
		if flt(count_payment) != 0:
			payment_date = frappe.db.sql("""select datediff(posting_date, %s) from `tabPayment Entry Reference` a inner join `tabPayment Entry` b on a.parent = b.`name` where b.docstatus = '1' and a.reference_name = %s order by posting_date desc limit 1""", (si.posting_date, si.name))[0][0]
			payment_amount = frappe.db.sql("""select sum(allocated_amount) from `tabPayment Entry Reference` a inner join `tabPayment Entry` b on a.parent = b.`name` where b.docstatus = '1' and a.reference_name = %s""", si.name)[0][0]
			# diff_day = payment_date - si.posting_date
			diff_day = payment_date
		else:
			payment_date = ""
			payment_amount = 0
			diff_day = "-"
		si_list.append(frappe._dict({
	        'customer': si.customer,
	        'customer_name': si.customer_name,
	        'sales_invoice_date': si.posting_date,
			'sales_invoice': si.name,
			'grand_total': si.net_total,
			'payment_date': payment_date,
			'payment_amount': payment_amount,
			'difference_day': diff_day,
			'contribution': contribution
	    }))
	return si_list
