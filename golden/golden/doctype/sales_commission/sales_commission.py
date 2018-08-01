# -*- coding: utf-8 -*-
# Copyright (c) 2018, RSS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt
from frappe import msgprint, _

class SalesCommission(Document):
	def validate(self):
		self.check_sales_target()

	def check_sales_target(self):
		st = frappe.db.sql("""select count(*) from `tabSales Target` where `name` = %s and sales_commission is not null""", self.name)[0][0]
		if flt(st) == 1:
			frappe.throw(_("Sales Target <b>{0}</b> already used in other Sales Commission").format(self.sales_target))

	def on_submit(self):
		self.check_sales_target()
		self.update_sales_target()

	def update_sales_target(self):
		frappe.db.sql("""update `tabSales Target` set sales_commission = %s where `name` = %s""", (self.name, self.sales_target))

	def on_cancel(self):
		frappe.db.sql("""update `tabSales Target` set sales_commission = null where `name` = %s""",  self.sales_target)

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

@frappe.whitelist()
def get_payments(sales, sales_target, start_date, end_date):
	si_list = []
	std = frappe.db.sql("""select b.`name` as payment_entry, b.posting_date as payment_date, a.allocated_amount, c.sales_invoice, c.sales_invoice_date, datediff(b.posting_date,c.sales_invoice_date) as range_day from `tabPayment Entry Receive Reference` a inner join `tabPayment Entry Receive` b on b.`name` = a.parent inner join `tabSales Target Detail` c on c.sales_invoice = a.reference_name where b.docstatus = '1' and c.parent = %s""", (sales_target), as_dict=True)
	for si in std:
		check1 = frappe.db.sql("""select count(*) from `tabCommission Percentage` where docstatus = '1' and commission_type = 'COLLECT' and sales = %s and disabled = '0'""", sales)[0][0]
		if flt(check1) == 1:
			check2 = frappe.db.sql("""select count(*) from `tabCommission Percentage` where docstatus = '1' and commission_type = 'COLLECT' and sales = %s and disabled = '0'""", sales)[0][0]
			if flt(check2) == 1:
				cp = frappe.db.sql("""select `name` from `tabCommission Percentage` where docstatus = '1' and commission_type = 'COLLECT' and sales = %s and disabled = '0'""", sales)[0][0]
				cpd = frappe.db.sql("""select percentage from `tabCommission Percentage Collect` where parent = %s and from_day <= %s and to_day >= %s""", (cp, si.range_day, si.range_day))[0][0]
				hasil = cpd
			else:
				hasil = 0
		else:
			check2 = frappe.db.sql("""select count(*) from `tabCommission Percentage` where docstatus = '1' and commission_type = 'COLLECT' and sales is null and disabled = '0'""")[0][0]
			if flt(check2) == 1:
				cp = frappe.db.sql("""select `name` from `tabCommission Percentage` where docstatus = '1' and commission_type = 'COLLECT' and sales is null and disabled = '0'""")[0][0]
				cpd = frappe.db.sql("""select percentage from `tabCommission Percentage Collect` where parent = %s and from_day <= %s and to_day >= %s""", (cp, si.range_day, si.range_day))[0][0]
				hasil = cpd
			else:
				hasil = 0
		komisi = (flt(hasil) / 100) * flt(si.allocated_amount)
		si_list.append(frappe._dict({
	        'payment_entry': si.payment_entry,
	        'payment_date': si.payment_date,
			'sales_invoice': si.sales_invoice,
	        'payment_amount': si.allocated_amount,
			'invoice_date': si.sales_invoice_date,
			'date_diff': si.range_day,
			'payment_commission': komisi
	    }))
	return si_list

@frappe.whitelist()
def calculate_invoice(sales, percentage, total_invoice):
	percent_round = round(flt(percentage),0)
	check1 = frappe.db.sql("""select count(*) from `tabCommission Percentage` where docstatus = '1' and commission_type = 'SELL' and sales = %s and disabled = '0'""", sales)[0][0]
	if flt(check1) == 1:
		check2 = frappe.db.sql("""select count(*) from `tabCommission Percentage` where docstatus = '1' and commission_type = 'SELL' and sales = %s and disabled = '0'""", sales)[0][0]
		if flt(check2) == 1:
			cp = frappe.db.sql("""select `name` from `tabCommission Percentage` where docstatus = '1' and commission_type = 'SELL' and sales = %s and disabled = '0'""", sales)[0][0]
			cpd = frappe.db.sql("""select percentage from `tabCommission Percentage Detail` where parent = %s and from_range <= %s and to_range >= %s""", (cp, percent_round, percent_round))[0][0]
			hasil = cpd
		else:
			hasil = 0
	else:
		check2 = frappe.db.sql("""select count(*) from `tabCommission Percentage` where docstatus = '1' and commission_type = 'SELL' and sales is null and disabled = '0'""")[0][0]
		if flt(check2) == 1:
			cp = frappe.db.sql("""select `name` from `tabCommission Percentage` where docstatus = '1' and commission_type = 'SELL' and sales is null and disabled = '0'""")[0][0]
			cpd = frappe.db.sql("""select percentage from `tabCommission Percentage Detail` where parent = %s and from_range <= %s and to_range >= %s""", (cp, percent_round, percent_round))[0][0]
			hasil = cpd
		else:
			hasil = 0
	komisi = (flt(hasil) / 100) * flt(total_invoice)
	inv_commission = {
		'invoice_commission': komisi,
	}
	return inv_commission

@frappe.whitelist()
def calculate_return(sales, percentage, total_return):
	percent_round = round(flt(percentage),0)
	check1 = frappe.db.sql("""select count(*) from `tabCommission Percentage` where docstatus = '1' and commission_type = 'RETURN' and sales = %s and disabled = '0'""", sales)[0][0]
	if flt(check1) == 1:
		check2 = frappe.db.sql("""select count(*) from `tabCommission Percentage` where docstatus = '1' and commission_type = 'RETURN' and sales = %s and disabled = '0'""", sales)[0][0]
		if flt(check2) == 1:
			cp = frappe.db.sql("""select `name` from `tabCommission Percentage` where docstatus = '1' and commission_type = 'RETURN' and sales = %s and disabled = '0'""", sales)[0][0]
			cpd = frappe.db.sql("""select percentage from `tabCommission Percentage Detail` where parent = %s and from_range <= %s and to_range >= %s""", (cp, percent_round, percent_round))[0][0]
			hasil = cpd
		else:
			hasil = 0
	else:
		check2 = frappe.db.sql("""select count(*) from `tabCommission Percentage` where docstatus = '1' and commission_type = 'RETURN' and sales is null and disabled = '0'""")[0][0]
		if flt(check2) == 1:
			cp = frappe.db.sql("""select `name` from `tabCommission Percentage` where docstatus = '1' and commission_type = 'RETURN' and sales is null and disabled = '0'""")[0][0]
			cpd = frappe.db.sql("""select percentage from `tabCommission Percentage Detail` where parent = %s and from_range <= %s and to_range >= %s""", (cp, percent_round, percent_round))[0][0]
			hasil = cpd
		else:
			hasil = 0
	komisi = (flt(hasil) / 100) * flt(total_return)
	inv_commission = {
		'return_commission': komisi,
	}
	return inv_commission
