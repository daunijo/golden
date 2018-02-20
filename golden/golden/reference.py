from __future__ import unicode_literals
import frappe
from frappe.utils import nowdate, cstr, flt, now, getdate, add_months
from frappe import msgprint, _
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe.model.naming import make_autoname
from dateutil import parser
from num2words import num2words

def submit_sales_order(doc, method):
    count = frappe.db.sql("""select count(distinct(default_section)) from `tabSales Order Item` where parent = %s""", doc.name)[0][0]
    if flt(count) != 0:
        section = frappe.db.sql("""select distinct(default_section) from `tabSales Order Item` where parent = %s""", doc.name, as_dict=1)
        for row in section:
    		picking = frappe.get_doc({
    			"doctype": "Picking",
    			"sales_order": doc.name,
                "customer": doc.customer,
                "customer_name": doc.customer_name,
    			"section": row.default_section,
    			"transaction_date": doc.transaction_date,
    			"company": doc.company,
    		})
    		picking.insert()

def submit_sales_order_2(doc, method):
    so = doc.name
    pick = frappe.db.sql("""select `name`, section from `tabPicking` where docstatus = '0' and sales_order = %s""", doc.name, as_dict=1)
    for picking in pick:
        item = frappe.db.sql("""select * from `tabSales Order Item` where parent = %s and default_section = %s order by idx asc""", (doc.name, picking.section), as_dict=1)
        for row in item:
            picking_item = frappe.get_doc("Picking", picking.name)
            picking_item.append("items", {
    			"item_code": row.item_code,
    			"item_name": row.item_name,
    			"qty": row.qty,
                "stock_uom": row.stock_uom,
                "uom": row.uom,
                "conversion_factor": row.conversion_factor,
    			"location": row.default_location,
                "sales_order": row.parent,
                "so_detail": row.name
            })
            picking_item.save()
        simple = frappe.get_doc("Picking", picking.name)
        simple.append("simple", {
            "picking": picking.name
        })
        simple.save()
        submit_picking = frappe.get_doc("Picking", picking.name)
        submit_picking.submit()

def submit_sales_order_3(doc, method):
    warehouse_detail = frappe.db.sql("""select `name` from `tabWarehouse` where is_group = '0' and type = 'Location' and parent is not null""", as_dict=1)
    for wd in warehouse_detail:
        bins = frappe.db.sql("""select * from `tabBin` where warehouse = %s and (projected_qty + ito_qty) < 0""", wd.name, as_dict=1)
        for row in bins:
            check_ito = frappe.db.sql("""select count(*) from `tabITO` where docstatus = '0'""")[0][0]
            if flt(check_ito) == 0:
                default_warehouse = frappe.db.sql("""select `value` from `tabSingles` where doctype = 'Stock Settings' and field = 'default_warehouse'""")[0][0]
                ito = frappe.get_doc({
                	"doctype": "ITO",
                	"warehouse": default_warehouse,
                	"posting_date": doc.transaction_date,
                	"company": doc.company,
                })
                ito.insert()

def submit_sales_order_4(doc, method):
    count_ito = frappe.db.sql("""select count(*) from `tabITO` where docstatus = '0'""")[0][0]
    if flt(count_ito) == 1:
        ito_id = frappe.db.sql("""select `name` from `tabITO` where docstatus = '0'""")[0][0]
        warehouse_detail = frappe.db.sql("""select `name` from `tabWarehouse` where is_group = '0' and type = 'Location' and parent is not null""", as_dict=1)
        for wd in warehouse_detail:
            bins = frappe.db.sql("""select * from `tabBin` where warehouse = %s and (projected_qty + ito_qty) < 0 order by `name` asc""", wd.name, as_dict=1)
            for row in bins:
                check_ito_item = frappe.db.sql("""select count(*) from `tabITO Item` where parent = %s and item_code = %s and location = %s""", (ito_id, row.item_code, row.warehouse))[0][0]
                if flt(check_ito_item) == 0:
                    item_name = frappe.db.get_value("Item", {"item_code": row.item_code}, "item_name")
                    ito_item = frappe.get_doc("ITO", ito_id)
                    ito_item.append("items", {
                    	"item_code": row.item_code,
                    	"item_name": item_name,
                    	"qty_need": (flt(row.projected_qty) * -1) - flt(row.ito_qty),
                        "stock_uom": row.stock_uom,
                        "qty": 0,
                        "location": row.warehouse,
                        "bin": row.name
                    })
                    ito_item.save()
                else:
                    ito_item = frappe.get_doc("ITO Item", {"parent": ito_id, "item_code": row.item_code, "location": row.warehouse})
                    ito_item.qty_need = (flt(row.projected_qty) * -1) - flt(row.ito_qty)
                    ito_item.save()

