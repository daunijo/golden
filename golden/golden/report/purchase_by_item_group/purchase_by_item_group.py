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
	# bulk_po = frappe.db.get_value("Purchase Budget", frappe.db.escape(filters["purchase_budget"]), "bulk_po")
	# frappe.throw(_("select distinct(i.item_group) from `tabPurchase Order Item` poi inner join `tabItem` i on poi.item_code = i.item_code inner join `tabItem Group` ig on i.item_group = ig.`name` where poi.parent in ({0})").format(bulk_po))
	sl_entries = frappe.db.sql("select distinct(item_group), parent from `tabPurchase Budget Item` where %s order by item_group asc" % conditions, as_dict=1)
	for cl in sl_entries:
		total = frappe.db.sql("select sum(net_amount) from `tabPurchase Budget Item` where item_group = %s and parent = %s", (cl.item_group, cl.parent))[0][0]
		total2 = frappe.db.sql("select sum(net_amount) from `tabPurchase Budget Item` where parent = %s", cl.parent)[0][0]
		percen = flt(total) / flt(total2) * 100
		data.append([cl.item_group, total, percen])

	return columns, data

def get_columns():
	"""return columns"""

	columns = [
		_("Item Group")+":Link/Item Group:200",
		_("Total")+":Float:120",
		_("Kontribusi")+":Percent:100",
	]

	return columns

def get_conditions(filters):
	conditions = ""
	if filters.get("purchase_budget"):
		conditions += " parent = '%s'" % frappe.db.escape(filters["purchase_budget"])
	return conditions
