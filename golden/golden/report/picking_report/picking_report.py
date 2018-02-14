# Copyright (c) 2013, RSS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import cint, flt, cstr
from frappe import _

def execute(filters=None):
	if not filters: filters = {}

	columns = get_columns()
	data = get_picking_report(filters)

	return columns, data

def get_columns():
	return [
	    #_("Status") + ":Data:80",
		_("Document") + ":Link/Picking:100",
		_("No.Sales Order")+":Link/Sales Order:100",
		_("Date")+":Date:80",
		_("Section")+":Data:150",
		_("CreatedDate") + ":Datetime:150",
		_("CreatedBy") + ":Data:150",
		_("ModifiedDate") + ":Datetime:150",
		_("ModifiedBy") + ":Data:150",
		_("Action")+":Data:100"
	]

def get_picking_report(filters):
	conditions = get_conditions(filters)
	return frappe.db.sql(

		"""select
				name,
				sales_order,
				transaction_date,
				section,
				creation,owner,
				modified,modified_by,
				if(docstatus = 1 && creation <= modified, "<span class = 'label label-success'>Auto</span>","<span class = 'label label-danger'>Manual</span>")

		   from
		   		`tabPicking`
		   where
		   		docstatus < 2 %s order by name desc,transaction_date desc
		""" % conditions, as_list=1)

def get_conditions(filters):
	conditions = ""
	if filters.get("picking"):
		conditions += "and name = '%s'" % filters["picking"]

	if filters.get("sales_order"):
		conditions += "and sales_order = '%s'" % filters["sales_order"]

	if filters.get("from_date"):
		conditions += "and transaction_date >= '%s'" % filters["from_date"]

	if filters.get("to_date"):
		conditions += "and transaction_date <= '%s'" % filters["to_date"]

	return conditions
