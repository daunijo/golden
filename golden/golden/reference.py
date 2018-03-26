from __future__ import unicode_literals
import frappe, math
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
                "action": "Auto"
    		})
    		picking.save()

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
    check_ito = frappe.db.sql("""select count(*) from `tabTransfer Order` where docstatus = '0'""")[0][0]
    if flt(check_ito) == 0:
        ito = frappe.get_doc({
        	"doctype": "Transfer Order",
        	"posting_date": doc.transaction_date,
        	"company": doc.company,
            "action": "Auto"
        })
        ito.save()

def submit_sales_order_4(doc, method):
    count_ito = frappe.db.sql("""select count(*) from `tabTransfer Order` where docstatus = '0'""")[0][0]
    if flt(count_ito) == 1:
        ito_id = frappe.db.sql("""select `name` from `tabTransfer Order` where docstatus = '0'""")[0][0]
        ito_item_delete = frappe.db.sql("""delete from `tabTransfer Order Item` where parent = %s""", ito_id)

    count_rep = frappe.db.sql("""select count(*) from `tabWarehouse` where rss_is_primary = '1'""")[0][0]
    if flt(count_rep) == 0:
        frappe.throw(_("<b>Replenishment Section</b> in <b>Warehouse</b> has not been selected"))

def submit_sales_order_5(doc, method):
    count_ito = frappe.db.sql("""select count(*) from `tabTransfer Order` where docstatus = '0'""")[0][0]
    if flt(count_ito) == 1:
        ito_id = frappe.db.sql("""select `name` from `tabTransfer Order` where docstatus = '0'""")[0][0]
        for row in doc.items:
            ito_detail = frappe.get_doc("Transfer Order", ito_id)
            ito_detail.append("detail", {
                "item_code": row.item_code,
                "item_name": row.item_name,
                "qty_need": row.stock_qty,
                "stock_uom": row.stock_uom,
                "to_location": row.warehouse,
                "so_detail": row.name
            })
            ito_detail.save()

