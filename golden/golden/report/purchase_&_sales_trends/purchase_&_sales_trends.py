# Copyright (c) 2013, RSS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import getdate, flt
from frappe import _

def execute(filters=None):
	columns = get_columns(filters)
	data = []

	conditions = get_conditions(filters)
	begin = filters.get("fiscal_year") + "-01-01"
	sl_entries = frappe.db.sql("""select distinct(item_code) from `tabStock Ledger Entry` where fiscal_year = %s""", filters.get("fiscal_year"), as_dict=1)
	for cl in sl_entries:
		item_name = frappe.db.get_value("Item", cl.item_code, "item_name")
		sa = frappe.db.sql("""select sum(actual_qty) from `tabStock Ledger Entry` where docstatus = '1' and posting_date < %s and item_code = %s""", (begin, cl.item_code))[0][0] or 0

		essential = [cl.item_code, item_name, sa]

		if filters.get("period") == "Monthly":
			"""january"""
			posting_date = "%"+filters.get("fiscal_year")+"-01%"
			pr01 = frappe.db.sql("""select sum(actual_qty) from `tabStock Ledger Entry` where docstatus = '1' and voucher_type = 'Purchase Receipt' and posting_date like %s and item_code = %s""", (posting_date, cl.item_code))[0][0] or 0
			dn01 = frappe.db.sql("""select sum(actual_qty * -1) from `tabStock Ledger Entry` where docstatus = '1' and voucher_type = 'Delivery Note' and posting_date like %s and item_code = %s""", (posting_date, cl.item_code))[0][0] or 0
			if flt(sa) >= 1 or flt(dn01) >= 1:
				percent01 = (flt(dn01)/(flt(pr01)+flt(sa)))*100
			else:
				percent01 = 0
			sa = (flt(sa) + flt(pr01)) - flt(dn01)
			"""february"""
			posting_date = "%"+filters.get("fiscal_year")+"-02%"
			pr02 = frappe.db.sql("""select sum(actual_qty) from `tabStock Ledger Entry` where docstatus = '1' and voucher_type = 'Purchase Receipt' and posting_date like %s and item_code = %s""", (posting_date, cl.item_code))[0][0] or 0
			dn02 = frappe.db.sql("""select sum(actual_qty * -1) from `tabStock Ledger Entry` where docstatus = '1' and voucher_type = 'Delivery Note' and posting_date like %s and item_code = %s""", (posting_date, cl.item_code))[0][0] or 0
			if flt(sa) >= 1 or flt(dn02) >= 1:
				percent02 = (flt(dn02)/(flt(pr02)+flt(sa)))*100
			else:
				percent02 = 0
			sa = (flt(sa) + flt(pr02)) - flt(dn02)
			"""march"""
			posting_date = "%"+filters.get("fiscal_year")+"-03%"
			pr03 = frappe.db.sql("""select sum(actual_qty) from `tabStock Ledger Entry` where docstatus = '1' and voucher_type = 'Purchase Receipt' and posting_date like %s and item_code = %s""", (posting_date, cl.item_code))[0][0] or 0
			dn03 = frappe.db.sql("""select sum(actual_qty * -1) from `tabStock Ledger Entry` where docstatus = '1' and voucher_type = 'Delivery Note' and posting_date like %s and item_code = %s""", (posting_date, cl.item_code))[0][0] or 0
			if flt(sa) >= 1 or flt(dn03) >= 1:
				percent03 = (flt(dn03)/(flt(pr03)+flt(sa)))*100
			else:
				percent03 = 0
			sa = (flt(sa) + flt(pr03)) - flt(dn03)
			"""april"""
			posting_date = "%"+filters.get("fiscal_year")+"-04%"
			pr04 = frappe.db.sql("""select sum(actual_qty) from `tabStock Ledger Entry` where docstatus = '1' and voucher_type = 'Purchase Receipt' and posting_date like %s and item_code = %s""", (posting_date, cl.item_code))[0][0] or 0
			dn04 = frappe.db.sql("""select sum(actual_qty * -1) from `tabStock Ledger Entry` where docstatus = '1' and voucher_type = 'Delivery Note' and posting_date like %s and item_code = %s""", (posting_date, cl.item_code))[0][0] or 0
			if flt(sa) >= 1 or flt(dn04) >= 1:
				percent04 = (flt(dn04)/(flt(pr04)+flt(sa)))*100
			else:
				percent04 = 0
			sa = (flt(sa) + flt(pr04)) - flt(dn04)
			"""may"""
			posting_date = "%"+filters.get("fiscal_year")+"-05%"
			pr05 = frappe.db.sql("""select sum(actual_qty) from `tabStock Ledger Entry` where docstatus = '1' and voucher_type = 'Purchase Receipt' and posting_date like %s and item_code = %s""", (posting_date, cl.item_code))[0][0] or 0
			dn05 = frappe.db.sql("""select sum(actual_qty * -1) from `tabStock Ledger Entry` where docstatus = '1' and voucher_type = 'Delivery Note' and posting_date like %s and item_code = %s""", (posting_date, cl.item_code))[0][0] or 0
			if flt(sa) >= 1 or flt(dn05) >= 1:
				percent05 = (flt(dn05)/(flt(pr05)+flt(sa)))*100
			else:
				percent05 = 0
			sa = (flt(sa) + flt(pr05)) - flt(dn05)
			"""june"""
			posting_date = "%"+filters.get("fiscal_year")+"-06%"
			pr06 = frappe.db.sql("""select sum(actual_qty) from `tabStock Ledger Entry` where docstatus = '1' and voucher_type = 'Purchase Receipt' and posting_date like %s and item_code = %s""", (posting_date, cl.item_code))[0][0] or 0
			dn06 = frappe.db.sql("""select sum(actual_qty * -1) from `tabStock Ledger Entry` where docstatus = '1' and voucher_type = 'Delivery Note' and posting_date like %s and item_code = %s""", (posting_date, cl.item_code))[0][0] or 0
			if flt(sa) >= 1 or flt(dn06) >= 1:
				percent06 = (flt(dn06)/(flt(pr06)+flt(sa)))*100
			else:
				percent06 = 0
			sa = (flt(sa) + flt(pr06)) - flt(dn06)
			"""july"""
			posting_date = "%"+filters.get("fiscal_year")+"-07%"
			pr07 = frappe.db.sql("""select sum(actual_qty) from `tabStock Ledger Entry` where docstatus = '1' and voucher_type = 'Purchase Receipt' and posting_date like %s and item_code = %s""", (posting_date, cl.item_code))[0][0] or 0
			dn07 = frappe.db.sql("""select sum(actual_qty * -1) from `tabStock Ledger Entry` where docstatus = '1' and voucher_type = 'Delivery Note' and posting_date like %s and item_code = %s""", (posting_date, cl.item_code))[0][0] or 0
			if flt(sa) >= 1 or flt(dn07) >= 1:
				percent07 = (flt(dn07)/(flt(pr07)+flt(sa)))*100
			else:
				percent07 = 0
			sa = (flt(sa) + flt(pr07)) - flt(dn07)
			"""august"""
			posting_date = "%"+filters.get("fiscal_year")+"-08%"
			pr08 = frappe.db.sql("""select sum(actual_qty) from `tabStock Ledger Entry` where docstatus = '1' and voucher_type = 'Purchase Receipt' and posting_date like %s and item_code = %s""", (posting_date, cl.item_code))[0][0] or 0
			dn08 = frappe.db.sql("""select sum(actual_qty * -1) from `tabStock Ledger Entry` where docstatus = '1' and voucher_type = 'Delivery Note' and posting_date like %s and item_code = %s""", (posting_date, cl.item_code))[0][0] or 0
			if flt(sa) >= 1 or flt(dn08) >= 1:
				percent08 = (flt(dn08)/(flt(pr08)+flt(sa)))*100
			else:
				percent08 = 0
			sa = (flt(sa) + flt(pr08)) - flt(dn08)
			"""september"""
			posting_date = "%"+filters.get("fiscal_year")+"-09%"
			pr09 = frappe.db.sql("""select sum(actual_qty) from `tabStock Ledger Entry` where docstatus = '1' and voucher_type = 'Purchase Receipt' and posting_date like %s and item_code = %s""", (posting_date, cl.item_code))[0][0] or 0
			dn09 = frappe.db.sql("""select sum(actual_qty * -1) from `tabStock Ledger Entry` where docstatus = '1' and voucher_type = 'Delivery Note' and posting_date like %s and item_code = %s""", (posting_date, cl.item_code))[0][0] or 0
			if flt(sa) >= 1 or flt(dn09) >= 1:
				percent09 = (flt(dn09)/(flt(pr09)+flt(sa)))*100
			else:
				percent09 = 0
			sa = (flt(sa) + flt(pr09)) - flt(dn09)
			"""october"""
			posting_date = "%"+filters.get("fiscal_year")+"-10%"
			pr10 = frappe.db.sql("""select sum(actual_qty) from `tabStock Ledger Entry` where docstatus = '1' and voucher_type = 'Purchase Receipt' and posting_date like %s and item_code = %s""", (posting_date, cl.item_code))[0][0] or 0
			dn10 = frappe.db.sql("""select sum(actual_qty * -1) from `tabStock Ledger Entry` where docstatus = '1' and voucher_type = 'Delivery Note' and posting_date like %s and item_code = %s""", (posting_date, cl.item_code))[0][0] or 0
			if flt(sa) >= 1 or flt(dn10) >= 1:
				percent10 = (flt(dn10)/(flt(pr10)+flt(sa)))*100
			else:
				percent10 = 0
			sa = (flt(sa) + flt(pr10)) - flt(dn10)
			"""november"""
			posting_date = "%"+filters.get("fiscal_year")+"-11%"
			pr11 = frappe.db.sql("""select sum(actual_qty) from `tabStock Ledger Entry` where docstatus = '1' and voucher_type = 'Purchase Receipt' and posting_date like %s and item_code = %s""", (posting_date, cl.item_code))[0][0] or 0
			dn11 = frappe.db.sql("""select sum(actual_qty * -1) from `tabStock Ledger Entry` where docstatus = '1' and voucher_type = 'Delivery Note' and posting_date like %s and item_code = %s""", (posting_date, cl.item_code))[0][0] or 0
			if flt(sa) >= 1 or flt(dn11) >= 1:
				percent11 = (flt(dn11)/(flt(pr11)+flt(sa)))*100
			else:
				percent11 = 0
			sa = (flt(sa) + flt(pr11)) - flt(dn11)
			"""december"""
			posting_date = "%"+filters.get("fiscal_year")+"-12%"
			pr12 = frappe.db.sql("""select sum(actual_qty) from `tabStock Ledger Entry` where docstatus = '1' and voucher_type = 'Purchase Receipt' and posting_date like %s and item_code = %s""", (posting_date, cl.item_code))[0][0] or 0
			dn12 = frappe.db.sql("""select sum(actual_qty * -1) from `tabStock Ledger Entry` where docstatus = '1' and voucher_type = 'Delivery Note' and posting_date like %s and item_code = %s""", (posting_date, cl.item_code))[0][0] or 0
			if flt(sa) >= 1 or flt(dn12) >= 1:
				percent12 = (flt(dn12)/(flt(pr12)+flt(sa)))*100
			else:
				percent12 = 0
			sa = (flt(sa) + flt(pr12)) - flt(dn12)
			add_value = [pr01, dn01, percent01, pr02, dn02, percent02, pr03, dn03, percent03, pr04, dn04, percent04, pr05, dn05, percent05, pr06, dn06, percent06, pr07, dn07, percent07, pr08, dn08, percent08, pr09, dn09, percent09, pr10, dn10, percent10, pr11, dn11, percent11, pr12, dn12, percent12]
		elif filters.get("period") == "Quarterly":
			"""january-march"""
			from_date = filters.get("fiscal_year")+"-01-01"
			to_date = filters.get("fiscal_year")+"-03-31"
			pr1 = frappe.db.sql("""select sum(actual_qty) from `tabStock Ledger Entry` where docstatus = '1' and voucher_type = 'Purchase Receipt' and posting_date >= %s and posting_date <= %s and item_code = %s""", (from_date, to_date, cl.item_code))[0][0] or 0
			dn1 = frappe.db.sql("""select sum(actual_qty * -1) from `tabStock Ledger Entry` where docstatus = '1' and voucher_type = 'Delivery Note' and posting_date >= %s and posting_date <= %s and item_code = %s""", (from_date, to_date, cl.item_code))[0][0] or 0
			if flt(sa) >= 1 or flt(dn1) >= 1:
				percent1 = (flt(dn1)/(flt(pr1)+flt(sa)))*100
			else:
				percent1 = 0
			sa = (flt(sa) + flt(pr1)) - flt(dn1)
			"""april-june"""
			from_date = filters.get("fiscal_year")+"-04-01"
			to_date = filters.get("fiscal_year")+"-06-30"
			pr2 = frappe.db.sql("""select sum(actual_qty) from `tabStock Ledger Entry` where docstatus = '1' and voucher_type = 'Purchase Receipt' and posting_date >= %s and posting_date <= %s and item_code = %s""", (from_date, to_date, cl.item_code))[0][0] or 0
			dn2 = frappe.db.sql("""select sum(actual_qty * -1) from `tabStock Ledger Entry` where docstatus = '1' and voucher_type = 'Delivery Note' and posting_date >= %s and posting_date <= %s and item_code = %s""", (from_date, to_date, cl.item_code))[0][0] or 0
			if flt(sa) >= 1 or flt(dn2) >= 1:
				percent2 = (flt(dn2)/(flt(pr2)+flt(sa)))*100
			else:
				percent2 = 0
			sa = (flt(sa) + flt(pr2)) - flt(dn2)
			"""july-september"""
			from_date = filters.get("fiscal_year")+"-07-01"
			to_date = filters.get("fiscal_year")+"-09-30"
			pr3 = frappe.db.sql("""select sum(actual_qty) from `tabStock Ledger Entry` where docstatus = '1' and voucher_type = 'Purchase Receipt' and posting_date >= %s and posting_date <= %s and item_code = %s""", (from_date, to_date, cl.item_code))[0][0] or 0
			dn3 = frappe.db.sql("""select sum(actual_qty * -1) from `tabStock Ledger Entry` where docstatus = '1' and voucher_type = 'Delivery Note' and posting_date >= %s and posting_date <= %s and item_code = %s""", (from_date, to_date, cl.item_code))[0][0] or 0
			if flt(sa) >= 1 or flt(dn3) >= 1:
				percent3 = (flt(dn3)/(flt(pr3)+flt(sa)))*100
			else:
				percent3 = 0
			sa = (flt(sa) + flt(pr3)) - flt(dn3)
			"""october-december"""
			from_date = filters.get("fiscal_year")+"-10-01"
			to_date = filters.get("fiscal_year")+"-12-31"
			pr4 = frappe.db.sql("""select sum(actual_qty) from `tabStock Ledger Entry` where docstatus = '1' and voucher_type = 'Purchase Receipt' and posting_date >= %s and posting_date <= %s and item_code = %s""", (from_date, to_date, cl.item_code))[0][0] or 0
			dn4 = frappe.db.sql("""select sum(actual_qty * -1) from `tabStock Ledger Entry` where docstatus = '1' and voucher_type = 'Delivery Note' and posting_date >= %s and posting_date <= %s and item_code = %s""", (from_date, to_date, cl.item_code))[0][0] or 0
			if flt(sa) >= 1 or flt(dn4) >= 1:
				percent4 = (flt(dn4)/(flt(pr4)+flt(sa)))*100
			else:
				percent4 = 0
			sa = (flt(sa) + flt(pr4)) - flt(dn4)
			add_value = [pr1, dn1, percent1, pr2, dn2, percent2, pr3, dn3, percent3, pr4, dn4, percent4]
		elif filters.get("period") == "Half-Yearly":
			"""january-june"""
			from_date = filters.get("fiscal_year")+"-01-01"
			to_date = filters.get("fiscal_year")+"-06-30"
			pr1 = frappe.db.sql("""select sum(actual_qty) from `tabStock Ledger Entry` where docstatus = '1' and voucher_type = 'Purchase Receipt' and posting_date >= %s and posting_date <= %s and item_code = %s""", (from_date, to_date, cl.item_code))[0][0] or 0
			dn1 = frappe.db.sql("""select sum(actual_qty * -1) from `tabStock Ledger Entry` where docstatus = '1' and voucher_type = 'Delivery Note' and posting_date >= %s and posting_date <= %s and item_code = %s""", (from_date, to_date, cl.item_code))[0][0] or 0
			if flt(sa) >= 1 or flt(dn1) >= 1:
				percent1 = (flt(dn1)/(flt(pr1)+flt(sa)))*100
			else:
				percent1 = 0
			sa = (flt(sa) + flt(pr1)) - flt(dn1)
			"""july-december"""
			from_date = filters.get("fiscal_year")+"-07-01"
			to_date = filters.get("fiscal_year")+"-12-31"
			pr2 = frappe.db.sql("""select sum(actual_qty) from `tabStock Ledger Entry` where docstatus = '1' and voucher_type = 'Purchase Receipt' and posting_date >= %s and posting_date <= %s and item_code = %s""", (from_date, to_date, cl.item_code))[0][0] or 0
			dn2 = frappe.db.sql("""select sum(actual_qty * -1) from `tabStock Ledger Entry` where docstatus = '1' and voucher_type = 'Delivery Note' and posting_date >= %s and posting_date <= %s and item_code = %s""", (from_date, to_date, cl.item_code))[0][0] or 0
			if flt(sa) >= 1 or flt(dn2) >= 1:
				percent2 = (flt(dn2)/(flt(pr2)+flt(sa)))*100
			else:
				percent2 = 0
			sa = (flt(sa) + flt(pr2)) - flt(dn2)
			add_value = [pr1, dn1, percent1, pr2, dn2, percent2]
		elif filters.get("period") == "Yearly":
			from_date = filters.get("fiscal_year")+"-01-01"
			to_date = filters.get("fiscal_year")+"-12-31"
			pr = frappe.db.sql("""select sum(actual_qty) from `tabStock Ledger Entry` where docstatus = '1' and voucher_type = 'Purchase Receipt' and posting_date >= %s and posting_date <= %s and item_code = %s""", (from_date, to_date, cl.item_code))[0][0] or 0
			dn = frappe.db.sql("""select sum(actual_qty * -1) from `tabStock Ledger Entry` where docstatus = '1' and voucher_type = 'Delivery Note' and posting_date >= %s and posting_date <= %s and item_code = %s""", (from_date, to_date, cl.item_code))[0][0] or 0
			if flt(sa) >= 1 or flt(dn) >= 1:
				percent = (flt(dn)/(flt(pr)+flt(sa)))*100
			else:
				percent = 0
			add_value = [pr, dn, percent]
		data.append(essential + add_value)

	return columns, data

