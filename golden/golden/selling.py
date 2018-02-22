from __future__ import unicode_literals
import frappe
from frappe.utils import nowdate, cstr, flt, now, getdate, add_months
from frappe import msgprint, _
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe.desk.reportview import get_match_cond, get_filters_cond

def item_query(doctype, txt, searchfield, start, page_len, filters):
    return frappe.db.sql("""select distinct(a.`name`), a.item_group from `tabItem` a
        inner join `tabSales Invoice Item` b on a.`name` = b.item_code
        inner join `tabSales Invoice` c on b.parent = c.`name`
        where c.docstatus = '1'
            and (a.`name` like %(txt)s or a.item_code like %(txt)s)
            and c.customer = %(cond)s
            {mcond}
        limit %(start)s, %(page_len)s""".format(**{
            'key': searchfield,
            'mcond':get_match_cond(doctype)
        }), {
            'txt': "%%%s%%" % txt,
            '_txt': txt.replace("%", ""),
            'start': start,
            'page_len': page_len,
            'cond': filters.get("customer")
        })

def default_warehouse(doctype, txt, searchfield, start, page_len, filters):
    return frappe.db.sql("""select `name` from `tabWarehouse`
        where docstatus = '0' and is_group = '1' and type = 'Warehouse'
            and `name` like %(txt)s
            {mcond}
        limit %(start)s, %(page_len)s""".format(**{
            'key': searchfield,
            'mcond':get_match_cond(doctype)
        }), {
            'txt': "%%%s%%" % txt,
            '_txt': txt.replace("%", ""),
            'start': start,
            'page_len': page_len
        })

def si_query(doctype, txt, searchfield, start, page_len, filters):
    return frappe.db.sql("""select distinct(b.`name`), a.rate from `tabSales Invoice Item` a
        inner join `tabSales Invoice` b on a.parent = b.`name`
        where b.docstatus = '1'
            and b.`name` like %(txt)s
            and b.customer = %(customer)s
            and a.item_code = %(item_code)s
            {mcond}
        limit %(start)s, %(page_len)s""".format(**{
            'key': searchfield,
            'mcond':get_match_cond(doctype)
        }), {
            'txt': "%%%s%%" % txt,
            '_txt': txt.replace("%", ""),
            'start': start,
            'page_len': page_len,
            'customer': filters.get("customer"),
            'item_code': filters.get("item_code")
        })