def submit_sales_order_5(doc, method):
	frappe.db.sql("""update `tabSales Order` set golden_status = 'Pick' where `name` = %s""", doc.name)

def cancel_sales_order(doc, method):
    pick = frappe.db.sql("""select `name` from `tabPicking` where docstatus = '1' and sales_order = %s""", doc.name, as_dict=1)
    for picking in pick:
    	cancel_picking = frappe.get_doc("Picking", picking.name)
    	cancel_picking.cancel()
    	cancel_picking.delete()

def cancel_sales_order_2(doc, method):
    count_ito = frappe.db.sql("""select count(*) from `tabITO` where docstatus = '0'""")[0][0]
    if flt(count_ito) == 1:
        ito_id = frappe.db.sql("""select `name` from `tabITO` where docstatus = '0'""")[0][0]
        warehouse_detail = frappe.db.sql("""select `name` from `tabWarehouse` where is_group = '0' and type = 'Location' and parent is not null""", as_dict=1)
        for wd in warehouse_detail:
            bins = frappe.db.sql("""select * from `tabBin` where warehouse = %s""", wd.name, as_dict=1)
            for row in bins:
                check_ito_item = frappe.db.sql("""select count(*) from `tabITO Item` where parent = %s and item_code = %s and location = %s""", (ito_id, row.item_code, row.warehouse))[0][0]
                if flt(check_ito_item) == 1:
                    if flt(row.projected_qty) >= 0:
                        ito_item = frappe.get_doc("ITO Item", {"parent": ito_id, "item_code": row.item_code, "location": row.warehouse})
                        ito_item.delete()
                    else:
                        ito_item = frappe.get_doc("ITO Item", {"parent": ito_id, "item_code": row.item_code, "location": row.warehouse})
                        ito_item.qty_need = flt(row.projected_qty) * -1
                        ito_item.save()

def cancel_sales_order_3(doc, method):
    count_ito = frappe.db.sql("""select count(*) from `tabITO` where docstatus = '0'""")[0][0]
    if flt(count_ito) == 1:
        ito_id = frappe.db.sql("""select `name` from `tabITO` where docstatus = '0'""")[0][0]
        count_ito_item = frappe.db.sql("""select count(*) from `tabITO Item` where `name` = %s""", ito_id)[0][0]
        if flt(count_ito_item) == 0:
            delete_ito = frappe.get_doc("ITO", ito_id)
            delete_ito.delete()

def cancel_sales_order_4(doc, method):
	frappe.db.sql("""update `tabSales Order` set golden_status = 'Cancelled' where `name` = %s""", doc.name)

def submit_sales_invoice(doc, method):
    for row in doc.items:
        if row.sales_order:
            so_status = frappe.db.sql("""select `status` from `tabSales Order` where `name` = %s""", row.sales_order)[0][0]
            if so_status == "Completed":
                update_packing = frappe.db.sql("""update`tabPacking` set is_completed = '1' where sales_order = %s""", row.sales_order)
                update_so = frappe.db.sql("""update`tabSales Order` set golden_status = 'Invoice' where `name` = %s""", row.sales_order)

def cancel_sales_invoice(doc, method):
    for row in doc.items:
        if row.sales_order:
            update_packing = frappe.db.sql("""update`tabPacking` set is_completed = '0' where sales_order = %s""", row.sales_order)
            update_so = frappe.db.sql("""update`tabSales Order` set golden_status = 'Pack' where `name` = %s""", row.sales_order)

def submit_stock_entry(doc, method):
    if doc.ito:
        frappe.db.sql("""update `tabBin` set ito = null, ito_qty = 0 where ito = %s""", doc.ito)
        frappe.db.sql("""update `tabITO` set status = 'Completed' where `name` = %s""", doc.ito)

def validate_warehouse(doc, method):
    if not doc.parent_warehouse:
        if doc.type != "Warehouse":
            frappe.throw(_("Type must be <b>Warehouse</b>"))
        if doc.is_group == 0 and doc.type == "Warehouse":
            frappe.throw(_("<b>Is Group</b> is mandatory"))
