# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt

def execute(filters=None):
	columns = get_columns()
	data = []

	conditions = get_conditions(filters)
	vouchers = get_voucher(filters)
	stock_fil = get_stock(filters)
	stock_all = 0
	stock_all = flt(stock_all) + flt(stock_fil)
	sl_entries = frappe.db.sql("""select concat_ws(" ",sle.posting_date,sle.posting_time) as date, sle.item_code, i.item_name, sle.voucher_type, sle.voucher_no, sle.actual_qty, sle.qty_after_transaction, sle.warehouse, sle.stock_uom, sle.stock_value_difference, sle.valuation_rate from `tabStock Ledger Entry` sle inner join `tabItem` i on i.item_code = sle.item_code where sle.docstatus = '1' %s order by date asc""" % conditions, as_dict=1)
	for cl in sl_entries:
		if cl.voucher_type == "Stock Reconciliation":
			qty = cl.qty_after_transaction
			qty2 = frappe.db.get_value("Stock Reconciliation Item", {"parent": cl.voucher_no, "item_code": cl.item_code}, "quantity_difference")
			stock_all = flt(stock_all) + flt(qty2)
		else:
			qty = cl.actual_qty
			stock_all = flt(stock_all) + flt(cl.actual_qty)

		if cl.voucher_type == "Delivery Note":
			vt = "Delivery Order"
			pc = frappe.db.get_value("Delivery Note", cl.voucher_no, "packing")
			vn = frappe.db.get_value("Delivery Order Detail", {"packing": pc, "docstatus": 1}, "parent")
		elif cl.voucher_type == "Purchase Receipt":
			vt = "Receive Order"
			vn = frappe.db.get_value("Purchase Receipt", cl.voucher_no, "receive_order")
		elif cl.voucher_type == "Stock Entry":
			purpose = frappe.db.get_value("Stock Entry", cl.voucher_no, "purpose")
			if purpose == "Material Transfer":
				vt = "Transfer Order"
				vn = frappe.db.get_value("Stock Entry", cl.voucher_no, "transfer_order")
			elif purpose == "Material Receipt":
				vt = "Sales Return"
				vn = frappe.db.get_value("Stock Entry", cl.voucher_no, "sales_return")
			elif purpose == "Material Issue":
				vt = "Purchase Return"
				vn = frappe.db.get_value("Stock Entry", cl.voucher_no, "purchase_return")
			else:
				vt = cl.voucher_type
				vn = cl.voucher_no
		else:
			vt = cl.voucher_type
			vn = cl.voucher_no

		loc = "<a href='/desk#query-report/Stock Card by Location?item_code="+cl.item_code+"&location="+cl.warehouse+"' style='border:1px #01DF01 solid; background:#01DF01; color:#FFF'>Stock per Location</a>"

		if vouchers == "All":
			data.append([cl.date, cl.item_code, cl.item_name, cl.warehouse, qty, stock_all, cl.stock_uom, vt, vn, loc])
		elif vouchers == vt:
			data.append([cl.date, cl.item_code, cl.item_name, cl.warehouse, qty, stock_all, cl.stock_uom, vt, vn, loc])

	return columns, data

def get_columns():
	"""return columns"""

	columns = [
		_("Date") + ":Datetime:95",
		_("Item") + ":Link/Item:130",
		_("Item Name") + "::200",
		_("Location") + ":Link/Warehouse:150",
		_("Qty") + ":Float:60",
		_("Balance Qty") + ":Float:80",
		_("Stock UOM") + ":Link/UOM:80",
		_("Voucher Type") + "::130",
		_("Voucher #") + ":Dynamic Link/" + _("Voucher Type") + ":100",
		_("Stock Card by Location") + "::130",
	]

	return columns

def get_conditions(filters):
	conditions = ""
	if filters.get("company"):
		conditions += " and sle.company = '%s'" % frappe.db.escape(filters["company"])
	if filters.get("from_date"):
		conditions += " and sle.posting_date >= '%s'" % frappe.db.escape(filters["from_date"])
	if filters.get("to_date"):
		conditions += " and sle.posting_date <= '%s'" % frappe.db.escape(filters["to_date"])
	if filters.get("item_code"):
		conditions += " and sle.item_code = '%s'" % frappe.db.escape(filters["item_code"])
	return conditions