def submit_sales_order_6(doc, method):
    count_ito = frappe.db.sql("""select count(*) from `tabTransfer Order` where docstatus = '0'""")[0][0]
    if flt(count_ito) == 1:
        ito_id = frappe.db.sql("""select `name` from `tabTransfer Order` where docstatus = '0'""")[0][0]
        rep = frappe.db.sql("""select `name` from `tabWarehouse` where rss_is_primary = '1'""")[0][0]
        to_warehouse = frappe.db.sql("""select distinct(to_location) as warehouse from `tabTransfer Order Item Detail` where docstatus = '0' and parent = %s""", ito_id, as_dict=1)
        for tw in to_warehouse:
            items = frappe.db.sql("""select distinct(item_code) as item, to_location, item_name, stock_uom from `tabTransfer Order Item Detail` where docstatus = '0' and parent = %s and to_location = %s""", (ito_id, tw.warehouse), as_dict=1)
            for it in items:
                qty_need = frappe.db.sql("""select sum(qty_need) from `tabTransfer Order Item Detail` where docstatus = '0' and parent = %s and to_location = %s and item_code = %s""", (ito_id, tw.warehouse, it.item))[0][0]
                qty_reserve = frappe.db.sql("""select ito_qty from `tabBin` where warehouse = %s and item_code = %s""", (tw.warehouse, it.item))[0][0]
                qty_need2 = flt(qty_need) + flt(qty_reserve)
                qty_bin = frappe.db.sql("""select (actual_qty - ito_qty) from `tabBin` where warehouse = %s and item_code = %s""", (tw.warehouse, it.item))[0][0]
                count_check_actual_qty = frappe.db.sql("""select count(*) from `tabBin` where warehouse = %s and item_code = %s and actual_qty >= %s""", (it.to_location, it.item, qty_need2))[0][0]
                if flt(count_check_actual_qty) == 0:
                    available_qty = frappe.db.sql("""select sum(b.actual_qty) from `tabWarehouse` w inner join `tabBin` b on w.`name` = b.warehouse where w.parent_warehouse = %s and b.item_code = %s""", (rep, it.item))[0][0]
                    if flt(available_qty) >= flt(qty_need):
                        count_available_qty_location = frappe.db.sql("""select count(w.`name`) from `tabWarehouse` w inner join `tabBin` b on w.`name` = b.warehouse where w.parent_warehouse = %s and (b.actual_qty - b.ito_qty) >= %s and b.item_code = %s order by actual_qty asc""", (rep, qty_need2, it.item))[0][0]
                        largest_uom = frappe.db.sql("""select uom from `tabUOM Conversion Detail` where parent = %s order by conversion_factor desc limit 1""", it.item)[0][0]
                        largest_conversion = frappe.db.sql("""select conversion_factor from `tabUOM Conversion Detail` where parent = %s order by conversion_factor desc limit 1""", it.item)[0][0]
                        qty_minus = flt(qty_need) - flt(qty_bin)
                        if flt(count_available_qty_location) != 0:
                            transfer_qty = math.ceil(flt(qty_minus) / flt(largest_conversion))
                            replenish_location = frappe.db.sql("""select w.`name` from `tabWarehouse` w inner join `tabBin` b on w.`name` = b.warehouse where w.parent_warehouse = %s and b.actual_qty >= %s and b.item_code = %s order by actual_qty asc limit 1""", (rep, qty_need, it.item))[0][0]
                            ito_item = frappe.get_doc("Transfer Order", ito_id)
                            ito_item.append("items", {
                            	"item_code": it.item,
                            	"item_name": it.item_name,
                            	"qty_need": qty_minus,
                                "stock_uom": it.stock_uom,
                                "qty": transfer_qty,
                                "transfer_uom": largest_uom,
                                "from_location": replenish_location,
                                "to_location": it.to_location
                            })
                            ito_item.save()
                        else:
                            replenish_location_list = frappe.db.sql("""select w.`name` as warehouse, b.`name` as bin_name from `tabWarehouse` w inner join `tabBin` b on w.`name` = b.warehouse where w.parent_warehouse = %s and b.actual_qty >= '1' and b.item_code = %s order by actual_qty asc""", (rep, it.item), as_dict=1)
                            hit = flt(qty_need)
                            for lr in replenish_location_list:
                                if flt(hit) > 0:
                                    qty_from_loc = frappe.db.sql("""select actual_qty from `tabBin` where item_code = %s and `name` = %s""", (it.item, lr.bin_name))[0][0]
                                    if flt(qty_from_loc) >= flt(hit):
                                        need_qty = flt(hit)
                                        transfer_qty = math.ceil(flt(hit) / flt(largest_conversion))
                                    else:
                                        need_qty = flt(qty_from_loc)
                                        transfer_qty = math.ceil(flt(qty_from_loc) / flt(largest_conversion))
                                    ito_item = frappe.get_doc("Transfer Order", ito_id)
                                    ito_item.append("items", {
                                    	"item_code": it.item,
                                    	"item_name": it.item_name,
                                    	"qty_need": need_qty,
                                        "stock_uom": it.stock_uom,
                                        "qty": transfer_qty,
                                        "transfer_uom": largest_uom,
                                        "from_location": lr.warehouse,
                                        "to_location": it.to_location
                                    })
                                    ito_item.save()
                                    hit = flt(hit) - flt(qty_from_loc)
                    else:
                        frappe.throw(_("Stock not enough in <b>Replenishment Section</b> for items <b>{0}</b>, only {1} available").format(it.item, available_qty))

def submit_sales_order_3_old(doc, method):
    warehouse_detail = frappe.db.sql("""select `name` from `tabWarehouse` where is_group = '0' and type = 'Location' and parent is not null""", as_dict=1)
    for wd in warehouse_detail:
        bins = frappe.db.sql("""select * from `tabBin` where warehouse = %s and (projected_qty + ito_qty) < 0""", wd.name, as_dict=1)
        for row in bins:
            check_ito = frappe.db.sql("""select count(*) from `tabTransfer Order` where docstatus = '0'""")[0][0]
            if flt(check_ito) == 0:
                ito = frappe.get_doc({
                	"doctype": "Transfer Order",
                	"posting_date": doc.transaction_date,
                	"company": doc.company,
                    "action": "Auto"
                })
                ito.save()

