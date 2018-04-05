from __future__ import unicode_literals
import frappe
from frappe.utils import nowdate, cstr, flt, now, getdate, add_months
from frappe import msgprint, _
from frappe.model.document import Document
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

def pi_query(doctype, txt, searchfield, start, page_len, filters):
    return frappe.db.sql("""select distinct(b.`name`), concat('Date: ', b.posting_date), concat('<br>Price: ', cast((a.rate / a.conversion_factor) as int)), concat('<br>Qty: ', cast(qty as decimal(16,0))) from `tabPurchase Invoice Item` a inner join `tabPurchase Invoice` b on a.parent = b.`name`
        where b.docstatus = '1'
            and b.`name` like %(txt)s
            and b.supplier = %(supplier)s
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
            'supplier': filters.get("supplier"),
            'item_code': filters.get("item_code")
        })
