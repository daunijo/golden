from __future__ import unicode_literals
import frappe
from frappe.utils import nowdate, cstr, flt, now, getdate, add_months
from frappe import msgprint, _
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe.desk.reportview import get_match_cond, get_filters_cond

def default_gudang(doctype, txt, searchfield, start, page_len, filters):
    return frappe.db.sql("""select `name` from `tabWarehouse`
        where type = 'Warehouse' and disabled = '0' and `name` like %(txt)s
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

def default_location(doctype, txt, searchfield, start, page_len, filters):
    return frappe.db.sql("""select `name` from `tabWarehouse`
        where type = 'Location' and disabled = '0' and `name` like %(txt)s
            and parent = %(cond)s
            {mcond}
        limit %(start)s, %(page_len)s""".format(**{
            'key': searchfield,
            'mcond':get_match_cond(doctype)
        }), {
            'txt': "%%%s%%" % txt,
            '_txt': txt.replace("%", ""),
            'start': start,
            'page_len': page_len,
            'cond': filters.get("parent")
        })

def item_query(doctype, txt, searchfield, start, page_len, filters):
    return frappe.db.sql("""select i.`name`, i.item_name, concat('<br>Current Stock: ', cast((select sum(actual_qty) from `tabBin` where item_code = i.`name`) as int), ' ', i.stock_uom) as current_stock, concat('<br>Available Stock: ', cast((select sum(actual_qty - ito_qty) from `tabBin` where item_code = i.`name`) as int), ' ', i.stock_uom) as available_stock, concat('<br>SO Qty: ', cast((select sum(soi.stock_qty) from `tabSales Order` so inner join `tabSales Order Item` soi on so.`name` = soi.parent where so.docstatus = '1' and soi.item_code = i.`name` and so.`status` in ('To Deliver and Bill', 'To Deliver')) as int), ' ', i.stock_uom) as so_qty, concat('<br>PO Qty: ', cast((select sum(stock_qty) from `tabPurchase Order` po inner join `tabPurchase Order Item` poi on po.`name` = poi.parent where po.docstatus = '1' and poi.item_code = i.`name` and po.`status` in ('To Receive and Bill', 'To Receive')) as int), ' ', i.stock_uom) as po_qty
        from `tabItem` i
        where i.disabled = '0'
            and (i.`name` like %(txt)s or i.item_name like %(txt)s)
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

def pi_item_query(doctype, txt, searchfield, start, page_len, filters):
    return frappe.db.sql("""select roi.item_code, roi.item_name, concat('<br/>RO: ', ro.`name`), concat('<br/>Qty: ', cast(roi.qty as int), ' ', roi.uom) as ro_item from `tabReceive Order` ro
inner join `tabReceive Order Item` roi on ro.`name` = roi.parent
        where ro.docstatus = '1' and ro.`status` in ('Submitted', 'Partial Bill') and roi.purchase_invoice is null
            and (roi.item_code like %(txt)s or roi.item_name like %(txt)s)
            and roi.supplier = %(cond)s
            order by roi.item_code asc
            {mcond}
        limit %(start)s, %(page_len)s""".format(**{
            'key': searchfield,
            'mcond':get_match_cond(doctype)
        }), {
            'txt': "%%%s%%" % txt,
            '_txt': txt.replace("%", ""),
            'start': start,
            'page_len': page_len,
            'cond': filters.get("supplier")
        })

def uom_query(doctype, txt, searchfield, start, page_len, filters):
    return frappe.db.sql("""select uom from `tabUOM Conversion Detail`
        where docstatus = '0' and parent = %(cond)s
            and uom like %(txt)s
            order by idx asc
            {mcond}
        limit %(start)s, %(page_len)s""".format(**{
            'key': searchfield,
            'mcond':get_match_cond(doctype)
        }), {
            'txt': "%%%s%%" % txt,
            '_txt': txt.replace("%", ""),
            'start': start,
            'page_len': page_len,
            'cond': filters.get("item_code")
        })

@frappe.whitelist()
def make_material_transfer(source_name, target_doc=None):
    def set_missing_values(source, target):
        target.purpose = "Material Transfer"
        target.run_method("set_missing_values")

    doc = get_mapped_doc("Transfer Order", source_name, {
		"Transfer Order": {
			"doctype": "Stock Entry",
			"validation": {
				"docstatus": ["=", 1],
			},
			"field_map":{
				"name": "transfer_order",
                "warehouse": "from_warehouse"
			},
		},
		"Transfer Order Item": {
			"doctype": "Stock Entry Detail",
			"field_map":{
				"location": "t_warehouse",
				"stock_uom": "uom"
			},
		},
	}, target_doc, set_missing_values)
    return doc

@frappe.whitelist()
def make_packing_list(source_name, target_doc=None):
    def set_missing_values(source, target):
        target.run_method("set_missing_values")

    doc = get_mapped_doc("Sales Order", source_name, {
		"Sales Order": {
			"doctype": "Packing",
			"validation": {
				"docstatus": ["=", 1],
			},
		},
		"Sales Order Item": {
			"doctype": "Packing Item",
			"field_map":{
				"parent": "against_sales_order",
                "name": "so_detail"
			},
		},
	}, target_doc, set_missing_values)
    return doc

@frappe.whitelist()
def get_picking(sales_order):
    picking_list = []
    pick = frappe.db.sql("""select `name` from `tabPicking` where docstatus = '1' and sales_order = %s""", sales_order, as_dict=1)
    for picking in pick:
        picking_list.append(frappe._dict({
            'picking': picking.name,
        }))
    return picking_list

@frappe.whitelist()
def get_packing_list(source_name, target_doc=None):
    def set_missing_values(source, target):
        target.run_method("set_missing_values")

    doc = get_mapped_doc("Packing", source_name, {
		"Packing": {
			"doctype": "Delivery Keeptrack",
			"validation": {
				"docstatus": ["=", 1],
			},
            "field_no_map": ["posting_date", "posting_time", "set_posting_time", "total_box"]
		},
		"Packing Simple": {
			"doctype": "Delivery Keeptrack Detail",
		},
	}, target_doc, set_missing_values)
    return doc

@frappe.whitelist()
def set_qty_stock(name):
    a = frappe.db.sql("""select (select sum(actual_qty) from `tabBin` where item_code = i.`name`) as current_stock from `tabItem` i where i.disabled = '0' and i.item_code = %s""", name)[0][0]
    b = frappe.db.sql("""select (select sum(actual_qty - ito_qty) from `tabBin` where item_code = i.`name`) as available_stock from `tabItem` i where i.disabled = '0' and i.item_code = %s""", name)[0][0]
    c = frappe.db.sql("""select (select sum(soi.stock_qty) from `tabSales Order` so inner join `tabSales Order Item` soi on so.`name` = soi.parent where so.docstatus = '1' and soi.item_code = i.`name` and so.`status` in ('To Deliver and Bill', 'To Deliver')) as so_qty from `tabItem` i where i.disabled = '0' and i.item_code = %s""", name)[0][0]
    d = frappe.db.sql("""select (select sum(stock_qty) from `tabPurchase Order` po inner join `tabPurchase Order Item` poi on po.`name` = poi.parent where po.docstatus = '1' and poi.item_code = i.`name` and po.`status` in ('To Receive and Bill', 'To Receive')) as po_qty from `tabItem` i where i.disabled = '0' and i.item_code = %s""", name)[0][0]
    si_rate = {
		'total_current_stock': a,
		'total_available_stock': b,
		'total_so_qty': c,
		'total_po_qty': d
	}
    return si_rate
