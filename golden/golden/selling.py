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
            and c.customer = %(customer)s
            and c.rss_sales_person = %(sales_person)s
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
            'sales_person': filters.get("sales")
        })

def all_item_query(doctype, txt, searchfield, start, page_len, filters):
    return frappe.db.sql("""select a.`name`, a.item_group from `tabItem` a
        where a.disabled = '0' and a.is_stock_item = '1'
            and (a.`name` like %(txt)s or a.item_code like %(txt)s)
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
    return frappe.db.sql("""select distinct(b.`name`), concat('Price: ', format(a.rate,0)), concat('<br>Qty: ', format((select sum(c.qty - c.return_qty) from `tabSales Invoice Item` c where c.item_code = %(item_code)s and c.parent = b.`name`), 0)) from `tabSales Invoice Item` a
        inner join `tabSales Invoice` b on a.parent = b.`name`
        where b.docstatus = '1'
            and b.`name` like %(txt)s
            and b.customer = %(customer)s
            and a.item_code = %(item_code)s
            and b.rss_sales_person = %(sales_person)s
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
            'item_code': filters.get("item_code"),
            'sales_person': filters.get("sales")
        })

@frappe.whitelist()
def get_items_from_dn(sales_order):
    dn = frappe.db.sql("""select * from `tabDelivery Note Item` where docstatus = '1' and against_sales_order = %s order by idx asc""", sales_order, as_dict=True)
    si_list = []
    for d in dn:
        item = frappe.db.get_value("Item", d.item_code, ["income_account", "expense_account"], as_dict=1)
        picking_order = frappe.db.get_value("Sales Order Item", d.so_detail, "picking_order")
        si_list.append(frappe._dict({
            'rss_item_code': d.rss_item_code,
            'item_code': d.item_code,
            'item_name': d.item_name,
            'description': d.description,
            'image': d.image,
            'qty': d.qty,
            'stock_uom': d.stock_uom,
            'uom': d.uom,
            'conversion_factor': d.conversion_factor,
            'stock_qty': d.stock_qty,
            'price_list_rate': d.price_list_rate,
            'base_price_list_rate': d.base_price_list_rate,
            'margin_type': d.margin_type,
            'discount_percentage': d.discount_percentage,
            'rate': d.rate,
            'amount': d.amount,
            'base_rate': d.base_rate,
            'base_amount': d.base_amount,
            'net_rate': d.net_rate,
            'net_amount': d.net_amount,
            'base_net_rate': d.base_net_rate,
            'base_net_amount': d.base_net_amount,
            'income_account': item.income_account,
            'expense_account': item.expense_account,
            'warehouse': d.warehouse,
            'sales_order': d.against_sales_order,
            'so_detail': d.so_detail,
            'delivery_note': d.parent,
            'dn_detail': d.name,
            'picking_order': picking_order
        }))
    return si_list