def submit_sales_order_4_old2(doc, method):
    count_ito = frappe.db.sql("""select count(*) from `tabTransfer Order` where docstatus = '0'""")[0][0]
    if flt(count_ito) == 1:
        ito_id = frappe.db.sql("""select `name` from `tabTransfer Order` where docstatus = '0'""")[0][0]
        for row in doc.items:
            if flt(row.projected_qty) < flt(row.stock_qty):
                check_ito_item2 = frappe.db.sql("""select count(*) from `tabTransfer Order Item` where parent = %s and item_code = %s and to_location = %s""", (ito_id, row.item_code, row.warehouse))[0][0]
                if flt(check_ito_item2) == 0:
                    difference = flt(row.stock_qty) - flt(row.actual_qty)
                else:
                    difference = flt(row.stock_qty)
                largest_uom = frappe.db.sql("""select uom from `tabUOM Conversion Detail` where parent = %s order by conversion_factor desc limit 1""", row.item_code)[0][0]
                largest_conversion = frappe.db.sql("""select conversion_factor from `tabUOM Conversion Detail` where parent = %s order by conversion_factor desc limit 1""", row.item_code)[0][0]
                transfer_qty = math.ceil(flt(difference) / flt(largest_conversion))
                count_rep = frappe.db.sql("""select count(*) from `tabWarehouse` where rss_is_primary = '1'""")[0][0]
                if flt(count_rep) != 0:
                    rep = frappe.db.sql("""select `name` from `tabWarehouse` where rss_is_primary = '1'""")[0][0]
                    count_replenish_location = frappe.db.sql("""select count(*) from `tabWarehouse` w inner join `tabBin` b on w.`name` = b.warehouse where w.parent_warehouse = %s and actual_qty >= %s order by actual_qty asc limit 1""", (rep, difference))[0][0]
                    if flt(count_replenish_location) != 0:
                        check_ito_item = frappe.db.sql("""select count(*) from `tabTransfer Order Item` where parent = %s and item_code = %s and to_location = %s""", (ito_id, row.item_code, row.warehouse))[0][0]
                        if flt(check_ito_item) == 0:
                            replenish_location = frappe.db.sql("""select w.`name` from `tabWarehouse` w inner join `tabBin` b on w.`name` = b.warehouse where w.parent_warehouse = %s and actual_qty >= %s order by actual_qty asc limit 1""", (rep, difference))[0][0]
                            ito_item = frappe.get_doc("Transfer Order", ito_id)
                            ito_item.append("items", {
                            	"item_code": row.item_code,
                            	"item_name": row.item_name,
                            	"qty_need": difference,
                                "stock_uom": row.stock_uom,
                                "qty": transfer_qty,
                                "transfer_uom": largest_uom,
                                "from_location": replenish_location,
                                "to_location": row.warehouse
                            })
                            ito_item.save()
                        else:
                            need_qty = frappe.db.get_value("Transfer Order Item", {"parent": ito_id, "item_code": row.item_code, "to_location": row.warehouse}, "qty_need")
                            need_add = flt(need_qty) + flt(row.stock_qty)
                            replenish_location = frappe.db.sql("""select w.`name` from `tabWarehouse` w inner join `tabBin` b on w.`name` = b.warehouse where w.parent_warehouse = %s and actual_qty >= %s order by actual_qty asc limit 1""", (rep, need_add))[0][0]
                            ito_item = frappe.get_doc("Transfer Order Item", {"parent": ito_id, "item_code": row.item_code, "to_location": row.warehouse})
                            ito_item.qty_need = need_add
                            ito_item.qty = transfer_qty
                            ito_item.from_location = replenish_location
                            ito_item.save()
                    else:
                        frappe.throw(_("Stock not enough in <b>Replenishment Section</b> for items <b>{0}</b>").format(row.item_code))
                else:
                    frappe.throw(_("<b>Replenishment Section</b> in <b>Warehouse</b> has not been selected"))
            else:
                frappe.throw(_("Item {0} oke").format(row.item_code))

