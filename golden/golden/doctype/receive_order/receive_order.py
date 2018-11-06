# -*- coding: utf-8 -*-
# Copyright (c) 2018, RSS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import nowdate, cstr, flt
from frappe import msgprint, _
from frappe.model.mapper import get_mapped_doc
from frappe.desk.reportview import get_match_cond, get_filters_cond
from datetime import timedelta

class ReceiveOrder(Document):
	def validate(self):
		self.check_item()
		self.update_stock_qty()

	def before_submit(self):
		self.update_status_submitted()

	def on_submit(self):
		if not self.from_stock_reconciliation:
			self.check_packaging()
			self.create_purchase_receipt()
			self.insert_pr_taxes()
			self.submit_purchase_receipt()
			self.update_transaction_date()

	def on_cancel(self):
		self.delete_purchase_receipt()
		self.update_status_cancel()

	def check_item(self):
		temp = []
		for row in self.items:
			if row.po_detail in temp:
				frappe.throw(_("Purchase Order {0} is duplicate").format(row.purchase_order))
			else:
				temp.append(row.po_detail)

	def update_stock_qty(self):
		for row in self.items:
			row.stock_qty = flt(row.qty) * flt(row.conversion_factor)

	def check_packaging(self):
		pack = 0
		for row in self.items:
			pack = flt(pack) + flt(row.packaging)

		if flt(pack) != flt(self.packaging):
			frappe.throw(_("Please recheck your Packaging"))

	def create_purchase_receipt(self):
		purchase_order = frappe.db.sql("""select distinct(purchase_order) as po_name from `tabReceive Order Item` where parent = %s and qty != 0""", self.name, as_dict=1)
		temp = []
		for po in purchase_order:
			source = frappe.db.get_value("Purchase Order", po.po_name, ["supplier", "supplier_name", "taxes_and_charges", "apply_discount_on", "additional_discount_percentage", "base_discount_amount", "discount_amount"], as_dict=1)
			pr = frappe.new_doc("Purchase Receipt")
			pr.supplier = source.supplier
			pr.supplier_name = source.supplier_name
			pr.receive_order = self.name
			pr.rss_po = po.po_name
			pr.posting_date = self.posting_date
			pr.posting_time = self.posting_time
			pr.set_posting_time = 1
			pr.taxes_and_charges = source.taxes_and_charges
			pr.apply_discount_on = source.apply_discount_on
			pr.additional_discount_percentage = source.additional_discount_percentage
			pr.base_discount_amount = source.base_discount_amount
			pr.discount_amount = source.discount_amount
			for row in self.items:
				if flt(row.qty) >= 1 and row.purchase_order == po.po_name:
					poi = frappe.db.get_value("Purchase Order Item", row.po_detail, ["price_list_rate", "rate"], as_dict=1)
					if row.uom == row.po_uom:
						final_qty = flt(row.qty)
						pr_uom = row.uom
					elif row.stock_uom == row.po_uom:
						final_qty = flt(row.qty) * flt(row.conversion_factor)
						pr_uom = row.stock_uom
					else:
						final_qty = flt(row.qty) * flt(row.conversion_factor)
						pr_uom = row.stock_uom
					pr.append("items", {
						"rss_item_code": row.item_code,
						"item_code": row.item_code,
						"item_name": row.item_name,
						"description": row.description,
						"qty": final_qty,
						"uom": pr_uom,
						"stock_uom": row.stock_uom,
						"conversion_factor": row.conversion_factor,
						"warehouse": self.accepted_location,
						"purchase_order": row.purchase_order,
						"purchase_order_item": row.po_detail,
						"schedule_date": po.schedule_date,
						"stock_qty": row.qty,
						"price_list_rate": poi.price_list_rate,
						"rate": poi.rate
					})
			pr.flags.ignore_permissions = True
			pr.save()

	def insert_pr_taxes(self):
		purchase_order = frappe.db.sql("""select distinct(purchase_order) as po_name from `tabReceive Order Item` where parent = %s and qty != 0""", self.name, as_dict=1)
		for po in purchase_order:
			taxes = frappe.db.get_value("Purchase Order", po.po_name, "total_taxes_and_charges")
			if flt(taxes) != 0:
				tc = frappe.db.sql("""select category, add_deduct_tax, charge_type, account_head, cost_center, description, rate from `tabPurchase Taxes and Charges` where parent = %s""", po.po_name, as_dict=1)
				for tax in tc:
					pr = frappe.get_doc("Purchase Receipt", {"receive_order": self.name, "rss_po": po.po_name})
					pr.append("taxes", {
						"category": tax.category,
						"add_deduct_tax": tax.add_deduct_tax,
						"charge_type": tax.charge_type,
						"account_head": tax.account_head,
						"cost_center": tax.cost_center,
						"description": tax.description,
						"rate": tax.rate
					})
					pr.save()

	def submit_purchase_receipt(self):
		count = frappe.db.sql("""select count(`name`) from `tabPurchase Receipt` where docstatus = '0' and receive_order = %s""", self.name)[0][0]
		if flt(count) >= 1:
			purchase_receipt = frappe.db.sql("""select `name` from `tabPurchase Receipt` where docstatus = '0' and receive_order = %s""", self.name, as_dict=1)
			for pr in purchase_receipt:
				submit_pr = frappe.get_doc("Purchase Receipt", pr.name)
				submit_pr.submit()

	def update_transaction_date(self):
		self.transaction_date = self.posting_date

	def delete_purchase_receipt(self):
		count = frappe.db.sql("""select count(`name`) from `tabPurchase Receipt` where docstatus = '1' and receive_order = %s""", self.name)[0][0]
		if flt(count) >= 1:
			purchase_receipt = frappe.db.sql("""select `name` from `tabPurchase Receipt` where docstatus = '1' and receive_order = %s""", self.name, as_dict=1)
			for pr in purchase_receipt:
				submit_pr = frappe.get_doc("Purchase Receipt", pr.name)
				submit_pr.cancel()
				submit_pr.delete()

	def update_status_submitted(self):
		self.status = "Submitted"

	def update_status_cancel(self):
		self.status = "Cancelled"

