# -*- coding: utf-8 -*-
# Copyright (c) 2018, RSS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import nowdate, cstr, flt, now, getdate, add_months
from frappe import msgprint, _
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc

class Packing(Document):
	def validate(self):
		for row in self.items:
			if flt(row.qty_packing) <= 0:
				frappe.throw(_("Qty Packing is mandatory in item line {0}").format(row.idx))

	def on_submit(self):
		self.delivery_note_insert()

	def delivery_note_insert(self):
		delivery_note = frappe.get_doc({
			"doctype": "Delivery Note",
			"customer": self.customer,
			"posting_date": self.posting_date,
			"posting_time": self.posting_time,
			"shipping_address_name": self.shipping_address_name,
			"currency": self.currency,
			"conversion_rate": self.conversion_rate,
			"selling_price_list": self.selling_price_list,
			"price_list_currency": self.price_list_currency,
			"plc_conversion_rate": self.plc_conversion_rate,
			"ignore_pricing_rule": self.ignore_pricing_rule,
			"items": self.items,
			"taxes_and_charges": self.taxes_and_charges,
			"taxes": self.taxes,
			"total_taxes_and_charges": self.total_taxes_and_charges,
			"base_total_taxes_and_charges": self.base_total_taxes_and_charges,
			"total": self.total,
			"base_total": self.base_total,
			"net_total": self.net_total,
			"base_net_total": self.base_net_total,
			"base_grand_total": self.base_grand_total,
			"grand_total": self.grand_total,
			"base_rounding_adjustment": self.base_rounding_adjustment,
			"base_rounded_total": self.base_rounded_total,
			"rounded_total": self.rounded_total
		})
		delivery_note.ignore_permissions = True
		delivery_note.insert()
#		se = frappe.get_doc("Delivery Note", {"sales_return": self.name})
#		se.submit()
