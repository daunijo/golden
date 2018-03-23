# -*- coding: utf-8 -*-
# Copyright (c) 2018, RSS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import msgprint, _

class TransferOrder(Document):
	def validate(self):
		pass
#		self.check_qty()

	def on_submit(self):
		frappe.db.set(self, 'status', 'Submitted')
		self.update_bin()
		self.check_picker()
		self.make_stock_entry()
		self.insert_stock_entry_item()
		self.submit_stock_entry()
		self.delete_stock_entry_item_so()
		self.update_bin()
		self.update_picking()

	def on_cancel(self):
		frappe.db.set(self, 'status', 'Cancelled')
		self.cancel_bin()

	def update_bin(self):
		for row in self.items:
			if row.bin:
				bins = frappe.get_doc("Bin", row.bin)
				bins.ito = self.name
				bins.ito_qty = row.qty
				bins.save()

	def check_qty(self):
		for row in self.items:
			if row.qty <= 0:
				frappe.throw(_("Qty is mandatory"))

	def check_picker(self):
		if not self.picker:
			frappe.throw(_("Picker Name is mandatory"))

	def make_stock_entry(self):
		se = frappe.get_doc({
        	"doctype": "Stock Entry",
			"purpose": "Material Transfer",
        	"posting_date": self.posting_date,
        	"company": self.company,
            "set_posting_time": 1,
			"transfer_order": self.name
        })
		se.save()

	def insert_stock_entry_item(self):
		se = frappe.db.sql("""select `name` from `tabStock Entry` where docstatus = '0' and transfer_order = %s""", self.name)[0][0]
		for row in self.items:
			sei = frappe.get_doc("Stock Entry", se)
			sei.append("items", {
				"s_warehouse": row.from_location,
				"t_warehouse": row.to_location,
	            "item_code": row.item_code,
	            "item_name": row.item_name,
	            "qty": row.qty,
	            "uom": row.transfer_uom,
	        })
			sei.save()

	def submit_stock_entry(self):
		se = frappe.db.sql("""select `name` from `tabStock Entry` where docstatus = '0' and transfer_order = %s""", self.name)[0][0]
		submit_se = frappe.get_doc("Stock Entry", se)
		submit_se.submit()

	def delete_stock_entry_item_so(self):
		frappe.db.sql("""update `tabTransfer Order Item Detail` set so_detail = null where parent = %s""", self.name)

	def update_bin(self):
		if self.action == "Auto":
			for row in self.items:
				check_ito_bin = frappe.db.sql("""select ito from `tabBin` where item_code = %s and warehouse = %s""", (row.item_code, row.to_location))[0][0]
				bin = frappe.db.sql("""select `name` from `tabBin` where item_code = %s and warehouse = %s""", (row.item_code, row.to_location))[0][0]
				if check_ito_bin == None:
					frappe.db.sql("""update `tabBin` set ito = %s, ito_qty = %s where `name` = %s""", (self.name, row.qty_need, bin))
				elif check_ito_bin == self.name:
					bin_qty = frappe.db.sql("""select ito_qty from `tabBin` where `name`""", bin)[0][0]
					add_qty = flt(bin_qty) + flt(row.qty_need)
					frappe.db.sql("""update `tabBin` set qty_need = %s where `name` = %s""", (self.name, add_qty, bin))
				else:
					frappe.throw(_("Packing from the previous Transfer Order has not been completed"))

	def update_picking(self):
		for i in self.detail:
			frappe.db.sql("""update `tabPicking Item` set transfer_order = %s where so_detail = %s""", (self.name, i.so_detail))

	def cancel_bin(self):
		for row in self.items:
			if row.bin:
				bins = frappe.get_doc("Bin", row.bin)
				bins.ito = None
				bins.ito_qty = 0
				bins.save()