@frappe.whitelist()
def get_purchase_order(source_name, target_doc=None):
	def set_missing_values(source, target):
		target.run_method("set_missing_values")

	def update_item(source, target, source_parent):
		target.supplier = frappe.db.sql("""select supplier from `tabPurchase Order` where `name` = %s""", source.parent)[0][0]
		target.supplier_name = frappe.db.sql("""select supplier_name from `tabPurchase Order` where `name` = %s""", source.parent)[0][0]
		target.qty = flt(frappe.db.sql("""select qty from `tabPurchase Order Item` where `name` = %s""", source.name)[0][0]) - flt(frappe.db.sql("""select received_qty from `tabPurchase Order Item` where `name` = %s""", source.name)[0][0])

	doclist = get_mapped_doc("Purchase Order", source_name, {
		"Purchase Order": {
			"doctype": "Receive Order",
			"validation": {
				"docstatus": ["=", 1],
			},
            "field_no_map": ["naming_series", "posting_date", "posting_time", "set_posting_time"]
		},
		"Purchase Order Item": {
			"doctype": "Receive Order Item",
			"field_map": {
				"parent": "purchase_order",
				"name": "po_detail",
				"qty": "po_qty",
				"uom": "po_uom"
			},
			"condition":lambda doc: doc.received_qty < doc.qty,
			"postprocess": update_item
		},
	}, target_doc, set_missing_values)

	return doclist

@frappe.whitelist()
def get_po_detail(po, item_code):
	poi = frappe.db.get_value("Purchase Order Item", {"docstatus": 1, "parent": po, "item_code": item_code}, ["name", "qty", "uom", "received_qty"], as_dict=1)
	pp = frappe.db.get_value("Purchase Order", po, ["supplier", "supplier_name"], as_dict=1)
	qty_remaining = flt(poi.qty) - flt(poi.received_qty)
	si_rate = {
		'po_detail': poi.name,
		'po_qty': poi.qty,
		'supplier': pp.supplier,
		'supplier_name': pp.supplier_name,
		'po_uom': poi.uom,
		'qty': qty_remaining,
		'uom': poi.uom,
		'received_qty': poi.received_qty,
		'conversion_factor': 1
	}
	return si_rate