def submit_sales_order_4_old1(doc, method):
    count_ito = frappe.db.sql("""select count(*) from `tabTransfer Order` where docstatus = '0'""")[0][0]
    if flt(count_ito) == 1:
        ito_id = frappe.db.sql("""select `name` from `tabTransfer Order` where docstatus = '0'""")[0][0]
        warehouse_detail = frappe.db.sql("""select `name` from `tabWarehouse` where is_group = '0' and type = 'Location' and parent is not null""", as_dict=1)
        for wd in warehouse_detail:
            bins = frappe.db.sql("""select * from `tabBin` where warehouse = %s and (projected_qty + ito_qty) < 0 order by `name` asc""", wd.name, as_dict=1)
            for row in bins:
                check_ito_item = frappe.db.sql("""select count(*) from `tabTransfer Order Item` where parent = %s and item_code = %s and to_location = %s""", (ito_id, row.item_code, row.warehouse))[0][0]
                if flt(check_ito_item) == 0:
                    item_name = frappe.db.get_value("Item", {"item_code": row.item_code}, "item_name")
                    ito_item = frappe.get_doc("Transfer Order", ito_id)
                    count_fw = frappe.db.sql("""select count(warehouse) from `tabBin` where warehouse != %s and item_code = %s order by actual_qty desc limit 1""", (row.warehouse, row.item_code))[0][0]
                    if flt(count_fw) != 0:
                        fw = frappe.db.sql("""select warehouse from `tabBin` where warehouse != %s and item_code = %s order by actual_qty desc limit 1""", (row.warehouse, row.item_code))[0][0]
                    else:
                        fw = frappe.db.sql("""select `value` from `tabSingles` where doctype = 'Stock Settings' and field = 'default_warehouse'""")[0][0]
                    ito_item.append("items", {
                    	"item_code": row.item_code,
                    	"item_name": item_name,
                    	"qty_need": (flt(row.projected_qty) * -1) - flt(row.ito_qty),
                        "stock_uom": row.stock_uom,
                        "qty": 0,
                        "from_location": fw,
                        "to_location": row.warehouse,
                        "bin": row.name
                    })
                    ito_item.save()
                else:
                    ito_item = frappe.get_doc("Transfer Order Item", {"parent": ito_id, "item_code": row.item_code, "location": row.warehouse})
                    ito_item.qty_need = (flt(row.projected_qty) * -1) - flt(row.ito_qty)
                    ito_item.save()

def submit_sales_order_7(doc, method):
	frappe.db.sql("""update `tabSales Order` set golden_status = 'In Picking' where `name` = %s""", doc.name)

def cancel_sales_order(doc, method):
    pick = frappe.db.sql("""select `name` from `tabPicking` where docstatus = '1' and sales_order = %s""", doc.name, as_dict=1)
    for picking in pick:
    	cancel_picking = frappe.get_doc("Picking", picking.name)
    	cancel_picking.cancel()
    	cancel_picking.delete()

def cancel_sales_order_2(doc, method):
    count_ito = frappe.db.sql("""select count(*) from `tabTransfer Order` where docstatus = '0'""")[0][0]
    if flt(count_ito) == 1:
        ito_id = frappe.db.sql("""select `name` from `tabTransfer Order` where docstatus = '0'""")[0][0]
        for row in doc.items:
            ito_detail = frappe.get_doc("Transfer Order Item Detail", {"so_detail": row.name})
            ito_detail.delete()

def cancel_sales_order_2_old2(doc, method):
    count_ito = frappe.db.sql("""select count(*) from `tabTransfer Order` where docstatus = '0'""")[0][0]
    if flt(count_ito) == 1:
        ito_id = frappe.db.sql("""select `name` from `tabTransfer Order` where docstatus = '0'""")[0][0]
        for row in doc.items:
            check_ito_item = frappe.db.sql("""select count(*) from `tabTransfer Order Item` where parent = %s and item_code = %s and to_location = %s""", (ito_id, row.item_code, row.warehouse))[0][0]
            if flt(check_ito_item) == 1:
                qty_need = frappe.db.sql("""select qty_need from `tabTransfer Order Item` where parent = %s and item_code = %s and to_location = %s""", (ito_id, row.item_code, row.warehouse))[0][0]
                difference = flt(qty_need) - flt(row.stock_qty)
                if flt(difference) <= 0:
                    ito_item = frappe.get_doc("Transfer Order Item", {"parent": ito_id, "item_code": row.item_code, "to_location": row.warehouse})
                    ito_item.delete()
                else:
                    ito_item = frappe.get_doc("Transfer Order Item", {"parent": ito_id, "item_code": row.item_code, "to_location": row.warehouse})
                    ito_item.qty_need = difference
                    ito_item.save()

