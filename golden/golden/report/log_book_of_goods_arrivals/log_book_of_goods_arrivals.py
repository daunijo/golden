# Copyright (c) 2013, molie and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import cint, flt, cstr
from frappe import _

def execute(filters=None):
	if not filters: filters = {}

	columns = get_columns()
	data = []

	conditions = get_conditions(filters)

	purchase_order = frappe.db.sql("""select name,transaction_date,supplier from `tabPurchase Order` where docstatus = '1' order by name asc, transaction_date desc""", as_dict=1)
	for d in purchase_order: #looping master
		count_po = frappe.db.sql("""select count(*) from `tabPurchase Order Item` where parent = %s and docstatus = 1 order by parent asc, item_code asc""", d.name)[0][0]
		count_ro = frappe.db.sql("""select count(*) from `tabReceive Order Item` where purchase_order = %s and docstatus =1 order by parent asc, item_code asc""", d.name)[0][0]

		#count_pow = frappe.db.sql("""select count(*) from `tabPurchase Order Item` where parent = %s order by parent asc,item_code asc""",d.name)[0][0]
		#no = 1

		for x in range(0,count_ro): #range dari 0 s/d jumlah dari count_po #looping transaksi
		  y = flt(x)+1
		  if flt(x) < flt(count_po):
		   items = frappe.db.sql("""
		  		select
					distinct(name)
				from
					`tabPurchase Order Item`
				where
					parent = %s and docstatus = 1
				order by
					item_code asc limit %s,%s """, (d.name, x, y))[0][0]

		  #detail purchase order
		   det = frappe.db.get_value("Purchase Order Item", items, ["item_code", "item_name", "qty","rate","amount"], as_dict=1)
		   namepo = d.name
		   datepo = d.transaction_date
		   supppo = d.supplier
		   codepox = det.item_code
		   qtypox = det.qty
		   uompox = det.uom
		   ratepox = det.rate
		   amountpox = det.amount
		   itempox = det.item_name


			#quote = frappe.db.sql("""select distinct(qo.`name`) from `tabPurchase Order Item` qi inner join `tabPurchase Order` qo on qi.parent = qo.`name` where qi.parent = %s and qo.docstatus != '2' order by qo.`name` asc limit %s,%s""",(d.name, x, y))[0][0]
	  		#quote_container = frappe.db.get_value("Purchase Order", {"name": quote}, "container")
		  else:
			# quote = ""
			# 		quote_container = ""
			det = ""
			namepo = ""
			codepox = ""
			qtypox = ""
			# uompox = ""
  		  #   ratepox = ""
  		  #   amountpox = ""
			itempox = ""

		  itemsx = frappe.db.sql("""select * from `tabReceive Order Item` where docstatus = 1 and item_code = %s and purchase_order = %s""",(codepox,d.name), as_dict=1)
		  for rowx in itemsx:
		  	if flt(x) == 0:
				count_last_receipt = frappe.db.sql("""select count(*) from `tabReceive Order` pr inner join `tabReceive Order Item` pri where pr.docstatus = '1' and pri.item_code = %s""", codepox)[0][0]
				if flt(count_last_receipt) == 1:
					last_receipt = frappe.db.sql("""select item_code from `tabReceive Order` pr inner join `tabReceive Order` pri where pr.docstatus = '1' and pri.item_code = %s order by pri.item_code desc limit 1""", codepox)[0][0]
				else:
					last_receipt = ""
				#data.append([namepo,datepo,supppo,codepox,itempox,qtypox,uompox,ratepox,amountpox,qtypox])
				data.append([namepo,datepo,supppo,codepox,itempox,qtypox,uompox,ratepox,amountpox,qtypox,rowx.qty,last_receipt,rowx.name,rowx.posting_date,rowx.container,rowx.etd])
		  	else:
				#data.append(['','','',codepox,itempox,qtypox,uompox,ratepox,amountpox,qtypox])
				data.append(["","","",codepox,itempox,qtypox,uompox,ratepox,amountpox,qtypox,rowx.qty,rowx.item_code,rowx.name,rowx.posting_date,rowx.container,rowx.etd])
		 #tampilkan data
		 #itemsx = frappe.db.sql("""select * from `tabReceive Order Item` ro1 inner join `tabReceive Order` ro where ro.name = ro1.parent and ro.docstatus = 1 and ro1.item_code = %s and ro1.purchase_order = %s order by ro1.purchase_order asc, ro1.item_code asc""",(codepox,d.name), as_dict=1)

		  #count_ro = frappe.db.sql("""select count(*) from `tabReceive Order Item` where parent = %s order by parent asc, item_code asc""", d.name)[0][0]

		#   for rowx in itemsx:
		#     if flt(x) == 0:
		# 	  #data.append([namepo,datepo,supppo,codepox,itempox,qtypox,uompox,ratepox,amountpox,qtypox])
		# 	  data.append([namepo,datepo,supppo,codepox,itempox,qtypox,uompox,ratepox,amountpox,qtypox,rowx.qty,rowx.item_code,rowx.name,rowx.posting_date,rowx.container,rowx.etd])
		#     else:
		# 	  #data.append(['','','',codepox,itempox,qtypox,uompox,ratepox,amountpox,qtypox])
		# 	  data.append(["","","",codepox,itempox,qtypox,uompox,ratepox,amountpox,qtypox,rowx.qty,rowx.item_code,rowx.name,rowx.posting_date,rowx.container,rowx.etd])

	return columns, data


def get_columns():
	return [
		_("No.PO")+":Link/Purchase Order:80",
		_("Order Date") + ":Date:100",
		_("Supplier") + ":Link/Supplier:150",
		_("Item Code") + ":Link/Item:100",
		_("Item Name") + ":Data:100",
		_("Qty (PO)") + ":Float:80",
		_("UOM") + ":data:50",
		_("Rate") + ":Currency:100",
		_("Amount") + ":Currency:120",
		_("Qty (Order)") + ":Float:80",
		_("Qty (Received)") + ":Float:100",
		_("Item Codez") + ":Link/Item:100",
		_("No.RO")+":Link/Receive Order:100",
		_("RO Date") + ":Date:100",
		_("Container") + ":Data:150",
		_("ETD") + ":Date:80"

		# _("Qty (PO)") + ":Float:80"

	]

def get_conditions(filters):
	conditions = ""
	if filters.get("from_date"):
		conditions += "and transaction_date >= '%s'" % filters["from_date"]

	if filters.get("to_date"):
		conditions += "and transaction_date <= '%s'" % filters["to_date"]

	return conditions
