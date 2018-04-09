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
	sl_entries = frappe.db.sql("""select `name`, item_code, item_name, item_group from `tabItem` where disabled = '0' and is_stock_item = '1' %s""" % conditions, as_dict=1)
	for cl in sl_entries:
		bin = []
		count_1 = frappe.db.sql("""select count(*) from `tabPurchase Order` po inner join `tabPurchase Order Item` poi on po.`name` = poi.parent where po.`status` in ('To Receive and Bill', 'To Receive') and po.docstatus = '1' and poi.item_code = %s""", cl.name)[0][0]
		count_2 = frappe.db.sql("""select count(*) from `tabSales Order` so inner join `tabSales Order Item` soi on so.`name` = soi.parent where so.`status` in ('To Deliver and Bill', 'To Deliver') and so.docstatus = '1' and soi.item_code = %s""", cl.name)[0][0]
		count_3 = frappe.db.sql("""select count(*) from `tabBin` where item_code = %s""", cl.name)[0][0]
		if count_1 == 0 and count_2 == 0 and count_3 == 0:
			count = 1
		else:
			if count_1 >= count_2 and count_1 >= count_3:
				count = count_1
			elif count_2 >= count_1 and count_2 >= count_3:
				count = count_2
			else:
				count = count_3
		for q in range(0,count):
			i = flt(q)+1
			if q == 0:
				item_code = cl.item_code
				item_name = cl.item_name
				item_group = cl.item_group
				count_last_receipt = frappe.db.sql("""select count(*) from `tabPurchase Receipt` pr inner join `tabPurchase Receipt Item` pri where pr.docstatus = '1' and pri.item_code = %s""", cl.item_code)[0][0]
				if flt(count_last_receipt) == 1:
					last_receipt = frappe.db.sql("""select pr.posting_date from `tabPurchase Receipt` pr inner join `tabPurchase Receipt Item` pri where pr.docstatus = '1' and pri.item_code = %s order by pr.posting_date desc limit 1""", cl.item_code)[0][0]
				else:
					last_receipt = ""
				purchase_pl = frappe.db.sql("""select `name` from `tabPrice List` where enabled = '1' and buying = '1'""")[0][0]
				selling_pl = frappe.db.sql("""select `name` from `tabPrice List` where enabled = '1' and selling = '1'""")[0][0]
				projected_qty = frappe.db.sql("""select sum(projected_qty) from `tabBin` where item_code = %s""", cl.item_code)[0][0]
				available_qty = frappe.db.sql("""select sum(actual_qty - reserved_qty) from `tabBin` where item_code = %s""", cl.item_code)[0][0]
			else:
				item_code = ""
				item_name = ""
				item_group = ""
				last_receipt = ""
				purchase_pl = ""
				selling_pl = ""
				projected_qty = ""
				available_qty = ""
			if flt(q) < flt(count_1):
				po = frappe.db.sql("""select po.`name`, poi.qty, poi.uom, poi.schedule_date from `tabPurchase Order` po inner join `tabPurchase Order Item` poi on po.`name` = poi.parent where po.`status` in ('To Receive and Bill', 'To Receive') and po.docstatus = '1' and poi.item_code = %s order by po.`name` asc limit %s,%s""", (cl.name, q, i))
				po_name = po[0][0]
				po_qty = po[0][1]
				po_uom = po[0][2]
				po_eta = po[0][3]
			else:
				po_name = ""
				po_qty = ""
				po_uom = ""
				po_eta = ""
			if flt(q) < flt(count_2):
				so = frappe.db.sql("""select so.`name`, soi.qty, soi.uom from `tabSales Order` so inner join `tabSales Order Item` soi on so.`name` = soi.parent where so.`status` in ('To Deliver and Bill', 'To Deliver') and so.docstatus = '1' and soi.item_code = %s order by so.`name` asc limit %s,%s""", (cl.name, q, i))
				so_name = so[0][0]
				so_qty = so[0][1]
				so_uom = so[0][2]
			else:
				so_name = ""
				so_qty = ""
				so_uom = ""
			if flt(q) < flt(count_3):
				desc = ', '.join(bin)
				cek = frappe.db.sql("""select `name` from `tabBin` where item_code = %s and `name` not in (%s) order by warehouse asc limit 1""", (cl.name, desc))[0][0]
				bin.append(cek)
				wh = frappe.db.sql("""select warehouse, actual_qty, stock_uom from `tabBin` where `name` = %s""", cek)
				location = wh[0][0]
				# section = frappe.db.sql("""select parent from `tabWarehouse` where `name` = %s""", location)[0][0]
				# warehouse = frappe.db.sql("""select parent from `tabWarehouse` where `name` = %s""", section)[0][0]
				# actual_qty = wh[0][1]
				# bin_uom = wh[0][2]
				section = ""
				warehouse = ""
				actual_qty = ""
				bin_uom = ""
				test = desc
			else:
				location = ""
				section = ""
				warehouse = ""
				actual_qty = ""
				bin_uom = ""
				test = "nol"
			data.append([item_code, item_name, item_group, po_name, po_qty, po_uom, po_eta, last_receipt, purchase_pl, so_name, so_qty, so_uom, selling_pl, warehouse, section, location, actual_qty, projected_qty, available_qty, bin_uom, test])

	return columns, data

def get_columns():
	"""return columns"""

	columns = [
		_("Item ID")+":Link/Item:110",
		_("Item Name")+":Data:110",
		_("Item Group")+":Data:110",
		_("PO No.")+":Link/Purchase Order:110",
		_("PO Qty")+":Float:70",
		_("PO UOM")+":Link/UOM:70",
		_("PO ETA Date")+":Date:90",
		_("Last Receipt Date")+":Date:120",
		_("Purchase Price List")+":Link/Price List:120",
		_("SO No.")+":Link/Sales Order:110",
		_("SO Qty")+":Float:70",
		_("SO UOM")+":Link/UOM:70",
		_("Selling Price List")+":Link/Price List:120",
		_("Warehouse")+":Link/Warehouse:150",
		_("Section")+":Link/Warehouse:150",
		_("Location")+":Link/Warehouse:150",
		_("Actual Qty")+":Float:80",
		_("Projected Qty")+":Float:90",
		_("Available Qty")+":Float:90",
		_("UOM")+":Link/UOM:70",
		_("Test")+":Data:700",
	]

	return columns

def get_conditions(filters):
	conditions = ""

	return conditions
