from __future__ import unicode_literals
import frappe, math
from frappe.utils import nowdate, cstr, flt, now, getdate, add_months
from frappe import msgprint, _
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe.model.naming import make_autoname
from dateutil import parser
from num2words import num2words

def change_sales_order(doc, method):
    if doc.rss_warehouse:
        for row in doc.items:
            count_qty = frappe.db.sql("""select count(*) from `tabWarehouse` w1 inner join `tabWarehouse` w2 on w1.`name` = w2.parent_warehouse inner join `tabWarehouse` w3 on w2.`name` = w3.parent_warehouse inner join `tabBin` b on w3.`name` = b.warehouse where w1.`name` = %s and w3.disabled = '0' and b.item_code = %s""", (doc.rss_warehouse, row.item_code))[0][0]
            if flt(count_qty) >= 1:
                count_projected = frappe.db.sql("""select count(*) from `tabWarehouse` w1 inner join `tabWarehouse` w2 on w1.`name` = w2.parent_warehouse inner join `tabWarehouse` w3 on w2.`name` = w3.parent_warehouse inner join `tabBin` b on w3.`name` = b.warehouse where w1.`name` = %s and w3.disabled = '0' and b.item_code = %s and b.projected_qty >= %s order by b.projected_qty asc limit 1""", (doc.rss_warehouse, row.item_code, row.stock_qty))[0][0]
                if flt(count_projected) == 1:
                    wh = frappe.db.sql("""select w2.`name` as section, w3.`name` as location from `tabWarehouse` w1 inner join `tabWarehouse` w2 on w1.`name` = w2.parent_warehouse inner join `tabWarehouse` w3 on w2.`name` = w3.parent_warehouse inner join `tabBin` b on w3.`name` = b.warehouse where w1.`name` = %s and w3.disabled = '0' and b.item_code = %s and b.projected_qty >= %s order by b.projected_qty asc limit 1""", (doc.rss_warehouse, row.item_code, row.stock_qty))
                    row.default_gudang = doc.rss_warehouse
                    row.default_section = wh[0][0]
                    row.default_location = wh[0][1]
                    row.warehouse = wh[0][1]
                else:
                    wh = frappe.db.sql("""select w2.`name` as section, w3.`name` as location from `tabWarehouse` w1 inner join `tabWarehouse` w2 on w1.`name` = w2.parent_warehouse inner join `tabWarehouse` w3 on w2.`name` = w3.parent_warehouse inner join `tabBin` b on w3.`name` = b.warehouse where w1.`name` = %s and w3.disabled = '0' and b.item_code = %s and b.projected_qty <= %s order by b.projected_qty desc limit 1""", (doc.rss_warehouse, row.item_code, row.stock_qty))
                    row.default_gudang = doc.rss_warehouse
                    row.default_section = wh[0][0]
                    row.default_location = wh[0][1]
                    row.warehouse = wh[0][1]
            else:
                row.default_gudang = doc.rss_warehouse
                row.default_section = None
                row.default_location = None
            #     frappe.throw(_("Item <b>{0}</b> has never been transaction in warehouse <b>{1}</b>").format(row.item_code, doc.rss_warehouse))

def submit_sales_order(doc, method):
    count = frappe.db.sql("""select count(distinct(default_section)) from `tabSales Order Item` where parent = %s""", doc.name)[0][0]
    if flt(count) != 0:
        section = frappe.db.sql("""select distinct(default_section) from `tabSales Order Item` where parent = %s""", doc.name, as_dict=1)
        for row in section:
    		picking = frappe.get_doc({
    			"doctype": "Picking Order",
    			"sales_order": doc.name,
                "customer": doc.customer,
                "customer_name": doc.customer_name,
    			"section": row.default_section,
    			"transaction_date": doc.transaction_date,
    			"company": doc.company,
                "action": "Auto"
    		})
    		picking.save()

    count_null_section = frappe.db.sql("""select count(*) from `tabSales Order Item` where parent = %s and default_section is null""", doc.name)[0][0]
    if flt(count_null_section) == 1:
    	picking = frappe.get_doc({
    		"doctype": "Picking Order",
    		"sales_order": doc.name,
            "customer": doc.customer,
            "customer_name": doc.customer_name,
    		"transaction_date": doc.transaction_date,
    		"company": doc.company,
            "action": "Auto"
    	})
    	picking.save()

