from __future__ import unicode_literals
import frappe
from frappe.utils import nowdate, cstr, flt, now, getdate, add_months
from frappe import msgprint, _
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe.desk.reportview import get_match_cond, get_filters_cond

def item_query(doctype, txt, searchfield, start, page_len, filters):
    return frappe.db.sql("""select distinct(a.`name`), a.item_group from `tabItem` a
        inner join `tabDelivery Note Item` b on a.`name` = b.item_code
        inner join `tabDelivery Note` c on b.parent = c.`name`
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
