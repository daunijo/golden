# Copyright (c) 2013, RSS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
	columns = get_columns()
	data = []

	conditions = get_conditions(filters)
	vouchers = get_voucher(filters)
	if vouchers == "All":
		sl_entries = frappe.db.sql("""select concat_ws(' ', sle.posting_date, sle.posting_time) as date, sle.`name`, sle.item_code, sle.actual_qty, sle.qty_after_transaction, sle.warehouse as location, s.parent_warehouse as section, w.parent_warehouse, sle.valuation_rate, sle.voucher_type, sle.voucher_no, i.stock_uom, sle.voucher_detail_no from `tabStock Ledger Entry` sle inner join `tabWarehouse` s on sle.warehouse = s.`name` inner join `tabWarehouse` w on s.parent_warehouse = w.`name` inner join `tabItem` i on sle.item_code = i.item_code where sle.docstatus = '1' %s order by date asc""" % conditions, as_dict=1)
	elif vouchers == "Transfer Order":
		sl_entries = frappe.db.sql("""select concat_ws(' ', sle.posting_date, sle.posting_time) as date, sle.`name`, sle.item_code, sle.actual_qty, sle.qty_after_transaction, sle.warehouse as location, s.parent_warehouse as section, w.parent_warehouse, sle.valuation_rate, sle.voucher_type, sle.voucher_no, i.stock_uom, sle.voucher_detail_no from `tabStock Ledger Entry` sle inner join `tabWarehouse` s on sle.warehouse = s.`name` inner join `tabWarehouse` w on s.parent_warehouse = w.`name` inner join `tabItem` i on sle.item_code = i.item_code inner join `tabStock Entry` se on se.`name` = sle.voucher_no where sle.docstatus = '1' %s and se.purpose = 'Material Transfer' order by date asc""" % conditions, as_dict=1)
	elif vouchers == "Sales Return":
		sl_entries = frappe.db.sql("""select concat_ws(' ', sle.posting_date, sle.posting_time) as date, sle.`name`, sle.item_code, sle.actual_qty, sle.qty_after_transaction, sle.warehouse as location, s.parent_warehouse as section, w.parent_warehouse, sle.valuation_rate, sle.voucher_type, sle.voucher_no, i.stock_uom, sle.voucher_detail_no from `tabStock Ledger Entry` sle inner join `tabWarehouse` s on sle.warehouse = s.`name` inner join `tabWarehouse` w on s.parent_warehouse = w.`name` inner join `tabItem` i on sle.item_code = i.item_code inner join `tabStock Entry` se on se.`name` = sle.voucher_no where sle.docstatus = '1' %s and se.purpose = 'Material Receipt' order by date asc""" % conditions, as_dict=1)
	elif vouchers == "Purchase Return":
		sl_entries = frappe.db.sql("""select concat_ws(' ', sle.posting_date, sle.posting_time) as date, sle.`name`, sle.item_code, sle.actual_qty, sle.qty_after_transaction, sle.warehouse as location, s.parent_warehouse as section, w.parent_warehouse, sle.valuation_rate, sle.voucher_type, sle.voucher_no, i.stock_uom, sle.voucher_detail_no from `tabStock Ledger Entry` sle inner join `tabWarehouse` s on sle.warehouse = s.`name` inner join `tabWarehouse` w on s.parent_warehouse = w.`name` inner join `tabItem` i on sle.item_code = i.item_code inner join `tabStock Entry` se on se.`name` = sle.voucher_no where sle.docstatus = '1' %s and se.purpose = 'Material Issue' order by date asc""" % conditions, as_dict=1)
	elif vouchers == "Delivery Order":
		sl_entries = frappe.db.sql("""select concat_ws(' ', sle.posting_date, sle.posting_time) as date, sle.`name`, sle.item_code, sle.actual_qty, sle.qty_after_transaction, sle.warehouse as location, s.parent_warehouse as section, w.parent_warehouse, sle.valuation_rate, sle.voucher_type, sle.voucher_no, i.stock_uom, sle.voucher_detail_no from `tabStock Ledger Entry` sle inner join `tabWarehouse` s on sle.warehouse = s.`name` inner join `tabWarehouse` w on s.parent_warehouse = w.`name` inner join `tabItem` i on sle.item_code = i.item_code where sle.docstatus = '1' %s and sle.voucher_type = 'Delivery Note' order by date asc""" % conditions, as_dict=1)
	elif vouchers == "Stock Reconciliation":
		sl_entries = frappe.db.sql("""select concat_ws(' ', sle.posting_date, sle.posting_time) as date, sle.`name`, sle.item_code, sle.actual_qty, sle.qty_after_transaction, sle.warehouse as location, s.parent_warehouse as section, w.parent_warehouse, sle.valuation_rate, sle.voucher_type, sle.voucher_no, i.stock_uom, sle.voucher_detail_no from `tabStock Ledger Entry` sle inner join `tabWarehouse` s on sle.warehouse = s.`name` inner join `tabWarehouse` w on s.parent_warehouse = w.`name` inner join `tabItem` i on sle.item_code = i.item_code where sle.docstatus = '1' %s and sle.voucher_type = 'Stock Reconciliation' order by date asc""" % conditions, as_dict=1)
	elif vouchers == "Receive Order":
		sl_entries = frappe.db.sql("""select concat_ws(' ', sle.posting_date, sle.posting_time) as date, sle.`name`, sle.item_code, sle.actual_qty, sle.qty_after_transaction, sle.warehouse as location, s.parent_warehouse as section, w.parent_warehouse, sle.valuation_rate, sle.voucher_type, sle.voucher_no, i.stock_uom, sle.voucher_detail_no from `tabStock Ledger Entry` sle inner join `tabWarehouse` s on sle.warehouse = s.`name` inner join `tabWarehouse` w on s.parent_warehouse = w.`name` inner join `tabItem` i on sle.item_code = i.item_code where sle.docstatus = '1' %s and sle.voucher_type = 'Purchase Receipt' order by date asc""" % conditions, as_dict=1)
	for cl in sl_entries:
		item_name = frappe.db.get_value("Item", cl.item_code, "item_name")
		if cl.voucher_type == "Stock Reconciliation":
			qty = cl.qty_after_transaction
		else:
			qty = cl.actual_qty

		if cl.voucher_type == "Delivery Note":
			vt = "Delivery Order"
			pc = frappe.db.get_value("Delivery Note", cl.voucher_no, "packing")
			vn = frappe.db.get_value("Delivery Order Detail", {"packing": pc, "docstatus": 1}, "parent")
			sod = frappe.db.get_value("Delivery Note Item", cl.voucher_detail_no, "so_detail")
			soi = frappe.db.get_value("Sales Order Item", sod, ["price_list_rate", "discount_percentage", "parent"], as_dict=1)
			so = frappe.db.get_value("Sales Order", soi.parent, ["selling_price_list", "customer"], as_dict=1)
			rate = soi.price_list_rate
			discount = soi.discount_percentage
			pricelist = so.selling_price_list
			customer = so.customer
		elif cl.voucher_type == "Purchase Receipt":
			vt = "Receive Order"
			vn = frappe.db.get_value("Purchase Receipt", cl.voucher_no, "receive_order")
			rate = ""
			discount = ""
			pricelist = ""
			customer = ""
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
			rate = ""
			discount = ""
			pricelist = ""
			customer = ""
		else:
			vt = cl.voucher_type
			vn = cl.voucher_no
			rate = ""
			discount = ""
			pricelist = ""
			customer = ""

		data.append([cl.date, cl.item_code, item_name, cl.location, qty, cl.qty_after_transaction, vt, vn, cl.stock_uom, rate, discount, pricelist, customer])

	return columns, data