def cancel_sales_order_2_old(doc, method):
    count_ito = frappe.db.sql("""select count(*) from `tabTransfer Order` where docstatus = '0'""")[0][0]
    if flt(count_ito) == 1:
        ito_id = frappe.db.sql("""select `name` from `tabTransfer Order` where docstatus = '0'""")[0][0]
        warehouse_detail = frappe.db.sql("""select `name` from `tabWarehouse` where is_group = '0' and type = 'Location' and parent is not null""", as_dict=1)
        for wd in warehouse_detail:
            bins = frappe.db.sql("""select * from `tabBin` where warehouse = %s""", wd.name, as_dict=1)
            for row in bins:
                check_ito_item = frappe.db.sql("""select count(*) from `tabTransfer Order Item` where parent = %s and item_code = %s and to_location = %s""", (ito_id, row.item_code, row.warehouse))[0][0]
                if flt(check_ito_item) == 1:
                    if flt(row.projected_qty) >= 0:
                        ito_item = frappe.get_doc("Transfer Order Item", {"parent": ito_id, "item_code": row.item_code, "to_location": row.warehouse})
                        ito_item.delete()
                    else:
                        ito_item = frappe.get_doc("Transfer Order Item", {"parent": ito_id, "item_code": row.item_code, "to_location": row.warehouse})
                        ito_item.qty_need = flt(row.projected_qty) * -1
                        ito_item.save()

def cancel_sales_order_3(doc, method):
    count_ito = frappe.db.sql("""select count(*) from `tabTransfer Order` where docstatus = '0'""")[0][0]
    if flt(count_ito) == 1:
        ito_id = frappe.db.sql("""select `name` from `tabTransfer Order` where docstatus = '0'""")[0][0]
        count_ito_item = frappe.db.sql("""select count(*) from `tabTransfer Order Item` where parent = %s""", ito_id)[0][0]
        if flt(count_ito_item) == 0:
            delete_ito = frappe.get_doc("Transfer Order", ito_id)
            delete_ito.delete()

def cancel_sales_order_4(doc, method):
	frappe.db.sql("""update `tabSales Order` set golden_status = 'Cancelled' where `name` = %s""", doc.name)

def submit_sales_invoice(doc, method):
    for row in doc.items:
        if row.sales_order:
            so_status = frappe.db.sql("""select `status` from `tabSales Order` where `name` = %s""", row.sales_order)[0][0]
            if so_status == "Completed":
                update_packing = frappe.db.sql("""update`tabPacking` set is_completed = '1' where sales_order = %s""", row.sales_order)
                update_so = frappe.db.sql("""update`tabSales Order` set golden_status = 'Wait for Delivery and Bill' where `name` = %s""", row.sales_order)

def cancel_sales_invoice(doc, method):
    for row in doc.items:
        if row.sales_order:
            update_packing = frappe.db.sql("""update`tabPacking` set is_completed = '0' where sales_order = %s""", row.sales_order)
            update_so = frappe.db.sql("""update`tabSales Order` set golden_status = 'In Packing' where `name` = %s""", row.sales_order)

def submit_stock_entry(doc, method):
    if doc.transfer_order:
        frappe.db.sql("""update `tabBin` set ito = null, ito_qty = 0 where ito = %s""", doc.transfer_order)
        frappe.db.sql("""update `tabTransfer Order` set status = 'Completed' where `name` = %s""", doc.ito)

def validate_warehouse(doc, method):
    if not doc.parent_warehouse:
        if doc.type != "Warehouse":
            frappe.throw(_("Type must be <b>Warehouse</b>"))
        if doc.is_group == 0 and doc.type == "Warehouse":
            frappe.throw(_("<b>Is Group</b> is mandatory"))

    if doc.type != "Section":
        doc.rss_is_primary = 0

    if doc.type == "Section" and doc.rss_is_primary == 1:
        check_primary = frappe.db.sql("""select count(*) from `tabWarehouse` where rss_is_primary = '1'""")[0][0]
        if flt(check_primary) != 0:
            frappe.throw(_("<b>Replenishment Section</b> already used by another Section"))