def get_voucher(filters):
	vouchers = ""
	if filters.get("voucher_type"):
		if filters.get("voucher_type") == "All":
			vouchers = "All"
		elif filters.get("voucher_type") == "Transfer Order":
			vouchers = "Transfer Order"
		elif filters.get("voucher_type") == "Delivery Order":
			vouchers = "Delivery Order"
		elif filters.get("voucher_type") == "Stock Reconciliation":
			vouchers = "Stock Reconciliation"
		elif filters.get("voucher_type") == "Sales Return":
			vouchers = "Sales Return"
		elif filters.get("voucher_type") == "Receive Order":
			vouchers = "Receive Order"
		elif filters.get("voucher_type") == "Purchase Return":
			vouchers = "Purchase Return"
	return vouchers

def get_stock(filters):
	stock_fil = 0
	count1 = frappe.db.sql("""select count(distinct(warehouse)) from `tabStock Ledger Entry` where docstatus = '1' and item_code = %s and posting_date < %s""", (filters.get("item_code"), filters.get("from_date")))[0][0]
	if flt(count1) != 0:
		wr = frappe.db.sql("""select distinct(warehouse) as warehouse from `tabStock Ledger Entry` where docstatus = '1' and item_code = %s and posting_date < %s""", (filters.get("item_code"), filters.get("from_date")), as_dict=1)
		for wh in wr:
			count2 = frappe.db.sql("""select count(concat_ws(" ", posting_date, posting_time)) from `tabStock Ledger Entry` where docstatus = '1' and item_code = %s and posting_date < %s and warehouse = %s""", (filters.get("item_code"), filters.get("from_date"), wh.warehouse))[0][0]
			if flt(count2) != 0:
				qty_bef = frappe.db.sql("""select concat_ws(" ", posting_date, posting_time) as datetime, qty_after_transaction from `tabStock Ledger Entry` where docstatus = '1' and item_code = %s and posting_date < %s and warehouse = %s order by datetime desc limit 1""", (filters.get("item_code"), filters.get("from_date"), wh.warehouse))
				stock_fil = flt(stock_fil) + flt(qty_bef[0][1])
			else:
				stock_fil = flt(stock_fil) + 0
	else:
		stock_fil = flt(stock_fil) + 0
	return stock_fil
