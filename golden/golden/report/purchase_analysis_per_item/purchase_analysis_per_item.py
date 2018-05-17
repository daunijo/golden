# Copyright (c) 2013, RSS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import cint, flt, cstr
from frappe import _

def execute(filters=None):
	columns = get_columns()
	data = []

	conditions = get_conditions(filters)
	sl_entries = frappe.db.sql("""select item_group, item_code, item_name, stock_uom from `tabItem` where disabled = '0' %s""" % conditions, as_dict=1)
	for cl in sl_entries:
		actual_qty = frappe.db.sql("""select sum(b.actual_qty) from `tabItem` i inner join `tabBin` b on i.item_code = b.item_code inner join `tabWarehouse` w on b.warehouse = w.`name` where i.item_code = %s""", cl.item_code)[0][0] or 0
		bs_qty = frappe.db.sql("""select sum(b.actual_qty) from `tabItem` i inner join `tabBin` b on i.item_code = b.item_code inner join `tabWarehouse` w on b.warehouse = w.`name` where i.item_code = %s and w.gudang_bs = '1'""", cl.item_code)[0][0] or 0
		po_date = get_purchase_order(cl.item_code)
		po_name = get_purchase_order2(cl.item_code)
		po_qty = get_purchase_order3(cl.item_code)
		# po = frappe.db.sql("""select po.`name` from `tabPurchase Order Item` poi inner join `tabPurchase Order` po on poi.parent = po.`name` where po.docstatus = '1' and po.`status` in ('To Receive and Bill', 'To Receive') and poi.item_code = %s order by po.transaction_date desc limit 1""", cl.item_code)[0][0]
		data.append([cl.item_group, cl.item_code, cl.item_name, cl.stock_uom, actual_qty, bs_qty, po_date, po_name, po_qty])

	return columns, data

def get_purchase_order(item_code):
	po = frappe.db.sql("""select count(*) from `tabPurchase Order Item` poi inner join `tabPurchase Order` po on poi.parent = po.`name` where po.docstatus = '1' and po.`status` in ('To Receive and Bill', 'To Receive') and poi.item_code = %s order by po.transaction_date desc limit 1""", item_code)[0][0]
	if flt(po) == 1:
		poi = frappe.db.sql("""select po.transaction_date from `tabPurchase Order Item` poi inner join `tabPurchase Order` po on poi.parent = po.`name` where po.docstatus = '1' and po.`status` in ('To Receive and Bill', 'To Receive') and poi.item_code = %s order by po.transaction_date desc limit 1""", item_code)[0][0]
	else:
		poi = ""
	return poi

def get_purchase_order2(item_code):
	po = frappe.db.sql("""select count(*) from `tabPurchase Order Item` poi inner join `tabPurchase Order` po on poi.parent = po.`name` where po.docstatus = '1' and po.`status` in ('To Receive and Bill', 'To Receive') and poi.item_code = %s order by po.transaction_date desc limit 1""", item_code)[0][0]
	if flt(po) == 1:
		poi = frappe.db.sql("""select po.`name` from `tabPurchase Order Item` poi inner join `tabPurchase Order` po on poi.parent = po.`name` where po.docstatus = '1' and po.`status` in ('To Receive and Bill', 'To Receive') and poi.item_code = %s order by po.transaction_date desc limit 1""", item_code)[0][0]
	else:
		poi = ""
	return poi

def get_purchase_order3(item_code):
	po = frappe.db.sql("""select count(*) from `tabPurchase Order Item` poi inner join `tabPurchase Order` po on poi.parent = po.`name` where po.docstatus = '1' and po.`status` in ('To Receive and Bill', 'To Receive') and poi.item_code = %s order by po.transaction_date desc limit 1""", item_code)[0][0]
	if flt(po) == 1:
		poi = frappe.db.sql("""select sum(stock_qty) from `tabPurchase Order Item` poi inner join `tabPurchase Order` po on poi.parent = po.`name` where po.docstatus = '1' and po.`status` in ('To Receive and Bill', 'To Receive') and poi.item_code = %s order by po.transaction_date desc limit 1""", item_code)[0][0]
	else:
		poi = ""
	return poi

def get_columns():
	"""return columns"""

	columns = [
		_("Item Group")+":Link/Item Group:140",
		_("Item Code")+":Link/Item:120",
		_("Item Name")+":Data:150",
		_("UOM")+":Link/UOM:60",
		_("Actual All")+":Int:80",
		_("Actual BS")+":Int:80",
		_("PO Date")+":Date:100",
		_("PO")+":Link/Purchase Order:100",
		_("Purchase Qty")+":Int:90",
		_("Container")+":Data:120",
		_("History")+":Data:150",
	]

	return columns

def get_conditions(filters):
	conditions = ""
	if filters.get("item_group"):
		conditions += " and item_group = '%s'" % frappe.db.escape(filters["item_group"])

	return conditions
