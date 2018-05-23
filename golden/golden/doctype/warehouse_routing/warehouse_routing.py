# -*- coding: utf-8 -*-
# Copyright (c) 2018, RSS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import nowdate, cstr, flt, now, getdate, add_months
from frappe import msgprint, _
from frappe.model.mapper import get_mapped_doc

class WarehouseRouting(Document):
	pass

@frappe.whitelist()
def get_template_warehouse(tw):
	si_list = []
	sales_invoice = frappe.db.sql("""select warehouse from `tabWarehouse Routing Detail` where parent = %s order by idx asc""", (tw), as_dict=True)
	for si in sales_invoice:
		si_list.append(frappe._dict({
	        'warehouse': si.warehouse
	    }))
	return si_list