def submit_sales_order_2(doc, method):
    so = doc.name
    pick = frappe.db.sql("""select `name`, section from `tabPicking Order` where docstatus = '0' and sales_order = %s""", doc.name, as_dict=1)
    for picking in pick:
        item = frappe.db.sql("""select * from `tabSales Order Item` where parent = %s and default_section = %s order by idx asc""", (doc.name, picking.section), as_dict=1)
        for row in item:
            picking_item = frappe.get_doc("Picking Order", picking.name)
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
        item_wo_section = frappe.db.sql("""select * from `tabSales Order Item` where parent = %s and default_section is null order by idx asc""", doc.name, as_dict=1)
        for row in item_wo_section:
            picking_item = frappe.get_doc("Picking Order", picking.name)
            picking_item.append("items", {
    			"item_code": row.item_code,
    			"item_name": row.item_name,
    			"qty": row.qty,
                "stock_uom": row.stock_uom,
                "uom": row.uom,
                "conversion_factor": row.conversion_factor,
                "sales_order": row.parent,
                "so_detail": row.name
            })
            picking_item.save()
        simple = frappe.get_doc("Picking Order", picking.name)
        simple.append("simple", {
            "picking": picking.name
        })
        simple.save()
        submit_picking = frappe.get_doc("Picking Order", picking.name)
        submit_picking.submit()

def submit_sales_order_3(doc, method):
    if doc.replenishment_warehouse:
        ito = frappe.db.get_value("Transfer Order", {"docstatus": 0, "action": "Auto"}, "name")
        # check_ito = frappe.db.sql("""select count(*) from `tabTransfer Order` where docstatus = '0' and action = 'Auto'""")[0][0]
        # if flt(check_ito) == 0:
        if not ito:
            ito = frappe.get_doc({
            	"doctype": "Transfer Order",
            	"posting_date": doc.transaction_date,
            	"company": doc.company,
                "action": "Auto"
            })
            ito.save()

def submit_sales_order_4(doc, method):
    count_ito = frappe.db.sql("""select count(*) from `tabTransfer Order` where docstatus = '0' and action = 'Auto'""")[0][0]
    if flt(count_ito) == 1:
        ito_id = frappe.db.sql("""select `name` from `tabTransfer Order` where docstatus = '0' and action = 'Auto'""")[0][0]
        ito_item_delete = frappe.db.sql("""delete from `tabTransfer Order Item` where parent = %s""", ito_id)

    # count_rep = frappe.db.sql("""select count(*) from `tabWarehouse` where rss_is_primary = '1'""")[0][0]
    # if flt(count_rep) == 0:
    #     frappe.throw(_("<b>Replenishment Section</b> in <b>Warehouse</b> has not been selected"))

