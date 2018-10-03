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
	sr = frappe.db.sql("""select `name`, posting_date, total_2 from `tabSales Return` where docstatus = '1' and sales_person = %s and posting_date >= %s and posting_date <= %s""", (sales, start_date, end_date), as_dict=True)
	for si in sr:
		si_list.append(frappe._dict({
	        'return_date': si.posting_date,
	        'sales_return': si.name,
			'amount': si.total_2
	    }))
	return si_list

@frappe.whitelist()
def get_payments(sales, sales_target, start_date, end_date):
	si_list = []
	std = frappe.db.sql("""select b.`name` as payment_entry, b.posting_date as payment_date, a.allocated_amount, c.sales_invoice, c.sales_invoice_date, datediff(b.posting_date,c.sales_invoice_date) as range_day from `tabPayment Entry Receive Reference` a inner join `tabPayment Entry Receive` b on b.`name` = a.parent inner join `tabSales Target Detail` c on c.sales_invoice = a.reference_name where b.docstatus = '1' and b.collector = %s""", (sales), as_dict=True)
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
			from_range = frappe.db.sql("""select format(from_range,0) from `tabCommission Percentage Detail` where parent = %s and from_range <= %s and to_range >= %s""", (cp, percent_round, percent_round))[0][0]
			to_range = frappe.db.sql("""select format(to_range,0) from `tabCommission Percentage Detail` where parent = %s and from_range <= %s and to_range >= %s""", (cp, percent_round, percent_round))[0][0]
			hasil = cpd
			sra = from_range+"% - "+to_range+"%"
		else:
			hasil = 0
			sra = "Out of range"
	else:
		check2 = frappe.db.sql("""select count(*) from `tabCommission Percentage` where docstatus = '1' and commission_type = 'SELL' and sales is null and disabled = '0'""")[0][0]
		if flt(check2) == 1:
			cp = frappe.db.sql("""select `name` from `tabCommission Percentage` where docstatus = '1' and commission_type = 'SELL' and sales is null and disabled = '0'""")[0][0]
			cpd = frappe.db.sql("""select percentage from `tabCommission Percentage Detail` where parent = %s and from_range <= %s and to_range >= %s""", (cp, percent_round, percent_round))[0][0]
			from_range = frappe.db.sql("""select format(from_range,0) from `tabCommission Percentage Detail` where parent = %s and from_range <= %s and to_range >= %s""", (cp, percent_round, percent_round))[0][0]
			to_range = frappe.db.sql("""select format(to_range,0) from `tabCommission Percentage Detail` where parent = %s and from_range <= %s and to_range >= %s""", (cp, percent_round, percent_round))[0][0]
			hasil = cpd
			sra = from_range+"% - "+to_range+"%"
		else:
			hasil = 0
			sra = "Out of range"
	komisi = (flt(hasil) / 100) * flt(total_invoice)
	inv_commission = {
		'percentage_invoice_result': hasil,
		'invoice_commission': komisi,
		'sales_range_achievement': sra
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
			from_range = frappe.db.sql("""select format(from_range,0) from `tabCommission Percentage Detail` where parent = %s and from_range <= %s and to_range >= %s""", (cp, percent_round, percent_round))[0][0]
			to_range = frappe.db.sql("""select format(to_range,0) from `tabCommission Percentage Detail` where parent = %s and from_range <= %s and to_range >= %s""", (cp, percent_round, percent_round))[0][0]
			hasil = cpd
			sra = from_range+"% - "+to_range+"%"
		else:
			hasil = 0
			sra = "Out of range"
	else:
		check2 = frappe.db.sql("""select count(*) from `tabCommission Percentage` where docstatus = '1' and commission_type = 'RETURN' and sales is null and disabled = '0'""")[0][0]
		if flt(check2) == 1:
			cp = frappe.db.sql("""select `name` from `tabCommission Percentage` where docstatus = '1' and commission_type = 'RETURN' and sales is null and disabled = '0'""")[0][0]
			cpd = frappe.db.sql("""select percentage from `tabCommission Percentage Detail` where parent = %s and from_range <= %s and to_range >= %s""", (cp, percent_round, percent_round))[0][0]
			from_range = frappe.db.sql("""select format(from_range,0) from `tabCommission Percentage Detail` where parent = %s and from_range <= %s and to_range >= %s""", (cp, percent_round, percent_round))[0][0]
			to_range = frappe.db.sql("""select format(to_range,0) from `tabCommission Percentage Detail` where parent = %s and from_range <= %s and to_range >= %s""", (cp, percent_round, percent_round))[0][0]
			hasil = cpd
			sra = from_range+"% - "+to_range+"%"
		else:
			hasil = 0
			sra = "Out of range"
	komisi = (flt(hasil) / 100) * flt(total_return)
	inv_commission = {
		'percentage_return_result': hasil,
		'return_commission': komisi,
		'return_range_achievement': sra
	}
	return inv_commission

@frappe.whitelist()
def calculate_bonus(sales):
	si_list = []
	check1 = frappe.db.sql("""select count(*) from `tabCommission Percentage` where docstatus = '1' and commission_type = 'COLLECT' and sales = %s and disabled = '0'""", sales)[0][0]
	if flt(check1) == 1:
		check2 = frappe.db.sql("""select count(*) from `tabCommission Percentage` where docstatus = '1' and commission_type = 'COLLECT' and sales = %s and disabled = '0'""", sales)[0][0]
		if flt(check2) == 1:
			cp = frappe.db.sql("""select `name` from `tabCommission Percentage` where docstatus = '1' and commission_type = 'COLLECT' and sales = %s and disabled = '0'""", sales)[0][0]
			cpd = frappe.db.sql("""select * from `tabCommission Percentage Collect` where parent = %s order by idx asc""", cp, as_dict=1)
			last_day = 0
			for has in cpd:
				total_collect = frappe.db.sql("""select sum(a.allocated_amount) from `tabPayment Entry Receive Reference` a inner join `tabPayment Entry Receive` b on b.`name` = a.parent inner join `tabSales Target Detail` c on c.sales_invoice = a.reference_name where b.docstatus = '1' and b.collector = %s and datediff(b.posting_date,c.sales_invoice_date) >= %s and datediff(b.posting_date,c.sales_invoice_date) <= %s""", (sales, has.from_day, has.to_day))[0][0]
				bonus_amount = (flt(has.percentage) / 100) * flt(total_collect)
				last_day = has.to_day
				si_list.append(frappe._dict({
			        'range': "{0} - {1} Days".format(has.from_day, has.to_day),
			        'commission_percengate': has.percentage,
					'total_collect': total_collect,
			        'bonus_amount': bonus_amount
			    }))
			total_collect = frappe.db.sql("""select sum(a.allocated_amount) from `tabPayment Entry Receive Reference` a inner join `tabPayment Entry Receive` b on b.`name` = a.parent inner join `tabSales Target Detail` c on c.sales_invoice = a.reference_name where b.docstatus = '1' and b.collector = %s and datediff(b.posting_date,c.sales_invoice_date) > %s""", (sales, last_day))[0][0]
			si_list.append(frappe._dict({
				'range': "Out of range",
			    'commission_percengate': 0,
				'total_collect': total_collect,
				'bonus_amount': 0
			}))
		else:
			si_list.append(frappe._dict({
		        'range': "Out of range",
		        'commission_percengate': 0,
				'total_collect': 0,
		        'bonus_amount': 0
		    }))
	else:
		check2 = frappe.db.sql("""select count(*) from `tabCommission Percentage` where docstatus = '1' and commission_type = 'COLLECT' and sales is null and disabled = '0'""")[0][0]
		if flt(check2) == 1:
			cp = frappe.db.sql("""select `name` from `tabCommission Percentage` where docstatus = '1' and commission_type = 'COLLECT' and sales is null and disabled = '0'""")[0][0]
			cpd = frappe.db.sql("""select * from `tabCommission Percentage Collect` where parent = %s order by idx asc""", cp, as_dict=1)
			last_day = 0
			for has in cpd:
				total_collect = frappe.db.sql("""select sum(a.allocated_amount) from `tabPayment Entry Receive Reference` a inner join `tabPayment Entry Receive` b on b.`name` = a.parent inner join `tabSales Target Detail` c on c.sales_invoice = a.reference_name where b.docstatus = '1' and b.collector = %s and datediff(b.posting_date,c.sales_invoice_date) >= %s and datediff(b.posting_date,c.sales_invoice_date) <= %s""", (sales, has.from_day, has.to_day))[0][0]
				bonus_amount = (flt(has.percentage) / 100) * flt(total_collect)
				last_day = has.to_day
				si_list.append(frappe._dict({
			        'range': "{0} - {1} Days".format(has.from_day, has.to_day),
			        'commission_percengate': has.percentage,
					'total_collect': total_collect,
			        'bonus_amount': bonus_amount
			    }))
			total_collect = frappe.db.sql("""select sum(a.allocated_amount) from `tabPayment Entry Receive Reference` a inner join `tabPayment Entry Receive` b on b.`name` = a.parent inner join `tabSales Target Detail` c on c.sales_invoice = a.reference_name where b.docstatus = '1' and b.collector = %s and datediff(b.posting_date,c.sales_invoice_date) > %s""", (sales, last_day))[0][0]
			si_list.append(frappe._dict({
				'range': "Out of range",
			    'commission_percengate': 0,
				'total_collect': total_collect,
				'bonus_amount': 0
			}))
		else:
			si_list.append(frappe._dict({
		        'range': "Out of range",
		        'commission_percengate': 0,
				'total_collect': 0,
		        'bonus_amount': 0
		    }))
	return si_list
