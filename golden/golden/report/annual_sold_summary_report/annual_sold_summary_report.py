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
	sl_entries = frappe.db.sql("""select * from `tabReceive Order` where docstatus = '1' %s""" % conditions, as_dict=1)
	for cl in sl_entries:
		qty_pack = frappe.db.sql("""select sum(qty) from `tabReceive Order Item` where parent = %s""", cl.name)[0][0]
		qty_ro = frappe.db.sql("""select sum(stock_qty) from `tabReceive Order Item` where parent = %s""", cl.name)[0][0]
		qty_sold = frappe.db.sql("""select sum(used_qty) from `tabReceive Order Item` where parent = %s""", cl.name)[0][0]
		percen_sold = (flt(qty_sold) / flt(qty_ro)) * 100
		# qty_1 = frappe.db.sql("""select sum(qty) from `tabReceive Order Item Delivery` where parent = %s and delivery_date like '%s'""", (cl.name, frappe.db.escape(filters["year"])+"-01%")[0][0]
		jan = frappe.db.escape(filters["year"])+"-01%"
		qty_1 = frappe.db.sql("""select sum(qty) from `tabReceive Order Item Delivery` where parent = %s and delivery_date like %s""", (cl.name, jan))[0][0]
		feb = frappe.db.escape(filters["year"])+"-02%"
		qty_2 = frappe.db.sql("""select sum(qty) from `tabReceive Order Item Delivery` where parent = %s and delivery_date like %s""", (cl.name, feb))[0][0]
		mar = frappe.db.escape(filters["year"])+"-03%"
		qty_3 = frappe.db.sql("""select sum(qty) from `tabReceive Order Item Delivery` where parent = %s and delivery_date like %s""", (cl.name, mar))[0][0]
		apr = frappe.db.escape(filters["year"])+"-04%"
		qty_4 = frappe.db.sql("""select sum(qty) from `tabReceive Order Item Delivery` where parent = %s and delivery_date like %s""", (cl.name, apr))[0][0]
		may = frappe.db.escape(filters["year"])+"-05%"
		qty_5 = frappe.db.sql("""select sum(qty) from `tabReceive Order Item Delivery` where parent = %s and delivery_date like %s""", (cl.name, may))[0][0]
		jun = frappe.db.escape(filters["year"])+"-06%"
		qty_6 = frappe.db.sql("""select sum(qty) from `tabReceive Order Item Delivery` where parent = %s and delivery_date like %s""", (cl.name, jun))[0][0]
		jul = frappe.db.escape(filters["year"])+"-07%"
		qty_7 = frappe.db.sql("""select sum(qty) from `tabReceive Order Item Delivery` where parent = %s and delivery_date like %s""", (cl.name, jul))[0][0]
		aug = frappe.db.escape(filters["year"])+"-08%"
		qty_8 = frappe.db.sql("""select sum(qty) from `tabReceive Order Item Delivery` where parent = %s and delivery_date like %s""", (cl.name, aug))[0][0]
		sep = frappe.db.escape(filters["year"])+"-09%"
		qty_9 = frappe.db.sql("""select sum(qty) from `tabReceive Order Item Delivery` where parent = %s and delivery_date like %s""", (cl.name, sep))[0][0]
		okt = frappe.db.escape(filters["year"])+"-10%"
		qty_10 = frappe.db.sql("""select sum(qty) from `tabReceive Order Item Delivery` where parent = %s and delivery_date like %s""", (cl.name, okt))[0][0]
		nov = frappe.db.escape(filters["year"])+"-11%"
		qty_11 = frappe.db.sql("""select sum(qty) from `tabReceive Order Item Delivery` where parent = %s and delivery_date like %s""", (cl.name, nov))[0][0]
		dec = frappe.db.escape(filters["year"])+"-12%"
		qty_12 = frappe.db.sql("""select sum(qty) from `tabReceive Order Item Delivery` where parent = %s and delivery_date like %s""", (cl.name, dec))[0][0]
		data.append([cl.posting_date, cl.name, cl.expedition, cl.container, qty_pack, qty_ro, qty_sold, percen_sold, qty_1, qty_2, qty_3, qty_4, qty_5, qty_6, qty_7, qty_8, qty_9, qty_10, qty_11, qty_12])
		# january


	return columns, data

def get_columns():
	"""return columns"""

	columns = [
		_("Date Received")+":Date:100",
		_("RO ID")+":Link/Receive Order:140",
		_("Expedition")+":Link/Expedition:150",
		_("No Container")+":Data:120",
		_("Packages")+":Int:70",
		_("Qty RO")+":Int:70",
		_("Qty Sold")+":Int:70",
		_("Sold (%)")+":Percent:70",
		_("Jan")+":Int:60",
		_("Feb")+":Int:60",
		_("Mar")+":Int:60",
		_("Apr")+":Int:60",
		_("May")+":Int:60",
		_("Jun")+":Int:60",
		_("Jul")+":Int:60",
		_("Aug")+":Int:60",
		_("Sep")+":Int:60",
		_("Oct")+":Int:60",
		_("Nov")+":Int:60",
		_("Dec")+":Int:60",
	]

	return columns

def get_conditions(filters):
	conditions = ""
	if filters.get("year"):
		conditions += " and posting_date >= '%s-01-01'" % frappe.db.escape(filters["year"])
		conditions += " and posting_date <= '%s-12-31'" % frappe.db.escape(filters["year"])
	return conditions