def submit_sales_order_5(doc, method):
    ito = frappe.db.get_value("Transfer Order", {"docstatus": 0, "action": "Auto"}, "name")
    if doc.replenishment_warehouse:
        rep_wh = []
        for rep in doc.replenishment_warehouse:
            rep_wh.append("*-"+rep.warehouse+"*-")
        wh_list = ", ".join(rep_wh)
        whwh = wh_list.replace("*-", "'")

        for row in doc.items:
            if row.default_location:
                stock_in_location = frappe.db.get_value("Bin", {"item_code": row.item_code, "warehouse": row.default_location}, "(actual_qty - ito_qty)")
                diff_qty = flt(row.stock_qty) - flt(stock_in_location)
            else:
                diff_qty = flt(row.stock_qty)
            if flt(diff_qty) >= 1:
                if row.default_location:
                    stock_bin = frappe.db.get_value("Bin", {"item_code": row.item_code, "warehouse": row.default_location}, "(actual_qty - ito_qty)")
                    frappe.db.sql("""update `tabBin` set ito_qty = %s where item_code = %s and warehouse = %s""", (stock_bin, row.item_code, row.default_location))
                count1 = frappe.db.sql("select sum(b.actual_qty - b.ito_qty) from `tabBin` b inner join `tabWarehouse` w1 on b.warehouse = w1.`name` inner join `tabWarehouse` w2 on w1.parent_warehouse = w2.`name` inner join `tabWarehouse` w3 on w2.parent_warehouse = w3.`name` where b.item_code = %s and w3.`name` in ("+whwh+")", (row.item_code))[0][0]
                if flt(count1) >= flt(diff_qty):
                    ada = 0
                    for rh in doc.replenishment_warehouse:
                        count2 = frappe.db.sql("select sum(b.actual_qty - b.ito_qty) from `tabBin` b inner join `tabWarehouse` w1 on b.warehouse = w1.`name` inner join `tabWarehouse` w2 on w1.parent_warehouse = w2.`name` inner join `tabWarehouse` w3 on w2.parent_warehouse = w3.`name` where b.item_code = %s and w3.`name` = %s", (row.item_code, rh.warehouse))[0][0]
                        if flt(ada) == 0 and flt(count2) >= flt(diff_qty):
                            ada = flt(ada)+1
                            count3 = frappe.db.sql("select count(*) from `tabBin` b inner join `tabWarehouse` w1 on b.warehouse = w1.`name` inner join `tabWarehouse` w2 on w1.parent_warehouse = w2.`name` inner join `tabWarehouse` w3 on w2.parent_warehouse = w3.`name` where b.item_code = %s and w3.`name` = %s and (b.actual_qty - b.ito_qty) >= %s", (row.item_code, rh.warehouse, diff_qty))[0][0]
                            if flt(count3) >= 1:
                                rw = frappe.db.sql("select b.warehouse from `tabBin` b inner join `tabWarehouse` w1 on b.warehouse = w1.`name` inner join `tabWarehouse` w2 on w1.parent_warehouse = w2.`name` inner join `tabWarehouse` w3 on w2.parent_warehouse = w3.`name` where b.item_code = %s and w3.`name` = %s and (b.actual_qty - ito_qty) >= %s order by (b.actual_qty - b.ito_qty) asc limit 1", (row.item_code, rh.warehouse, diff_qty))[0][0]
                                ito_detail = frappe.get_doc("Transfer Order", ito)
                                ito_detail.append("detail", {
                                    "item_code": row.item_code,
                                    "item_name": row.item_name,
                                    "qty_need": diff_qty,
                                    "stock_uom": row.stock_uom,
                                    "from_location": rw,
                                    "to_location": row.default_location,
                                    "so_detail": row.name,
                                    "sales_order": doc.name
                                })
                                ito_detail.save()
                                bin_ito = frappe.db.get_value("Bin", {"item_code": row.item_code, "warehouse": rw}, "ito_qty")
                                bin_ito = flt(bin_ito) + flt(diff_qty)
                                frappe.db.sql("""update `tabBin` set ito_qty = %s where item_code = %s and warehouse = %s""", (bin_ito, row.item_code, rw))
                            else:
                                list_location = frappe.db.sql("select b.warehouse, b.actual_qty, b.ito_qty from `tabBin` b inner join `tabWarehouse` w1 on b.warehouse = w1.`name` inner join `tabWarehouse` w2 on w1.parent_warehouse = w2.`name` inner join `tabWarehouse` w3 on w2.parent_warehouse = w3.`name` where b.item_code = %s and w3.`name` = %s and (b.actual_qty - b.ito_qty) >= '1' order by (b.actual_qty - b.ito_qty) asc", (row.item_code, rh.warehouse), as_dict=1)
                                qty1 = diff_qty
                                temp = []
                                for lol in list_location:
                                    if flt(qty1) >= 1:
                                        rem_qty = flt(lol.actual_qty) - flt(lol.ito_qty)
                                        if flt(qty1) >= flt(rem_qty):
                                            update_qty = rem_qty
                                        else:
                                            update_qty = qty1
                                        qty1 = qty1 - rem_qty
                                        ito_detail = frappe.get_doc("Transfer Order", ito)
                                        ito_detail.append("detail", {
                                            "item_code": row.item_code,
                                            "item_name": row.item_name,
                                            "qty_need": update_qty,
                                            "stock_uom": row.stock_uom,
                                            "from_location": lol.warehouse,
                                            "to_location": row.default_location,
                                            "so_detail": row.name,
                                            "sales_order": doc.name
                                        })
                                        ito_detail.save()
                                        bin_ito = frappe.db.get_value("Bin", {"item_code": row.item_code, "warehouse": lol.warehouse}, "ito_qty")
                                        bin_ito2 = bin_ito + flt(update_qty)
                                        frappe.db.sql("""update `tabBin` set ito_qty = %s where item_code = %s and warehouse = %s""", (bin_ito2, row.item_code, lol.warehouse))
                    if flt(ada) == 0:
                        qty1 = diff_qty
                        for rh in doc.replenishment_warehouse:
                            list_location = frappe.db.sql("select b.warehouse, b.actual_qty, b.ito_qty from `tabBin` b inner join `tabWarehouse` w1 on b.warehouse = w1.`name` inner join `tabWarehouse` w2 on w1.parent_warehouse = w2.`name` inner join `tabWarehouse` w3 on w2.parent_warehouse = w3.`name` where b.item_code = %s and w3.`name` = %s and (b.actual_qty - b.ito_qty) >= '1' order by (b.actual_qty - b.ito_qty) asc", (row.item_code, rh.warehouse), as_dict=1)
                            for lol in list_location:
                                if flt(qty1) >= 1:
                                    rem_qty = flt(lol.actual_qty) - flt(lol.ito_qty)
                                    if flt(qty1) >= flt(rem_qty):
                                        update_qty = rem_qty
                                    else:
                                        update_qty = qty1
                                    qty1 = qty1 - rem_qty
                                    ito_detail = frappe.get_doc("Transfer Order", ito)
                                    ito_detail.append("detail", {
                                        "item_code": row.item_code,
                                        "item_name": row.item_name,
                                        "qty_need": update_qty,
                                        "stock_uom": row.stock_uom,
                                        "from_location": lol.warehouse,
                                        "to_location": row.warehouse,
                                        "so_detail": row.name,
                                        "sales_order": doc.name
                                    })
                                    ito_detail.save()
                                    bin_ito = frappe.db.get_value("Bin", {"item_code": row.item_code, "warehouse": lol.warehouse}, "ito_qty")
                                    bin_ito2 = bin_ito + flt(update_qty)
                                    frappe.db.sql("""update `tabBin` set ito_qty = %s where item_code = %s and warehouse = %s""", (bin_ito2, row.item_code, lol.warehouse))
                else:
                    frappe.throw(_("Stock not enough in all <b>Replenishment Warehouse</b> for item {0}").format(row.item_code))
            else:
                if row.default_location:
                    stock_bin = frappe.db.get_value("Bin", {"item_code": row.item_code, "warehouse": row.default_location}, "ito_qty")
                    update_qty = flt(stock_bin) + flt(row.stock_qty)
                    frappe.db.sql("""update `tabBin` set ito_qty = %s where item_code = %s and warehouse = %s""", (update_qty, row.item_code, row.default_location))