def get_columns():
	"""return columns"""

	columns = [
		_("Date") + ":Datetime:95",
		_("Item") + ":Link/Item:130",
		_("Item Name") + "::200",
		_("Location") + ":Link/Warehouse:150",
		_("Qty") + ":Float:50",
		_("Balance Qty") + ":Float:80",
		_("Voucher Type") + "::125",
		_("Voucher #") + ":Dynamic Link/" + _("Voucher Type") + ":100",
		_("Stock UOM") + ":Link/UOM:80",
		_("Price List Rate") + ":Float:100",
		_("Discount") + ":Percent:60",
		_("Price List") + ":Link/Price List:120",
		_("Customer") + ":Link/Customer:150",
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
	if filters.get("warehouse"):
		conditions += " and w.parent_warehouse = '%s'" % frappe.db.escape(filters["warehouse"])
	if filters.get("section"):
		conditions += " and s.parent_warehouse = '%s'" % frappe.db.escape(filters["section"])
	if filters.get("location"):
		conditions += " and sle.warehouse = '%s'" % frappe.db.escape(filters["location"])
	if filters.get("item_code"):
		conditions += " and sle.item_code = '%s'" % frappe.db.escape(filters["item_code"])
	if filters.get("item_group"):
		conditions += " and i.item_group = '%s'" % frappe.db.escape(filters["item_group"])
	if filters.get("brand"):
		conditions += " and i.brand = '%s'" % frappe.db.escape(filters["brand"])
	# if filters.get("voucher_no"):
	# 	conditions += " and item_code like '%%%s%%'" % frappe.db.escape(filters["voucher_no"])
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
