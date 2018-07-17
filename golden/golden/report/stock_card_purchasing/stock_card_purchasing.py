# Copyright (c) 2013, RSS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
	columns = get_columns()
	data = []

	conditions = get_conditions(filters)
	sl_entries = frappe.db.sql("""select concat_ws(" ", sle.posting_date, sle.posting_time) as date, sle.`name`, sle.item_code, sle.actual_qty, sle.qty_after_transaction, sle.warehouse as location, s.parent_warehouse as section, w.parent_warehouse, sle.valuation_rate, sle.voucher_type, sle.voucher_no, i.stock_uom, sle.voucher_detail_no from `tabStock Ledger Entry` sle inner join `tabWarehouse` s on sle.warehouse = s.`name` inner join `tabWarehouse` w on s.parent_warehouse = w.`name` inner join `tabItem` i on sle.item_code = i.item_code where sle.docstatus = '1' %s order by date asc""" % conditions, as_dict=1)
	for cl in sl_entries:
		item_name = frappe.db.get_value("Item", cl.item_code, "item_name")
		if cl.voucher_type == "Stock Reconciliation":
			qty = cl.qty_after_transaction
		else:
			qty = cl.actual_qty

		if cl.voucher_type == "Stock Entry":
			vt = "Transfer Order"
			vn = frappe.db.get_value("Stock Entry", cl.voucher_no, "transfer_order")
			rate = ""
			discount = ""
			supplier = ""
		elif cl.voucher_type == "Delivery Note":
			vt = "Delivery Order"
			pc = frappe.db.get_value("Delivery Note", cl.voucher_no, "packing")
			vn = frappe.db.get_value("Delivery Order Detail", {"packing": pc, "docstatus": 1}, "parent")
			rate = ""
			discount = ""
			supplier = ""
		elif cl.voucher_type == "Purchase Receipt":
			vt = "Receive Order"
			vn = frappe.db.get_value("Purchase Receipt", cl.voucher_no, "receive_order")
			pod = frappe.db.get_value("Purchase Receipt Item", cl.voucher_detail_no, "purchase_order_item")
			poi = frappe.db.get_value("Purchase Order Item", pod, ["price_list_rate", "discount_percentage", "parent"], as_dict=1)
			po = frappe.db.get_value("Purchase Order", poi.parent, "supplier")
			rate = poi.price_list_rate
			discount = poi.discount_percentage
			supplier = po
		else:
			vt = cl.voucher_type
			vn = cl.voucher_no
			rate = ""
			discount = ""
			supplier = ""

		data.append([cl.date, cl.item_code, item_name, cl.location, qty, cl.qty_after_transaction, cl.valuation_rate, vt, vn, cl.stock_uom, rate, discount, supplier])

	return columns, data

def get_columns():
	"""return columns"""

	columns = [
		_("Date") + ":Datetime:95",
		_("Item") + ":Link/Item:130",
		_("Item Name") + "::150",
		_("Location") + ":Link/Warehouse:150",
		_("Qty") + ":Float:50",
		_("Balance Qty") + ":Float:80",
		{"label": _("Valuation Rate"), "fieldtype": "Currency", "width": 110, "options":"Company:company:default_currency"},
		_("Voucher Type") + "::125",
		_("Voucher #") + ":Dynamic Link/" + _("Voucher Type") + ":100",
		_("Stock UOM") + ":Link/UOM:80",
		_("Price List Rate") + ":Float:80",
		_("Discount") + ":Percent:60",
		_("Supplier") + ":Link/Supplier:150",
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
	if filters.get("voucher_type") and filters.get("voucher_type") != 'All':
		if filters.get("voucher_type") == "Transfer Order":
			conditions += " and sle.voucher_type = 'Stock Entry'"
		elif filters.get("voucher_type") == "Delivery Order":
			conditions += " and sle.voucher_type = 'Delivery Note'"
		elif filters.get("voucher_type") == "Receive Order":
			conditions += " and sle.voucher_type = 'Purchase Receipt'"
		else:
			conditions += " and sle.voucher_type = '%s'" % frappe.db.escape(filters["voucher_type"])

	# if filters.get("voucher_no"):
	# 	conditions += " and item_code like '%%%s%%'" % frappe.db.escape(filters["voucher_no"])
	return conditions