def submit_sales_order_5_old(doc, method):
    count_ito = frappe.db.sql("""select count(*) from `tabTransfer Order` where docstatus = '0' and action = 'Auto'""")[0][0]
    if flt(count_ito) == 1:
        ito_id = frappe.db.sql("""select `name` from `tabTransfer Order` where docstatus = '0' and action = 'Auto'""")[0][0]
        for row in doc.items:
            ito_detail = frappe.get_doc("Transfer Order", ito_id)
            ito_detail.append("detail", {
                "item_code": row.item_code,
                "item_name": row.item_name,
                "qty_need": row.stock_qty,
                "stock_uom": row.stock_uom,
                "to_location": row.warehouse,
                "so_detail": row.name,
                "sales_order": row.parent
            })
            ito_detail.save()

def submit_sales_order_6(doc, method):
    ito = frappe.db.get_value("Transfer Order", {"docstatus": 0, "action": "Auto"}, "name")
    if doc.replenishment_warehouse and ito:
        ito_detail = frappe.db.sql("""select * from `tabTransfer Order Item Detail` where parent = %s order by idx asc""", ito, as_dict=1)
        for item in ito_detail:
            largest_uom = frappe.db.sql("""select uom from `tabUOM Conversion Detail` where parent = %s order by conversion_factor desc limit 1""", item.item_code)[0][0]
            largest_conversion = frappe.db.sql("""select conversion_factor from `tabUOM Conversion Detail` where parent = %s order by conversion_factor desc limit 1""", item.item_code)[0][0]
            toi = frappe.db.get_value("Transfer Order Item", {"parent": ito, "item_code": item.item_code, "from_location": item.from_location, "to_location": item.to_location}, ["name", "qty_need"], as_dict=1)
            if toi:
                update_qty = flt(item.qty_need) + flt(toi.qty_need)
                transfer_qty = math.ceil(flt(update_qty) / flt(largest_conversion))
                ito_item = frappe.get_doc("Transfer Order", ito)
                ito_item.qty_need = update_qty
                ito_item.qty = transfer_qty
                ito_item.save()
            else:
                transfer_qty = math.ceil(flt(item.qty_need) / flt(largest_conversion))
                ito_item = frappe.get_doc("Transfer Order", ito)
                ito_item.append("items", {
                	"item_code": item.item_code,
                	"item_name": item.item_name,
                	"qty_need": item.qty_need,
                    "stock_uom": item.stock_uom,
                    "qty": transfer_qty,
                    "transfer_uom": largest_uom,
                    "from_location": item.from_location,
                    "to_location": item.to_location,
                    "conversion_factor": largest_conversion
                })
                ito_item.save()

