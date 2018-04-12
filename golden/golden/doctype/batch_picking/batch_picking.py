# -*- coding: utf-8 -*-
# Copyright (c) 2018, RSS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import msgprint, _
from frappe.model.mapper import get_mapped_doc

class BatchPicking(Document):
	pass

@frappe.whitelist()
def get_details(start_from, end_from):
    bp = frappe.db.sql("""select `name`, sales_order from `tabPicking` where docstatus = '1' and `name` between %s and %s""", (start_from, end_from), as_dict=True)
    picking_list = []
    for d in bp:
		so = frappe.db.get_value("Sales Order", d.sales_order, ["delivery_date", "address_display"], as_dict=1)
		picking_list.append(frappe._dict({
            'picking': d.name,
			'delivery_date': so.delivery_date,
			'address_display': so.address_display
        }))
    return picking_list

@frappe.whitelist()
def get_detail_items(start_from, end_from):
    bp = frappe.db.sql("""select `name` from `tabPicking` where docstatus = '1' and `name` between %s and %s""", (start_from, end_from), as_dict=True)
    pi_list = []
    for d in bp:
		picking_items = frappe.db.sql("""select * from `tabPicking Item` where docstatus = '1' and parent = %s order by idx asc""", d.name, as_dict=1)
		for pi in picking_items:
			pi_list.append(frappe._dict({
	            'item_code': pi.item_code,
				'item_name': pi.item_name,
				'qty': pi.qty,
				'stock_uom': pi.stock_uom,
				'uom': pi.uom,
				'conversion_factor': pi.conversion_factor,
				'location': pi.location,
				'qty_taken': pi.qty_taken,
				'picking': d.name,
				'urut': pi.idx
	        }))
    return pi_list
