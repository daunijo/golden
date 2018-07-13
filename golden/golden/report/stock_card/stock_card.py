# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
	columns = get_columns()
	sl_entries = get_stock_ledger_entries(filters)
	item_details = get_item_details(filters)
	opening_row = get_opening_balance(filters, columns)

	data = []

	if opening_row:
		data.append(opening_row)

	for sle in sl_entries:
		item_detail = item_details[sle.item_code]
		if sle.voucher_type == "Stock Entry":
			custom_voucher_type = "Transfer Order"
			custom_voucher_no = frappe.db.get_value("Stock Entry", sle.voucher_no, "transfer_order")
		elif sle.voucher_type == "Delivery Note":
			custom_voucher_type = "Packing"
			custom_voucher_no = frappe.db.get_value("Delivery Note", sle.voucher_no, "packing")
		else:
			custom_voucher_type = sle.voucher_type
			custom_voucher_no = sle.voucher_no
		data.append([sle.date,
			sle.item_code,
			item_detail.item_name,
			sle.warehouse,
			sle.actual_qty,
			sle.qty_after_transaction,
			sle.valuation_rate,
			custom_voucher_type,
			custom_voucher_no,
			item_detail.item_group,
			item_detail.brand,
			item_detail.description,
			sle.parent_warehouse_rss,
			sle.parent_section_rss,
			item_detail.stock_uom,
			(sle.incoming_rate if sle.actual_qty > 0 else 0.0),
			sle.stock_value
			])

	return columns, data

def get_columns():
	columns = [
		_("Date") + ":Datetime:95",
		_("Item") + ":Link/Item:130",
		_("Item Name") + "::100",
		_("Location") + ":Link/Warehouse:150",
		_("Qty") + ":Float:50",
		_("Balance Qty") + ":Float:100",
		{"label": _("Valuation Rate"), "fieldtype": "Currency", "width": 110,
			"options": "Company:company:default_currency"},
		_("Voucher Type") + "::110",
		_("Voucher #") + ":Dynamic Link/" + _("Voucher Type") + ":100",
		_("Item Group") + ":Link/Item Group:100",
		_("Brand") + ":Link/Brand:100",
		_("Description") + "::200",
		_("Warehouse") + "::150",
		_("Section") + ":Link/Warehouse:150",
		_("Stock UOM") + ":Link/UOM:100",
		{"label": _("Incoming Rate"), "fieldtype": "Currency", "width": 110,
			"options": "Company:company:default_currency"},
		{"label": _("Balance Value"), "fieldtype": "Currency", "width": 110,
			"options": "Company:company:default_currency"}
	]

	return columns

def get_stock_ledger_entries(filters):
	return frappe.db.sql("""select concat_ws(" ", sle.posting_date, sle.posting_time) as date,
			sle.item_code,
			whs.parent_warehouse_rss,whs.parent_section_rss,whs.parent_warehouse,
			sle.warehouse,sle.warehouse, sle.actual_qty, sle.qty_after_transaction, sle.incoming_rate, sle.valuation_rate,
			sle.stock_value, sle.voucher_type, sle.voucher_no
		from `tabStock Ledger Entry` sle inner join `tabWarehouse` whs
		on sle.warehouse = whs.name
		where sle.company = %(company)s and
			sle.posting_date between %(from_date)s and %(to_date)s
			{sle_conditions}
			order by sle.posting_date asc, sle.posting_time asc, sle.name asc"""\
		.format(sle_conditions=get_sle_conditions(filters)), filters, as_dict=1)

def get_item_details(filters):
	item_details = {}
	for item in frappe.db.sql("""select name, item_name, description, item_group,
			brand, stock_uom from `tabItem` item {item_conditions}"""\
			.format(item_conditions=get_item_conditions(filters)), filters, as_dict=1):
		item_details.setdefault(item.name, item)

	return item_details

def get_item_conditions(filters):
	conditions = []
	if filters.get("item_code"):
		conditions.append("item.name=%(item_code)s")
	if filters.get("brand"):
		conditions.append("item.brand=%(brand)s")
	if filters.get("item_group"):
		conditions.append(get_item_group_condition(filters.get("item_group")))

	return "where {}".format(" and ".join(conditions)) if conditions else ""

def get_sle_conditions(filters):
	conditions = []
	item_conditions=get_item_conditions(filters)
	if item_conditions:
		conditions.append("""sle.item_code in (select item.name from tabItem item
			{item_conditions})""".format(item_conditions=item_conditions))
	if filters.get("warehouse"):
		warehouse_condition = get_warehouse_condition(filters.get("warehouse"))
		if warehouse_condition:
			conditions.append(warehouse_condition)

	if filters.get("section"):
		warehouse_condition = get_warehouse_condition(filters.get("section"))
		if warehouse_condition:
			conditions.append(warehouse_condition)

	if filters.get("location"):
		warehouse_condition = get_warehouse_condition(filters.get("location"))
		if warehouse_condition:
			conditions.append(warehouse_condition)

	if filters.get("voucher_no"):
		conditions.append("voucher_no=%(voucher_no)s")

	return "and {}".format(" and ".join(conditions)) if conditions else ""

def get_opening_balance(filters, columns):
	if not (filters.item_code and filters.warehouse and filters.from_date):
		return

	from erpnext.stock.stock_ledger import get_previous_sle
	last_entry = get_previous_sle({
		"item_code": filters.item_code,
		"warehouse_condition": get_warehouse_condition(filters.warehouse),
		"posting_date": filters.from_date,
		"posting_time": "00:00:00"
	})
	row = [""]*len(columns)
	row[1] = _("'Opening'")
	for i, v in ((9, 'qty_after_transaction'), (11, 'valuation_rate'), (12, 'stock_value')):
			row[i] = last_entry.get(v, 0)

	return row

def get_warehouse_condition(warehouse):
	warehouse_details = frappe.db.get_value("Warehouse", warehouse, ["lft", "rgt"], as_dict=1)
	if warehouse_details:
		return " exists (select name from `tabWarehouse` wh \
			where wh.lft >= %s and wh.rgt <= %s and warehouse = wh.name)"%(warehouse_details.lft,
			warehouse_details.rgt)

	return ''

def get_item_group_condition(item_group):
	item_group_details = frappe.db.get_value("Item Group", item_group, ["lft", "rgt"], as_dict=1)
	if item_group_details:
		return "item.item_group in (select ig.name from `tabItem Group` ig \
			where ig.lft >= %s and ig.rgt <= %s and item.item_group = ig.name)"%(item_group_details.lft,
			item_group_details.rgt)

	return ''