def submit_sales_order_6_old(doc, method):
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
                        frappe.throw(_("Stock not enough in all <b>Replenishment Warehouse</b> for items <b>{0}</b>, only {1} available").format(it.item, available_qty))

def submit_sales_order_7(doc, method):
	frappe.db.sql("""update `tabSales Order` set golden_status = 'In Picking' where `name` = %s""", doc.name)

def cancel_sales_order(doc, method):
	frappe.db.sql("""update `tabSingles` set value = null where doctype = 'Batch Picking' and field = 'from'""")
	frappe.db.sql("""update `tabSingles` set value = null where doctype = 'Batch Picking' and field = 'to'""")

def cancel_sales_order_2(doc, method):
    pick = frappe.db.sql("""select `name` from `tabPicking Order` where docstatus = '1' and sales_order = %s""", doc.name, as_dict=1)
    for picking in pick:
    	cancel_picking = frappe.get_doc("Picking Order", picking.name)
    	cancel_picking.cancel()
    	cancel_picking.delete()

def cancel_sales_order_3(doc, method):
    count_ito = frappe.db.sql("""select count(*) from `tabTransfer Order` where docstatus = '0' and action = 'Auto'""")[0][0]
    if flt(count_ito) == 1:
        ito_id = frappe.db.sql("""select `name` from `tabTransfer Order` where docstatus = '0' and action = 'Auto'""")[0][0]
        for row in doc.items:
            count_ito_det = frappe.db.sql("""select count(*) from `tabTransfer Order Item Detail` where docstatus = '0' and so_detail = %s""", row.name)[0][0]
            if flt(count_ito_det) != 0:
                qty = 0
                to_detail = frappe.db.sql("""select * from `tabTransfer Order Item Detail` where docstatus = '0' and so_detail = %s""", row.name, as_dict=1)
                for tod in to_detail:
                    bin_ito = frappe.db.get_value("Bin", {"item_code": row.item_code, "warehouse": tod.from_location}, "ito_qty")
                    bin_ito2 = bin_ito - flt(tod.qty_need)
                    qty = flt(qty) + flt(bin_ito)
                    frappe.db.sql("""update `tabBin` set ito_qty = %s where item_code = %s and warehouse = %s""", (bin_ito2, row.item_code, tod.from_location))
                ito_detail = frappe.get_doc("Transfer Order Item Detail", {"so_detail": row.name})
                ito_detail.delete()
                if flt(qty) < flt(row.stock_qty):
                    a = frappe.db.get_value("Bin", {"item_code": row.item_code, "warehouse": row.default_location}, "ito_qty")
                    c = flt(row.stock_qty) - flt(qty)
                    b = flt(a) - flt(c)
                    frappe.db.sql("""update `tabBin` set ito_qty = %s where item_code = %s and warehouse = %s""", (b, row.item_code, row.default_location))
    else:
        for row in doc.items:
            bin = frappe.db.get_value("Bin", {"item_code": row.item_code, "warehouse": row.default_location}, ["name", "ito_qty"], as_dict=1)
            if bin:
                a = flt(bin.ito_qty) - flt(row.stock_qty)
                frappe.db.sql("""update `tabBin` set ito_qty = %s where `name` = %s""", (a, bin.name))

def cancel_sales_order_4(doc, method):
    count_ito = frappe.db.sql("""select count(*) from `tabTransfer Order` where docstatus = '0' and action = 'Auto'""")[0][0]
    if flt(count_ito) == 1:
        ito_id = frappe.db.sql("""select `name` from `tabTransfer Order` where docstatus = '0' and action = 'Auto'""")[0][0]
        count_ito_item = frappe.db.sql("""select count(*) from `tabTransfer Order Item` where parent = %s""", ito_id)[0][0]
        if flt(count_ito_item) == 0:
            delete_ito = frappe.get_doc("Transfer Order", ito_id)
            delete_ito.delete()

def cancel_sales_order_5(doc, method):
	frappe.db.sql("""update `tabSales Order` set golden_status = 'Cancelled' where `name` = %s""", doc.name)

