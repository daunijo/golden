# Copyright (c) 2013, RSS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt

def execute(filters=None):
	columns = get_columns()
	data = []

	conditions = get_conditions(filters)
	vouchers = get_voucher(filters)
	price_list = get_price_list(filters)
	stock_fil = get_stock(filters)
	stock_all = 0
	stock_all = flt(stock_all) + flt(stock_fil)
	sl_entries = frappe.db.sql("""select concat_ws(" ",sle.posting_date,sle.posting_time) as date, sle.item_code, i.item_name, sle.voucher_type, sle.voucher_no, sle.voucher_detail_no, sle.actual_qty, sle.qty_after_transaction, sle.warehouse, sle.stock_uom, sle.stock_value_difference, sle.valuation_rate from `tabStock Ledger Entry` sle inner join `tabItem` i on i.item_code = sle.item_code where sle.docstatus = '1' %s order by date asc""" % conditions, as_dict=1)
	for cl in sl_entries:
		if cl.voucher_type == "Stock Reconciliation":
			qty = cl.qty_after_transaction
			# qty_diff = flt(cl.stock_value_difference) / flt(cl.valuation_rate)
			# qty_diff = flt(cl.actual_qty)
			stock_all = flt(stock_all) + flt(qty)
		else:
			qty = cl.actual_qty
			stock_all = flt(stock_all) + flt(cl.actual_qty)

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
			pr_rate = ""
			pr_disc = ""
		elif cl.voucher_type == "Purchase Receipt":
			vt = "Receive Order"
			vn = frappe.db.get_value("Purchase Receipt", cl.voucher_no, "receive_order")
			rate = ""
			discount = ""
			pricelist = ""
			customer = ""
			pr_rate = frappe.db.get_value("Purchase Receipt Item", cl.voucher_detail_no, "rate")
			pr_disc = frappe.db.get_value("Purchase Receipt Item", cl.voucher_detail_no, "discount_percentage")
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
			pr_rate = ""
			pr_disc = ""
		else:
			vt = cl.voucher_type
			vn = cl.voucher_no
			rate = ""
			discount = ""
			pricelist = ""
			customer = ""
			pr_rate = ""
			pr_disc = ""

		if price_list != "":
			pl = frappe.db.get_value("Item Price", {"price_list": price_list, "item_code": cl.item_code}, "price_list_rate")
		else:
			pl = 0

		loc = "<a href='/desk#query-report/Stock Card by Location?item_code="+cl.item_code+"&location="+cl.warehouse+"' style='border:1px #01DF01 solid; background:#01DF01; color:#FFF'>Stock per Location</a>"

		if vouchers == "All":
			data.append([cl.date, cl.item_code, cl.item_name, cl.warehouse, qty, stock_all, cl.stock_uom, vt, vn, pl, discount, price_list, customer, pr_rate, pr_disc, loc])
		elif vouchers == vt:
			data.append([cl.date, cl.item_code, cl.item_name, cl.warehouse, qty, stock_all, cl.stock_uom, vt, vn, pl, discount, price_list, customer, pr_rate, pr_disc, loc])

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
		_("Voucher Type") + "::125",
		_("Voucher #") + ":Dynamic Link/" + _("Voucher Type") + ":100",
		_("Price List Rate") + ":Float:100",
		_("Discount") + ":Percent:60",
		_("Price List") + ":Link/Price List:120",
		_("Customer") + ":Link/Customer:150",
		_("Incoming Rate") + ":Float:100",
		_("Discount Buying") + ":Percent:60",
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

def get_price_list(filters):
	price_list = ""
	if filters.get("price_list"):
		price_list = frappe.db.escape(filters["price_list"])
	return price_list

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