def get_item_code(doctype, txt, searchfield, start, page_len, filters):
    # return frappe.db.sql("""select item_code, parent, concat("<br />Qty PO: ",cast(qty as int)), concat("<br />Qty: ",cast((qty-received_qty) as int)) from `tabPurchase Order Item`
    #     where docstatus = '1'
    #         and (item_name like %(txt)s or item_code like %(txt)s)
	# 		and qty > received_qty
    #         {mcond}
    #     order by item_code asc limit %(start)s, %(page_len)s""".format(**{
    #         'key': searchfield,
    #         'mcond':get_match_cond(doctype)
    return frappe.db.sql("""select distinct(a.item_code), a.item_name, concat("<br />",(select count(*) from `tabPurchase Order Item` b where b.docstatus = '1' and b.item_code = a.item_code and b.qty > b.received_qty), " PO(S)") from `tabPurchase Order Item` a
        where a.docstatus = '1'
            and (a.item_name like %(txt)s or a.item_code like %(txt)s)
			and a.qty > a.received_qty
            {mcond}
        order by a.item_code asc limit %(start)s, %(page_len)s""".format(**{
            'key': searchfield,
            'mcond':get_match_cond(doctype)
        }), {
            'txt': "%%%s%%" % txt,
            '_txt': txt.replace("%", ""),
            'start': start,
            'page_len': page_len
        })

def get_list_purchase_order(doctype, txt, searchfield, start, page_len, filters):
    return frappe.db.sql("""select distinct(parent), concat("Qty PO: ",cast(qty as int)) from `tabPurchase Order Item`
        where docstatus = '1'
			and qty > received_qty
            and parent like %(txt)s
			and item_code = %(item_code)s
            {mcond}
        order by item_code asc limit %(start)s, %(page_len)s""".format(**{
            'key': searchfield,
            'mcond':get_match_cond(doctype)
        }), {
            'txt': "%%%s%%" % txt,
            '_txt': txt.replace("%", ""),
            'start': start,
            'page_len': page_len,
			'item_code': filters.get("item_code")
        })

@frappe.whitelist()
def get_conversion_factor(parent, uom):
	cd = frappe.db.sql("""select count(*) from `tabUOM Conversion Detail` where parent = %s and uom = %s""",(parent, uom))[0][0]
	if flt(cd) == 0:
		conv = 1
	else:
		det = frappe.db.sql("""select conversion_factor from `tabUOM Conversion Detail` where parent = %s and uom = %s""",(parent, uom))[0][0]
		conv = det
	conversion_factor = {
		'conversion_factor': conv
	}
	return conversion_factor

@frappe.whitelist()
def get_items_for_pi(source_name, target_doc=None):
	def set_missing_values(source, target):
		target.run_method("set_missing_values")

	def update_item(source, target, source_parent):
		target.supplier = frappe.db.sql("""select supplier from `tabPurchase Order` where `name` = %s""", source.parent)[0][0]
		target.supplier_name = frappe.db.sql("""select supplier_name from `tabPurchase Order` where `name` = %s""", source.parent)[0][0]
		target.qty = flt(frappe.db.sql("""select qty from `tabPurchase Order Item` where `name` = %s""", source.name)[0][0]) - flt(frappe.db.sql("""select received_qty from `tabPurchase Order Item` where `name` = %s""", source.name)[0][0])

	doclist = get_mapped_doc("Receive Order", source_name, {
		"Receive Order": {
			"doctype": "Purchase Invoice",
			"validation": {
				"docstatus": ["=", 1],
			},
            "field_no_map": ["naming_series", "posting_date", "posting_time", "set_posting_time"]
		},
		"Receive Order Item": {
			"doctype": "Purchase Invoice Item",
			"field_map": {
				"parent": "purchase_order",
				"name": "po_detail",
				"qty": "po_qty",
				"uom": "po_uom"
			},
			"condition":lambda doc: doc.qty > doc.receive_qty,
			"postprocess": update_item
		},
	}, target_doc, set_missing_values)

	return doclist