def submit_delivery_note(doc, method):
    for row in doc.items:
        count_ro = frappe.db.sql("""select count(*) from `tabReceive Order Item` where docstatus = '1' and item_code = %s and stock_qty > used_qty""", row.item_code)[0][0]
        if flt(count_ro) != 0:
            roi = frappe.db.sql("""select roi.`name`, roi.stock_qty, roi.used_qty, ro.`name` as ro_id from `tabReceive Order Item` roi inner join `tabReceive Order` ro on roi.parent = ro.`name` where ro.docstatus = '1' and roi.item_code = %s and roi.stock_qty > roi.used_qty order by ro.posting_date asc""", row.item_code, as_dict=1)
            qty = flt(row.stock_qty)
            for a in roi:
                qty_remaining = flt(a.stock_qty) - flt(a.used_qty)
                if flt(qty_remaining) >= flt(qty):
                    qty_update =  flt(a.used_qty) + flt(qty)
                    frappe.db.sql("""update `tabReceive Order Item` set used_qty = %s where `name` = %s""", (qty_update, a.name))
                    receive_order = frappe.get_doc("Receive Order", a.ro_id)
                    receive_order.append("delivery", {
                        "delivery_note": doc.name,
                        "dn_detail": row.name,
                        "delivery_date": doc.posting_date,
                    	"item_code": row.item_code,
                        "qty": qty,
                        "ro_item": a.name
                    })
                    receive_order.save()
                    break
                else:
                    if flt(qty) <= 0:
                        break
                    else:
                        qty_update =  flt(a.stock_qty)
                        qty_delivery = flt(a.stock_qty) - flt(a.used_qty)
                        frappe.db.sql("""update `tabReceive Order Item` set used_qty = %s where `name` = %s""", (qty_update, a.name))
                        receive_order = frappe.get_doc("Receive Order", a.ro_id)
                        receive_order.append("delivery", {
                            "delivery_note": doc.name,
                            "dn_detail": row.name,
                            "delivery_date": doc.posting_date,
                        	"item_code": row.item_code,
                            "qty": qty_delivery,
                            "ro_item": a.name
                        })
                        receive_order.save()
                        qty = qty - qty_remaining
            # frappe.db.get_value("Packing", source.parent, ["customer", "customer_name", "posting_date", "total_box"], as_dict=1)

def cancel_delivery_note_1(doc, method):
    items = frappe.db.sql("""select * from `tabReceive Order Item Delivery` where delivery_note = %s""", doc.name, as_dict=1)
    for a in items:
        used_qty = frappe.db.get_value("Receive Order Item", a.ro_item, "used_qty")
        new_used_qty = flt(used_qty) - flt(a.qty)
        frappe.db.sql("""update `tabReceive Order Item` set used_qty = %s where `name` = %s""", (new_used_qty, a.ro_item))

def cancel_delivery_note_2(doc, method):
    frappe.db.sql("""delete from `tabReceive Order Item Delivery` where delivery_note = %s""", doc.name)

def submit_sales_invoice(doc, method):
    for row in doc.items:
        if row.sales_order:
            # so_status = frappe.db.sql("""select `status` from `tabSales Order` where `name` = %s""", row.sales_order)[0][0]
            # if so_status == "Completed":
            update_packing = frappe.db.sql("""update`tabPacking` set is_completed = '1' where sales_order = %s""", row.sales_order)
            update_so = frappe.db.sql("""update`tabSales Order` set golden_status = 'Wait for Delivery and Bill' where `name` = %s""", row.sales_order)

def cancel_sales_invoice(doc, method):
    for row in doc.items:
        so_status = frappe.db.get_value("Sales Order", row.sales_order, "golden_status")
        if so_status != 'Wait for Delivery and Bill':
            frappe.throw(_("You can not cancel this invoice"))
        elif row.sales_order:
            update_packing = frappe.db.sql("""update `tabPacking` set is_completed = '0' where sales_order = %s""", row.sales_order)
            update_so = frappe.db.sql("""update `tabSales Order` set golden_status = 'Packed' where `name` = %s""", row.sales_order)

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

    # if doc.type == "Section" and doc.rss_is_primary == 1:
    #     check_primary = frappe.db.sql("""select count(*) from `tabWarehouse` where rss_is_primary = '1'""")[0][0]
    #     if flt(check_primary) != 0:
    #         frappe.throw(_("<b>Replenishment Section</b> already used by another Section"))
