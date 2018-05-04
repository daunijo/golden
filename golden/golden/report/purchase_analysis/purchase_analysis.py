# Copyright (c) 2013, RSS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, getdate

def execute(filters=None):
	columns = get_columns()
	data = []

	conditions = get_conditions(filters)
	sl_entries = frappe.db.sql("""select `name`, minimum_item from `tabItem Group` where is_group = '0' %s""" % conditions, as_dict=1)
	for cl in sl_entries:
		items = frappe.db.sql("""select * from `tabItem` where item_group = %s and disabled = '0'""", cl.name, as_dict=1)
		count_actual = 0
		count_po = 0
		stock_qty = 0
		stock_value = 0
		for it in items:
			min_stock = it.minimum_stock
			actual_qty = frappe.db.sql("""select sum(b.actual_qty) from `tabItem` i inner join `tabBin` b on i.item_code = b.item_code inner join `tabWarehouse` w on b.warehouse = w.`name` where w.gudang_bs = '0' and i.item_code = %s""", it.item_code)[0][0]
			stock_qty = flt(stock_qty) + flt(actual_qty)
			valuation = frappe.db.sql("""select sum(b.stock_value) from `tabItem` i inner join `tabBin` b on i.item_code = b.item_code inner join `tabWarehouse` w on b.warehouse = w.`name` where w.gudang_bs = '0' and i.item_code = %s""", it.item_code)[0][0]
			stock_value = flt(stock_value) + flt(valuation)
			if flt(actual_qty) >= flt(min_stock):
				count_actual = count_actual + 1
			else:
				po_qty = frappe.db.sql("""select sum(stock_qty) from `tabPurchase Order Item` poi inner join `tabPurchase Order` po on poi.parent = po.`name` where po.docstatus = '1' and po.`status` in ('To Receive and Bill', 'To Receive') and poi.item_code = %s""", it.item_code)[0][0]
				po_actual_qty = flt(po_qty) + flt(actual_qty)
				if flt(po_actual_qty) >= flt(min_stock):
					count_po = count_po + 1

		diff = flt(cl.minimum_item) - flt(count_actual) - flt(count_po)
		if flt(diff) <= 0:
			record = 0
		else:
			record = diff
		data.append([cl.name, cl.minimum_item, count_actual, stock_qty, stock_value, count_po, record])

	return columns, data

def get_columns():
	"""return columns"""

	columns = [
		_("Item Group")+":Link/Item Group:150",
		_("Minimum Item")+":Int:100",
		_("Actual")+":Int:100",
		_("Stock Qty")+":Int:100",
		_("Stock Value")+":Currency:120",
		_("Purchase Order")+":Int:100",
		_("Record")+":Int:100",
	]

	return columns

def get_conditions(filters):
	conditions = ""

	return conditions
