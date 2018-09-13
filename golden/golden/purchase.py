from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import nowdate, cstr, flt, now, getdate, add_months
from frappe import msgprint, _
from frappe.model.mapper import get_mapped_doc
from frappe.desk.reportview import get_match_cond, get_filters_cond

def address_query(doctype, txt, searchfield, start, page_len, filters):
    return frappe.db.sql("""select a.`name`, a.city, a.country from `tabAddress` a
        inner join `tabDynamic Link` b on a.`name` = b.parent
        where a.docstatus != '2'
            and (a.address_title like %(txt)s or a.`name` like %(txt)s)
            and b.link_name = %(cond)s
            {mcond}
        limit %(start)s, %(page_len)s""".format(**{
            'key': searchfield,
            'mcond':get_match_cond(doctype)
        }), {
            'txt': "%%%s%%" % txt,
            '_txt': txt.replace("%", ""),
            'start': start,
            'page_len': page_len,
            'cond': filters.get("link_name")
        })

def item_query(doctype, txt, searchfield, start, page_len, filters):
    return frappe.db.sql("""select distinct(a.`name`), a.item_group from `tabItem` a
        inner join `tabPurchase Invoice Item` b on a.`name` = b.item_code
        inner join `tabPurchase Invoice` c on b.parent = c.`name`
        where c.docstatus = '1'
            and (a.`name` like %(txt)s or a.item_code like %(txt)s)
            and c.supplier = %(supplier)s
            {mcond}
        limit %(start)s, %(page_len)s""".format(**{
            'key': searchfield,
            'mcond':get_match_cond(doctype)
        }), {
            'txt': "%%%s%%" % txt,
            '_txt': txt.replace("%", ""),
            'start': start,
            'page_len': page_len,
            'supplier': filters.get("supplier")
        })

def receive_order_query(doctype, txt, searchfield, start, page_len, filters):
    return frappe.db.sql("""select distinct(ro.`name`), ro.expedition from `tabReceive Order` ro inner join `tabReceive Order Item` roi on ro.`name` = roi.parent inner join `tabPurchase Order` po on roi.purchase_order = po.`name`
        where ro.docstatus = '1' and ro.is_completed = '0'
            and ro.`name` like %(txt)s
            and po.supplier = %(supplier)s
            {mcond}
        limit %(start)s, %(page_len)s""".format(**{
            'key': searchfield,
            'mcond':get_match_cond(doctype)
        }), {
            'txt': "%%%s%%" % txt,
            '_txt': txt.replace("%", ""),
            'start': start,
            'page_len': page_len,
            'supplier': filters.get("supplier")
        })