def get_columns(filters):
	"""return columns"""

	essential = [
		_("Item Code")+":Link/Item:120",
		_("Item Name")+":Data:170",
		_("Saldo Awal")+":Int:100",
	]
	if filters.get("period") == "Monthly":
		add_columns = [
			_("Jan (Purchase)")+":Int:100",
			_("Jan (Sales)")+":Int:100",
			_("Jan (%)")+":Percent:70",
			_("Feb (Purchase)")+":Int:100",
			_("Feb (Sales)")+":Int:100",
			_("Feb (%)")+":Percent:70",
			_("Mar (Purchase)")+":Int:100",
			_("Mar (Sales)")+":Int:100",
			_("Mar (%)")+":Percent:70",
			_("Apr (Purchase)")+":Int:100",
			_("Apr (Sales)")+":Int:100",
			_("Apr (%)")+":Percent:70",
			_("May (Purchase)")+":Int:100",
			_("May (Sales)")+":Int:100",
			_("May (%)")+":Percent:70",
			_("Jun (Purchase)")+":Int:100",
			_("Jun (Sales)")+":Int:100",
			_("Jun (%)")+":Percent:70",
			_("Jul (Purchase)")+":Int:100",
			_("Jul (Sales)")+":Int:100",
			_("Jul (%)")+":Percent:70",
			_("Aug (Purchase)")+":Int:100",
			_("Aug (Sales)")+":Int:100",
			_("Aug (%)")+":Percent:70",
			_("Sep (Purchase)")+":Int:100",
			_("Sep (Sales)")+":Int:100",
			_("Sep (%)")+":Percent:70",
			_("Oct (Purchase)")+":Int:100",
			_("Oct (Sales)")+":Int:100",
			_("Oct (%)")+":Percent:70",
			_("Nov (Purchase)")+":Int:100",
			_("Nov (Sales)")+":Int:100",
			_("Nov (%)")+":Percent:70",
			_("Dec (Purchase)")+":Int:100",
			_("Dec (Sales)")+":Int:100",
			_("Dec (%)")+":Percent:70",
		]
	elif filters.get("period") == "Quarterly":
		add_columns = [
			_("Jan-Mar (Purchase)")+":Int:120",
			_("Jan-Mar (Sales)")+":Int:120",
			_("Jan-Mar (%)")+":Percent:90",
			_("Apr-Jun (Purchase)")+":Int:120",
			_("Apr-Jun (Sales)")+":Int:120",
			_("Apr-Jun (%)")+":Percent:90",
			_("Jul-Sep (Purchase)")+":Int:120",
			_("Jul-Sep (Sales)")+":Int:120",
			_("Jul-Sep (%)")+":Percent:90",
			_("Oct-Dec (Purchase)")+":Int:120",
			_("Oct-Dec (Sales)")+":Int:120",
			_("Oct-Dec (%)")+":Percent:90",
		]
	elif filters.get("period") == "Half-Yearly":
		add_columns = [
			_("Jan-Jun (Purchase)")+":Int:120",
			_("Jan-Jun (Sales)")+":Int:120",
			_("Jan-Jun (%)")+":Percent:90",
			_("Jul-Dec (Purchase)")+":Int:120",
			_("Jul-Dec (Sales)")+":Int:120",
			_("Jul-Dec (%)")+":Percent:90",
		]
	else:
		add_columns = [
			_(filters.get("fiscal_year")+" (Purchase)")+":Int:100",
			_(filters.get("fiscal_year")+" (Sales)")+":Int:100",
			_(filters.get("fiscal_year")+" (%)")+":Percent:90",
		]
	columns = essential + add_columns

	return columns

def get_conditions(filters):
	conditions = ""

	return conditions
