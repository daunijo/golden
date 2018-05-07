# -*- coding: utf-8 -*-
# Copyright (c) 2018, RSS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import nowdate, cstr, flt, now, getdate, add_months
from frappe import msgprint, _
from frappe.model.mapper import get_mapped_doc

class PurchaseBudget(Document):
	def validate(self):
		pass

	def on_submit(self):
		self.insert_items()

	def insert_items(self):
		for row in self.details:
			po_item = frappe.db.sql("select item_code, item_name, stock_qty, net_amount, item_group, parent, `name` from `tabPurchase Order Item` where parent = %s", row.purchase_order, as_dict=1)
			for items in po_item:
				self.append("items", {
					"item_code": items.item_code,
					"item_name": items.item_name,
					"stock_qty": items.stock_qty,
					"net_amount": items.net_amount,
					"item_group": items.item_group,
					"purchase_order": row.purchase_order,
					"po_item": items.name
				}).save()

@frappe.whitelist()
def get_purchase_order(start_date, end_date, budget1, budget2):
	if flt(budget2) >= 1:
		budget = budget2
	else:
		budget = budget1
	total_po = frappe.db.sql("""select sum(net_total) from `tabPurchase Order` where docstatus = '1' and transaction_date between %s and %s""", (start_date, end_date))[0][0]
	po_list = []
	purchase_order = frappe.db.sql("""select * from `tabPurchase Order` where docstatus = '1' and transaction_date between %s and %s order by `name` asc""", (start_date, end_date), as_dict=1)
	for po in purchase_order:
		count_pr = frappe.db.sql("""select count(*) from `tabPurchase Receipt Item` where docstatus = '1' and purchase_order = %s""", po.name)[0][0]
		if flt(count_pr) != 0:
			purchase_receipt = frappe.db.sql("""select pr.`name` from `tabPurchase Receipt Item` pri inner join `tabPurchase Receipt` pr on pri.parent = pr.`name` where pr.docstatus = '1' and pri.purchase_order = %s order by pr.`name` desc limit 1""", po.name)[0][0]
			percentage_budget_po = (flt(po.net_total) / flt(budget)) * 100
			pr_amount = frappe.db.sql("""select sum(pri.amount) from `tabPurchase Receipt Item` pri inner join `tabPurchase Receipt` pr on pri.parent = pr.`name` where pr.docstatus = '1' and pri.purchase_order = %s """, po.name)[0][0]
			total_pr = frappe.db.sql("""select sum(pri.amount) from `tabPurchase Receipt Item` pri inner join `tabPurchase Order` po on pri.purchase_order = po.`name` where po.docstatus = '1' and po.transaction_date between %s and %s""", (start_date, end_date))[0][0]
			percentage_budget_pr = (flt(pr_amount) / flt(budget)) * 100
		else:
			purchase_receipt = ""
			pr_amount = ""
			percentage_budget_po = ""
			percentage_budget_pr = ""
		po_list.append(frappe._dict({
	        'po_date': po.transaction_date,
	        'purchase_order': po.name,
	        'po_amount': po.net_total,
			'purchase_receipt': purchase_receipt,
			'pr_amount': pr_amount,
			'percentage_budget_po': percentage_budget_po,
			'percentage_budget_pr': percentage_budget_pr
	    }))
	return po_list