# ===========
# VERSI KEDUA
# ===========
# def execute(filters=None):
# 	columns = get_columns()
# 	data = []
#
# 	conditions = get_conditions(filters)
# 	vouchers = get_voucher(filters)
# 	if vouchers == "All":
# 		sl_entries = frappe.db.sql("""select concat_ws(' ', sle.posting_date, sle.posting_time) as date, sle.`name`, sle.item_code, sle.actual_qty, sle.qty_after_transaction, sle.warehouse as location, s.parent_warehouse as section, w.parent_warehouse, sle.valuation_rate, sle.voucher_type, sle.voucher_no, i.stock_uom, sle.voucher_detail_no from `tabStock Ledger Entry` sle inner join `tabWarehouse` s on sle.warehouse = s.`name` inner join `tabWarehouse` w on s.parent_warehouse = w.`name` inner join `tabItem` i on sle.item_code = i.item_code where sle.docstatus = '1' %s order by date asc""" % conditions, as_dict=1)
# 	elif vouchers == "Transfer Order":
# 		sl_entries = frappe.db.sql("""select concat_ws(' ', sle.posting_date, sle.posting_time) as date, sle.`name`, sle.item_code, sle.actual_qty, sle.qty_after_transaction, sle.warehouse as location, s.parent_warehouse as section, w.parent_warehouse, sle.valuation_rate, sle.voucher_type, sle.voucher_no, i.stock_uom, sle.voucher_detail_no from `tabStock Ledger Entry` sle inner join `tabWarehouse` s on sle.warehouse = s.`name` inner join `tabWarehouse` w on s.parent_warehouse = w.`name` inner join `tabItem` i on sle.item_code = i.item_code inner join `tabStock Entry` se on se.`name` = sle.voucher_no where sle.docstatus = '1' %s and se.purpose = 'Material Transfer' order by date asc""" % conditions, as_dict=1)
# 	elif vouchers == "Sales Return":
# 		sl_entries = frappe.db.sql("""select concat_ws(' ', sle.posting_date, sle.posting_time) as date, sle.`name`, sle.item_code, sle.actual_qty, sle.qty_after_transaction, sle.warehouse as location, s.parent_warehouse as section, w.parent_warehouse, sle.valuation_rate, sle.voucher_type, sle.voucher_no, i.stock_uom, sle.voucher_detail_no from `tabStock Ledger Entry` sle inner join `tabWarehouse` s on sle.warehouse = s.`name` inner join `tabWarehouse` w on s.parent_warehouse = w.`name` inner join `tabItem` i on sle.item_code = i.item_code inner join `tabStock Entry` se on se.`name` = sle.voucher_no where sle.docstatus = '1' %s and se.purpose = 'Material Receipt' order by date asc""" % conditions, as_dict=1)
# 	elif vouchers == "Purchase Return":
# 		sl_entries = frappe.db.sql("""select concat_ws(' ', sle.posting_date, sle.posting_time) as date, sle.`name`, sle.item_code, sle.actual_qty, sle.qty_after_transaction, sle.warehouse as location, s.parent_warehouse as section, w.parent_warehouse, sle.valuation_rate, sle.voucher_type, sle.voucher_no, i.stock_uom, sle.voucher_detail_no from `tabStock Ledger Entry` sle inner join `tabWarehouse` s on sle.warehouse = s.`name` inner join `tabWarehouse` w on s.parent_warehouse = w.`name` inner join `tabItem` i on sle.item_code = i.item_code inner join `tabStock Entry` se on se.`name` = sle.voucher_no where sle.docstatus = '1' %s and se.purpose = 'Material Issue' order by date asc""" % conditions, as_dict=1)
# 	elif vouchers == "Delivery Order":
# 		sl_entries = frappe.db.sql("""select concat_ws(' ', sle.posting_date, sle.posting_time) as date, sle.`name`, sle.item_code, sle.actual_qty, sle.qty_after_transaction, sle.warehouse as location, s.parent_warehouse as section, w.parent_warehouse, sle.valuation_rate, sle.voucher_type, sle.voucher_no, i.stock_uom, sle.voucher_detail_no from `tabStock Ledger Entry` sle inner join `tabWarehouse` s on sle.warehouse = s.`name` inner join `tabWarehouse` w on s.parent_warehouse = w.`name` inner join `tabItem` i on sle.item_code = i.item_code where sle.docstatus = '1' %s and sle.voucher_type = 'Delivery Note' order by date asc""" % conditions, as_dict=1)
# 	elif vouchers == "Stock Reconciliation":
# 		sl_entries = frappe.db.sql("""select concat_ws(' ', sle.posting_date, sle.posting_time) as date, sle.`name`, sle.item_code, sle.actual_qty, sle.qty_after_transaction, sle.warehouse as location, s.parent_warehouse as section, w.parent_warehouse, sle.valuation_rate, sle.voucher_type, sle.voucher_no, i.stock_uom, sle.voucher_detail_no from `tabStock Ledger Entry` sle inner join `tabWarehouse` s on sle.warehouse = s.`name` inner join `tabWarehouse` w on s.parent_warehouse = w.`name` inner join `tabItem` i on sle.item_code = i.item_code where sle.docstatus = '1' %s and sle.voucher_type = 'Stock Reconciliation' order by date asc""" % conditions, as_dict=1)
# 	elif vouchers == "Receive Order":
# 		sl_entries = frappe.db.sql("""select concat_ws(' ', sle.posting_date, sle.posting_time) as date, sle.`name`, sle.item_code, sle.actual_qty, sle.qty_after_transaction, sle.warehouse as location, s.parent_warehouse as section, w.parent_warehouse, sle.valuation_rate, sle.voucher_type, sle.voucher_no, i.stock_uom, sle.voucher_detail_no from `tabStock Ledger Entry` sle inner join `tabWarehouse` s on sle.warehouse = s.`name` inner join `tabWarehouse` w on s.parent_warehouse = w.`name` inner join `tabItem` i on sle.item_code = i.item_code where sle.docstatus = '1' %s and sle.voucher_type = 'Purchase Receipt' order by date asc""" % conditions, as_dict=1)
# 	for cl in sl_entries:
# 		item_name = frappe.db.get_value("Item", cl.item_code, "item_name")
# 		if cl.voucher_type == "Stock Reconciliation":
# 			qty = cl.qty_after_transaction
# 		else:
# 			qty = cl.actual_qty
#
# 		if cl.voucher_type == "Delivery Note":
# 			vt = "Delivery Order"
# 			pc = frappe.db.get_value("Delivery Note", cl.voucher_no, "packing")
# 			vn = frappe.db.get_value("Delivery Order Detail", {"packing": pc, "docstatus": 1}, "parent")
# 		elif cl.voucher_type == "Purchase Receipt":
# 			vt = "Receive Order"
# 			vn = frappe.db.get_value("Purchase Receipt", cl.voucher_no, "receive_order")
# 		elif cl.voucher_type == "Stock Entry":
# 			purpose = frappe.db.get_value("Stock Entry", cl.voucher_no, "purpose")
# 			if purpose == "Material Transfer":
# 				vt = "Transfer Order"
# 				vn = frappe.db.get_value("Stock Entry", cl.voucher_no, "transfer_order")
# 			elif purpose == "Material Receipt":
# 				vt = "Sales Return"
# 				vn = frappe.db.get_value("Stock Entry", cl.voucher_no, "sales_return")
# 			elif purpose == "Material Issue":
# 				vt = "Purchase Return"
# 				vn = frappe.db.get_value("Stock Entry", cl.voucher_no, "purchase_return")
# 			else:
# 				vt = cl.voucher_type
# 				vn = cl.voucher_no
# 		else:
# 			vt = cl.voucher_type
# 			vn = cl.voucher_no
#
# 		data.append([cl.date, cl.item_code, item_name, cl.location, qty, cl.qty_after_transaction, vt, vn, cl.stock_uom])
#
# 	return columns, data
#
# def get_columns():
# 	"""return columns"""
#
# 	columns = [
# 		_("Date") + ":Datetime:95",
# 		_("Item") + ":Link/Item:130",
# 		_("Item Name") + "::200",
# 		_("Location") + ":Link/Warehouse:150",
# 		_("Qty") + ":Float:50",
# 		_("Balance Qty") + ":Float:80",
# 		_("Voucher Type") + "::130",
# 		_("Voucher #") + ":Dynamic Link/" + _("Voucher Type") + ":100",
# 		_("Stock UOM") + ":Link/UOM:80",
# 	]
#
# 	return columns
#
# def get_conditions(filters):
# 	conditions = ""
# 	if filters.get("company"):
# 		conditions += " and sle.company = '%s'" % frappe.db.escape(filters["company"])
# 	if filters.get("from_date"):
# 		conditions += " and sle.posting_date >= '%s'" % frappe.db.escape(filters["from_date"])
# 	if filters.get("to_date"):
# 		conditions += " and sle.posting_date <= '%s'" % frappe.db.escape(filters["to_date"])
# 	if filters.get("warehouse"):
# 		conditions += " and w.parent_warehouse = '%s'" % frappe.db.escape(filters["warehouse"])
# 	if filters.get("section"):
# 		conditions += " and s.parent_warehouse = '%s'" % frappe.db.escape(filters["section"])
# 	if filters.get("location"):
# 		conditions += " and sle.warehouse = '%s'" % frappe.db.escape(filters["location"])
# 	if filters.get("item_code"):
# 		conditions += " and sle.item_code = '%s'" % frappe.db.escape(filters["item_code"])
# 	if filters.get("item_group"):
# 		conditions += " and i.item_group = '%s'" % frappe.db.escape(filters["item_group"])
# 	if filters.get("brand"):
# 		conditions += " and i.brand = '%s'" % frappe.db.escape(filters["brand"])
# 	return conditions
#
# def get_voucher(filters):
# 	vouchers = ""
# 	if filters.get("voucher_type"):
# 		if filters.get("voucher_type") == "All":
# 			vouchers = "All"
# 		elif filters.get("voucher_type") == "Transfer Order":
# 			vouchers = "Transfer Order"
# 		elif filters.get("voucher_type") == "Delivery Order":
# 			vouchers = "Delivery Order"
# 		elif filters.get("voucher_type") == "Stock Reconciliation":
# 			vouchers = "Stock Reconciliation"
# 		elif filters.get("voucher_type") == "Sales Return":
# 			vouchers = "Sales Return"
# 		elif filters.get("voucher_type") == "Receive Order":
# 			vouchers = "Receive Order"
# 		elif filters.get("voucher_type") == "Purchase Return":
# 			vouchers = "Purchase Return"
# 	return vouchers
# ==========
# VERSI AWAL
# ==========
# def execute(filters=None):
# 	columns = get_columns()
# 	sl_entries = get_stock_ledger_entries(filters)
# 	item_details = get_item_details(filters)
# 	opening_row = get_opening_balance(filters, columns)
#
# 	data = []
#
# 	if opening_row:
# 		data.append(opening_row)
#
# 	for sle in sl_entries:
# 		item_detail = item_details[sle.item_code]
# 		if sle.voucher_type == "Stock Entry":
# 			custom_voucher_type = "Transfer Order"
# 			custom_voucher_no = frappe.db.get_value("Stock Entry", sle.voucher_no, "transfer_order")
# 		elif sle.voucher_type == "Delivery Note":
# 			custom_voucher_type = "Packing"
# 			custom_voucher_no = frappe.db.get_value("Delivery Note", sle.voucher_no, "packing")
# 		else:
# 			custom_voucher_type = sle.voucher_type
# 			custom_voucher_no = sle.voucher_no
# 		data.append([sle.date,
# 			sle.item_code,
# 			item_detail.item_name,
# 			sle.warehouse,
# 			sle.actual_qty,
# 			sle.qty_after_transaction,
# 			sle.valuation_rate,
# 			custom_voucher_type,
# 			custom_voucher_no,
# 			item_detail.item_group,
# 			item_detail.brand,
# 			item_detail.description,
# 			sle.parent_warehouse_rss,
# 			sle.parent_section_rss,
# 			item_detail.stock_uom,
# 			(sle.incoming_rate if sle.actual_qty > 0 else 0.0),
# 			sle.stock_value
# 			])
#
# 	return columns, data
#
# def get_columns():
# 	columns = [
# 		_("Date") + ":Datetime:95",
# 		_("Item") + ":Link/Item:130",
# 		_("Item Name") + "::100",
# 		_("Location") + ":Link/Warehouse:150",
# 		_("Qty") + ":Float:50",
# 		_("Balance Qty") + ":Float:100",
# 		{"label": _("Valuation Rate"), "fieldtype": "Currency", "width": 110,
# 			"options": "Company:company:default_currency"},
# 		_("Voucher Type") + "::110",
# 		_("Voucher #") + ":Dynamic Link/" + _("Voucher Type") + ":100",
# 		_("Item Group") + ":Link/Item Group:100",
# 		_("Brand") + ":Link/Brand:100",
# 		_("Description") + "::200",
# 		_("Warehouse") + "::150",
# 		_("Section") + ":Link/Warehouse:150",
# 		_("Stock UOM") + ":Link/UOM:100",
# 		{"label": _("Incoming Rate"), "fieldtype": "Currency", "width": 110,
# 			"options": "Company:company:default_currency"},
# 		{"label": _("Balance Value"), "fieldtype": "Currency", "width": 110,
# 			"options": "Company:company:default_currency"}
# 	]
#
# 	return columns
#
# def get_stock_ledger_entries(filters):
# 	return frappe.db.sql("""select concat_ws(" ", sle.posting_date, sle.posting_time) as date,
# 			sle.item_code,
# 			whs.parent_warehouse_rss,whs.parent_section_rss,whs.parent_warehouse,
# 			sle.warehouse,sle.warehouse, sle.actual_qty, sle.qty_after_transaction, sle.incoming_rate, sle.valuation_rate,
# 			sle.stock_value, sle.voucher_type, sle.voucher_no
# 		from `tabStock Ledger Entry` sle inner join `tabWarehouse` whs
# 		on sle.warehouse = whs.name
# 		where sle.company = %(company)s and
# 			sle.posting_date between %(from_date)s and %(to_date)s
# 			{sle_conditions}
# 			order by sle.posting_date asc, sle.posting_time asc, sle.name asc"""\
# 		.format(sle_conditions=get_sle_conditions(filters)), filters, as_dict=1)
#
# def get_item_details(filters):
# 	item_details = {}
# 	for item in frappe.db.sql("""select name, item_name, description, item_group,
# 			brand, stock_uom from `tabItem` item {item_conditions}"""\
# 			.format(item_conditions=get_item_conditions(filters)), filters, as_dict=1):
# 		item_details.setdefault(item.name, item)
#
# 	return item_details
#
# def get_item_conditions(filters):
# 	conditions = []
# 	if filters.get("item_code"):
# 		conditions.append("item.name=%(item_code)s")
# 	if filters.get("brand"):
# 		conditions.append("item.brand=%(brand)s")
# 	if filters.get("item_group"):
# 		conditions.append(get_item_group_condition(filters.get("item_group")))
#
# 	return "where {}".format(" and ".join(conditions)) if conditions else ""
#
# def get_sle_conditions(filters):
# 	conditions = []
# 	item_conditions=get_item_conditions(filters)
# 	if item_conditions:
# 		conditions.append("""sle.item_code in (select item.name from tabItem item
# 			{item_conditions})""".format(item_conditions=item_conditions))
# 	if filters.get("warehouse"):
# 		warehouse_condition = get_warehouse_condition(filters.get("warehouse"))
# 		if warehouse_condition:
# 			conditions.append(warehouse_condition)
#
# 	if filters.get("section"):
# 		warehouse_condition = get_warehouse_condition(filters.get("section"))
# 		if warehouse_condition:
# 			conditions.append(warehouse_condition)
#
# 	if filters.get("location"):
# 		warehouse_condition = get_warehouse_condition(filters.get("location"))
# 		if warehouse_condition:
# 			conditions.append(warehouse_condition)
#
# 	if filters.get("voucher_no"):
# 		conditions.append("voucher_no=%(voucher_no)s")
#
# 	return "and {}".format(" and ".join(conditions)) if conditions else ""
#
# def get_opening_balance(filters, columns):
# 	if not (filters.item_code and filters.warehouse and filters.from_date):
# 		return
#
# 	from erpnext.stock.stock_ledger import get_previous_sle
# 	last_entry = get_previous_sle({
# 		"item_code": filters.item_code,
# 		"warehouse_condition": get_warehouse_condition(filters.warehouse),
# 		"posting_date": filters.from_date,
# 		"posting_time": "00:00:00"
# 	})
# 	row = [""]*len(columns)
# 	row[1] = _("'Opening'")
# 	for i, v in ((9, 'qty_after_transaction'), (11, 'valuation_rate'), (12, 'stock_value')):
# 			row[i] = last_entry.get(v, 0)
#
# 	return row
#
# def get_warehouse_condition(warehouse):
# 	warehouse_details = frappe.db.get_value("Warehouse", warehouse, ["lft", "rgt"], as_dict=1)
# 	if warehouse_details:
# 		return " exists (select name from `tabWarehouse` wh \
# 			where wh.lft >= %s and wh.rgt <= %s and warehouse = wh.name)"%(warehouse_details.lft,
# 			warehouse_details.rgt)
#
# 	return ''
#
# def get_item_group_condition(item_group):
# 	item_group_details = frappe.db.get_value("Item Group", item_group, ["lft", "rgt"], as_dict=1)
# 	if item_group_details:
# 		return "item.item_group in (select ig.name from `tabItem Group` ig \
# 			where ig.lft >= %s and ig.rgt <= %s and item.item_group = ig.name)"%(item_group_details.lft,
# 			item_group_details.rgt)
#
# 	return ''