@frappe.whitelist()
def get_po_due_date(supplier, ro, based_on):
	if ro.count('||') == 1:
		a,b = ro.split("||")
		ro_date = frappe.db.sql("""select posting_date from `tabReceive Order` where docstatus = '1' and (`name` = %s or `name` = %s) order by posting_date desc limit 1""", (a, b))[0][0]
		po_date = frappe.db.sql("""select po.transaction_date from `tabReceive Order` ro inner join `tabReceive Order Item` roi on ro.`name` = roi.parent inner join `tabPurchase Order` po on po.`name` = roi.purchase_order where ro.docstatus = '1' and (ro.`name` = %s or ro.`name` = %s) order by po.transaction_date desc limit 1""", (a, b))[0][0]
		po = frappe.db.sql("""select po.`name` from `tabReceive Order` ro inner join `tabReceive Order Item` roi on ro.`name` = roi.parent inner join `tabPurchase Order` po on po.`name` = roi.purchase_order where ro.docstatus = '1' and (ro.`name` = %s or ro.`name` = %s) order by po.transaction_date desc limit 1""", (a, b))[0][0]
	else:
		ro_date = frappe.db.sql("""select posting_date from `tabReceive Order` where docstatus = '1' and `name` = %s order by posting_date desc limit 1""", ro)[0][0]
		po_date = frappe.db.sql("""select po.transaction_date from `tabReceive Order` ro inner join `tabReceive Order Item` roi on ro.`name` = roi.parent inner join `tabPurchase Order` po on po.`name` = roi.purchase_order where ro.docstatus = '1' and ro.`name` = %s order by po.transaction_date desc limit 1""", ro)[0][0]
		po = frappe.db.sql("""select po.`name` from `tabReceive Order` ro inner join `tabReceive Order Item` roi on ro.`name` = roi.parent inner join `tabPurchase Order` po on po.`name` = roi.purchase_order where ro.docstatus = '1' and ro.`name` = %s order by po.transaction_date desc limit 1""", ro)[0][0]
	po_due_date = frappe.db.get_value("Payment Schedule", {"parent": po}, "due_date")
	selisih_hari = frappe.db.sql("""select datediff(%s, %s)""", (po_due_date, po_date))[0][0]
	if based_on == "Purchase Order":
		end_date = po_date + timedelta(days=selisih_hari)
		ptt = None
	elif based_on == "Receive Order":
		end_date = ro_date + timedelta(days=selisih_hari)
		ptt = None
	else:
		end_date = nowdate()
		pt = frappe.db.get_value("Payment Schedule", {"parent": po}, "payment_term")
		ptt = frappe.db.get_value("Payment Terms Template Detail", {"payment_term": pt}, "parent")
	aa = {
		'due_date': end_date,
		'payment_terms_template': ptt
	}
	return aa

@frappe.whitelist()
def get_picking_items(supplier, ro):
	si_list = []
	if ro.count('||') == 1:
		a,b = ro.split("||")
		items = frappe.db.sql("""select roi.item_code, roi.item_name, roi.po_detail, roi.qty, roi.si_qty, roi.po_uom, roi.stock_uom, roi.purchase_order, ro.accepted_location, roi.`name`, ro.`name` as rec_order from `tabReceive Order` ro inner join `tabReceive Order Item` roi on ro.`name` = roi.parent inner join `tabPurchase Order` po on roi.purchase_order = po.`name` where ro.docstatus = '1' and po.supplier = %s and (ro.`name` = %s or ro.`name` = %s) and roi.si_qty < roi.qty order by po.`name` asc""", (supplier, a, b), as_dict=1)
	else:
		items = frappe.db.sql("""select roi.item_code, roi.item_name, roi.po_detail, roi.qty, roi.si_qty, roi.po_uom, roi.stock_uom, roi.purchase_order, ro.accepted_location, roi.`name`, ro.`name` as rec_order from `tabReceive Order` ro inner join `tabReceive Order Item` roi on ro.`name` = roi.parent inner join `tabPurchase Order` po on roi.purchase_order = po.`name` where ro.docstatus = '1' and po.supplier = %s and ro.`name` = %s and roi.si_qty < roi.qty order by po.`name` asc""", (supplier, ro), as_dict=1)
	for row in items:
		description = frappe.db.get_value("Purchase Order Item", row.po_detail, "description")
		rate = frappe.db.get_value("Purchase Order Item", row.po_detail, "rate")
		amount = flt(rate) * flt(row.qty)
		si_list.append(frappe._dict({
	        'item_code': row.item_code,
			'item_name': row.item_name,
			'description': description,
			'qty': flt(row.qty) - flt(row.si_qty),
			'uom': row.po_uom,
			'stock_uom': row.stock_uom,
			'rate': rate,
			'purchase_order': row.purchase_order,
			'warehouse': row.accepted_location,
			'amount': amount,
			'po_detail': row.po_detail,
			'receive_order': row.rec_order,
			'ro_detail': row.name
	    }))
	return si_list
