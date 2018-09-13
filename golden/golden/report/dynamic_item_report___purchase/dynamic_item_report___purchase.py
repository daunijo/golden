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
	sl_entries = frappe.db.sql("""select `name`, item_code, item_name, item_group, stock_uom from `tabItem` where disabled = '0' and is_stock_item = '1' %s""" % conditions, as_dict=1)
	for cl in sl_entries:
		if filters.get("warehouse"):
			bin_qty = frappe.db.sql("""select sum(b.actual_qty), sum(b.projected_qty), sum(actual_qty - reserved_qty) from `tabWarehouse` w1 inner join `tabWarehouse` w2 on w1.parent_warehouse = w2.`name` inner join `tabWarehouse` w3 on w2.parent_warehouse = w3.`name` inner join `tabBin` b on w1.`name` = b.warehouse where w1.type = 'Location' and w3.`name` = %s and w1.disabled = '0' and b.item_code = %s""", (frappe.db.escape(filters["warehouse"]), cl.item_code))
		else:
			bin_qty = frappe.db.sql("""select sum(b.actual_qty), sum(b.projected_qty), sum(actual_qty - reserved_qty) from `tabWarehouse` w1 inner join `tabWarehouse` w2 on w1.parent_warehouse = w2.`name` inner join `tabWarehouse` w3 on w2.parent_warehouse = w3.`name` inner join `tabBin` b on w1.`name` = b.warehouse where w1.type = 'Location' and w1.disabled = '0' and b.item_code = %s""", cl.item_code)
		po = frappe.db.sql("""select sum(poi.stock_qty) from `tabPurchase Order` po inner join `tabPurchase Order Item` poi on po.`name` = poi.parent where po.`status` in ('To Receive and Bill', 'To Receive') and po.docstatus = '1' and poi.item_code = %s""", cl.item_code)[0][0]
		count_last_receipt = frappe.db.sql("""select count(*) from `tabPurchase Receipt` pr inner join `tabPurchase Receipt Item` pri on pr.`name` = pri.parent where pr.docstatus = '1' and pri.item_code = %s""", cl.item_code)[0][0]
		if flt(count_last_receipt) != 0:
			last_receipt = frappe.db.sql("""select pr.posting_date from `tabPurchase Receipt` pr inner join `tabPurchase Receipt Item` pri on pr.`name` = pri.parent where pr.docstatus = '1' and pri.item_code = %s order by pr.posting_date desc limit 1""", cl.item_code)[0][0]
		else:
			last_receipt = ""
		if filters.get("selling_price_list"):
			sell_item_price = frappe.db.get_value("Item Price", {"price_list": frappe.db.escape(filters["selling_price_list"]), "item_code": cl.item_code}, "price_list_rate")
		else:
			sell_item_price = ""
		if filters.get("buying_price_list"):
			buy_item_price = frappe.db.get_value("Item Price", {"price_list": frappe.db.escape(filters["buying_price_list"]), "item_code": cl.item_code}, "price_list_rate")
		else:
			buy_item_price = ""
		so = frappe.db.sql("""select sum(soi.stock_qty) from `tabSales Order` so inner join `tabSales Order Item` soi on so.`name` = soi.parent where so.`status` in ('To Deliver and Bill', 'To Deliver') and so.docstatus = '1' and soi.item_code = %s""", cl.name)[0][0]
		data.append([cl.item_code, cl.item_name, cl.item_group, cl.stock_uom, bin_qty[0][0], so, bin_qty[0][2], po, sell_item_price, buy_item_price, bin_qty[0][1], last_receipt])

	return columns, data

def get_columns():
	"""return columns"""

	columns = [
		_("Item ID")+":Link/Item:120",
		_("Item Name")+":Data:180",
		_("Item Group")+":Data:110",
		_("UOM")+":Link/UOM:60",
		_("Actual Qty")+":Float:80",
		_("SO Qty")+":Float:70",
		_("Available Qty")+":Float:90",
		_("PO Qty")+":Float:70",
		_("Selling Price Rate")+":Float:100",
		_("Buying Price Rate")+":Float:100",
		_("Projected Qty")+":Float:90",
		_("Last Receipt Date")+":Date:120",
	]

	return columns

def get_conditions(filters):
	conditions = ""
	if filters.get("item_code"):
		conditions += " and item_code = '%s'" % frappe.db.escape(filters["item_code"])
	if filters.get("item_name"):
		conditions += " and item_name like '%%%s%%'" % frappe.db.escape(filters["item_name"])
	if filters.get("item_group"):
		conditions += " and item_group = '%s'" % frappe.db.escape(filters["item_group"])
	if filters.get("limit"):
		if filters.get("limit") != "No Limit":
			conditions += " limit %s" % frappe.db.escape(filters["limit"])
	return conditions
