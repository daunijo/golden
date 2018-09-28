# -*- coding: utf-8 -*-
# Copyright (c) 2018, RSS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import nowdate, cstr, flt, now, getdate, add_months
from frappe import msgprint, _
from frappe.desk.reportview import get_match_cond, get_filters_cond

class EmployeeSettings(Document):
	def on_update(self):
		self.empty_is_sales_in_employee()
		self.update_is_sales_in_employee()

	def empty_is_sales_in_employee(self):
		frappe.db.sql("""update `tabEmployee` set is_sales = '0' where status = 'Active'""")

	def update_is_sales_in_employee(self):
		for row in self.sales:
			employee = frappe.get_doc("Employee", row.employee)
			employee.is_sales = 1
			employee.save()

def employee_query(doctype, txt, searchfield, start, page_len, filters):
    return frappe.db.sql("""select e.`name`, e.employee_name from `tabEmployee` e
		inner join `tabEmployee Settings Detail` a on e.`name` = a.employee
        where a.docstatus != '2'
            and (e.`name` like %(txt)s or a.employee_name like %(txt)s)
            and a.parentfield = %(cond)s
            {mcond}
        limit %(start)s, %(page_len)s""".format(**{
            'key': searchfield,
            'mcond':get_match_cond(doctype)
        }), {
            'txt': "%%%s%%" % txt,
            '_txt': txt.replace("%", ""),
            'start': start,
            'page_len': page_len,
            'cond': filters.get("department")
        })
