# -*- coding: utf-8 -*-
# Copyright (c) 2018, RSS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import msgprint, _
from frappe.utils import nowdate, cstr, flt
from erpnext.stock.get_item_details import get_bin_details, get_default_cost_center, get_conversion_factor

class TransferOrder(Document):
	def validate(self):
		self.check_uom()

	def on_submit(self):
		frappe.db.set(self, 'status', 'Submitted')
		self.check_from_location()
		self.check_to_location()
		self.check_picker()
		self.check_batch()
		self.make_stock_entry()
		self.insert_stock_entry_item()
		self.submit_stock_entry()
		self.delete_stock_entry_item_so()
		self.update_bin()
		self.update_picking()
		self.update_picking_location()
		self.update_picking2()

	def on_cancel(self):
		if self.action == "Auto":
			frappe.throw(_("You can not cancel auto Transfer Order"))
		frappe.db.set(self, 'status', 'Cancelled')
		# self.cancel_bin()
		self.cancel_stock_entry()

	def check_uom(self):
		for row in self.items:
			if row.stock_uom == row.transfer_uom:
				if flt(row.qty) < flt(row.qty_need):
					frappe.throw(_("Transfer Qty in <b>{0}</b> is smaller than <b>{1} {2}</b>").format(row.item_code, row.qty_need, row.stock_uom))

	def check_from_location(self):
		for row in self.items:
			if not row.from_location:
				frappe.throw(_("From Location is mandatory"))

	def check_to_location(self):
		for row in self.items:
			if not row.to_location:
				frappe.throw(_("To Location is mandatory"))

	def check_qty(self):
		for row in self.items:
			if row.qty <= 0:
				frappe.throw(_("Qty is mandatory"))

	def check_picker(self):
		if not self.picker:
			frappe.throw(_("Picker Name is mandatory"))

	def check_batch(self):
		for row in self.items:
			has_batch = frappe.db.get_value("Item", row.item_code, "has_batch_no")
			if has_batch == 1 and not row.batch:
				frappe.throw(_("Batch number is mandatory for <b>{0}</b>").format(row.item_code))

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
				bin  = frappe.db.get_value("Bin", {"item_code": row.item_code, "warehouse": row.to_location}, ["name", "ito_qty"], as_dict=1)
				if bin:
					a = flt(row.qty_need) + flt(bin.ito_qty)
					frappe.db.sql("""update `tabBin` set ito_qty = %s where `name` = %s""", (a, bin.name))
					frappe.db.sql("""update `tabBin` set ito_qty = '0' where item_code = %s and warehouse = %s""", (row.item_code, row.from_location))

	def update_picking(self):
		for i in self.detail:
			frappe.db.sql("""update `tabPicking Item` set transfer_order = %s where so_detail = %s""", (self.name, i.so_detail))

	def update_picking_location(self):
		for i in self.items:
			check_piking = frappe.db.sql("""select count(*) from `tabPicking Item` where docstatus = '1' and item_code = %s and location is null""", i.item_code)[0][0]
			if flt(check_piking) != 0:
				frappe.db.sql("""update `tabPicking Item` set location = %s where docstatus = '1' and item_code = %s and location is null""", (i.to_location, i.item_code))

	def update_picking2(self):
		check_piking = frappe.db.sql("""select count(*) from `tabPicking Order` where docstatus = '1' and section is null""")[0][0]
		if flt(check_piking) != 0:
			a = frappe.db.sql("""select `name` from `tabPicking Order` where docstatus = '1' and section is null""", as_dict=1)
			for b in a:
				location = frappe.db.sql("""select location from `tabPicking Item` where docstatus = '1' and parent = %s limit 1""", b.name)[0][0]
				section = frappe.db.sql("""select parent_warehouse from `tabWarehouse` where `name` = %s""", location)[0][0]
				frappe.db.sql("""update `tabPicking Order` set section = %s where `name` =%s""", (section, b.name))

	def cancel_bin(self):
		for row in self.items:
			if row.bin:
				bins = frappe.get_doc("Bin", row.bin)
				bins.ito = None
				bins.ito_qty = 0
				bins.save()

	def cancel_stock_entry(self):
		cancel_to = frappe.get_doc("Stock Entry", {"transfer_order": self.name})
		cancel_to.cancel()
		cancel_to.delete()

@frappe.whitelist()
def get_qty_available(item_code, batch, warehouse):
	count = frappe.db.sql("""select count(*) from `tabStock Ledger Entry` where item_code = %s and warehouse = %s and batch_no = %s""", (item_code, warehouse, batch))[0][0]
	if flt(count) != 0:
		available = frappe.db.sql("""select sum(actual_qty) from `tabStock Ledger Entry` where item_code = %s and warehouse = %s and batch_no = %s""", (item_code, warehouse, batch))[0][0]
		qty_available = {
			'qty_available': available
		}
	else:
		qty_available = {
			'qty_available': 0
		}
	return qty_available

@frappe.whitelist()
def get_uom_details(item_code, uom):
	"""Returns dict `{"conversion_factor": [value], "transfer_qty": qty * [value]}`

	:param args: dict with `item_code`, `uom` and `qty`"""
	conversion_factor = get_conversion_factor(item_code, uom).get("conversion_factor")

	if not conversion_factor:
		frappe.msgprint(_("UOM coversion factor required for UOM: {0} in Item: {1}")
			.format(uom, item_code))
		ret = {'transfer_uom' : ''}
	else:
		ret = {
			'conversion_factor'		: flt(conversion_factor)
		}
	return ret
