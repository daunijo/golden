# -*- coding: utf-8 -*-
# Copyright (c) 2018, RSS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import cstr, cint, flt, comma_or, getdate, nowdate, formatdate, format_time
from erpnext.stock.utils import get_incoming_rate
from erpnext.stock.stock_ledger import get_previous_sle, NegativeStockError
from erpnext.stock.get_item_details import get_bin_details, get_default_cost_center, get_conversion_factor

class SalesReturn(Document):
	def validate(self):
		self.check_si_qty_to_qty()
		self.check_write_off_account()
		self.set_transfer_qty()
		self.set_actual_qty()
		self.calculate_rate_and_amount()
		self.delete_account()
		self.set_default_account()
		self.check_allocated_ref()
		self.check_unallocated_amount()

	def before_submit(self):
		self.delete_account()
		self.copy_references()

	def on_submit(self):
		self.update_sales_invoice()
		self.stock_entry_insert()
		self.journal_entry_insert()

	def on_cancel(self):
		self.update_sales_invoice2()
		self.delete_account()
		self.stock_entry_cancel()
		self.journal_entry_cancel()

	def delete_account(self):
		count = frappe.db.sql("""select count(*) from `tabSales Return Account` where parent = %s""", self.name)[0][0]
		if flt(count) != 0:
			sra = frappe.get_doc("Sales Return Account", {"parent": self.name})
			sra.delete()

	def set_default_account(self):
		if not self.debit_account:
			check_return_account = frappe.db.sql("""select default_sales_return_account from `tabCompany` where `name` = %s""", self.company)[0][0]
			if check_return_account:
				self.debit_account = check_return_account
			else:
				frappe.throw(_("You must set <b>Default Sales Return Account</b> in Company"))

	def check_allocated_ref(self):
		for ref in self.references:
			if flt(ref.credit_in_account_currency) > flt(ref.outstanding_amount):
				frappe.throw(_("Allocated amount in row {0} is bigger than Outstanding Amount").format(ref.idx))

	def check_unallocated_amount(self):
		if flt(self.unallocated_amount) < 0:
			frappe.throw(_("Unallocated Amount cannot be minus"))

	def get_item_details(self, args=None, for_update=False):
		item = frappe.db.sql("""select stock_uom, description, image, item_name,
				expense_account, buying_cost_center, item_group, has_serial_no,
				has_batch_no
			from `tabItem`
			where name = %s
				and disabled=0
				and (end_of_life is null or end_of_life='0000-00-00' or end_of_life > %s)
			order by `name` asc""",
			(args.get('item_code'), nowdate()), as_dict = 1)
		if not item:
			frappe.throw(_("Item {0} is not active or end of life has been reached").format(args.get("item_code")))

		item = item[0]

		ret = frappe._dict({
			'uom'			      	: item.stock_uom,
			'stock_uom'			  	: item.stock_uom,
			'description'		  	: item.description,
			'image'					: item.image,
			'item_name' 		  	: item.item_name,
			'expense_account'		: args.get("expense_account"),
			'cost_center'			: get_default_cost_center(args, item),
			'qty'					: 0,
			'transfer_qty'			: 0,
			'conversion_factor'		: 1,
			'batch_no'				: '',
			'actual_qty'			: 0,
			'basic_rate'			: 0,
			'valuation_rate'			: 0,
			'serial_no'				: '',
			'has_serial_no'			: item.has_serial_no,
			'has_batch_no'			: item.has_batch_no
		})
		for d in [["Account", "expense_account", "default_expense_account"],
			["Cost Center", "cost_center", "cost_center"]]:
				company = frappe.db.get_value(d[0], ret.get(d[1]), "company")
				if not ret[d[1]] or (company and self.company != company):
					ret[d[1]] = frappe.db.get_value("Company", self.company, d[2]) if d[2] else None

		# update uom
		if args.get("uom") and for_update:
			ret.update(get_uom_details(args.get('item_code'), args.get('uom'), args.get('qty')))

		if not ret["expense_account"]:
			ret["expense_account"] = frappe.db.get_value("Company", self.company, "stock_adjustment_account")

		args['posting_date'] = self.posting_date
		args['posting_time'] = self.posting_time

		stock_and_rate = get_warehouse_details(args) if args.get('warehouse') else {}
		ret.update(stock_and_rate)

		# automatically select batch for outgoing item
		if (args.get('t_warehouse', None) and args.get('qty') and
			ret.get('has_batch_no') and not args.get('batch_no')):
			args.batch_no = get_batch_no(args['item_code'], args['t_warehouse'], args['qty'])

		return ret

	def get_stock_and_rate(self):
		self.set_transfer_qty()
		self.set_actual_qty()
		self.calculate_rate_and_amount()

	def calculate_rate_and_amount(self, force=False, update_finished_item_rate=True):
		self.set_basic_rate(force, update_finished_item_rate)
		self.update_valuation_rate()
		self.set_total_amount()

	def set_basic_rate(self, force=False, update_finished_item_rate=True):
		"""get stock and incoming rate on posting date"""
		for d in self.get('items'):
			args = frappe._dict({
				"item_code": d.item_code,
				"warehouse": d.t_warehouse,
				"posting_date": self.posting_date,
				"posting_time": self.posting_time,
				"qty": d.t_warehouse and -1*flt(d.transfer_qty) or flt(d.transfer_qty),
				"serial_no": d.serial_no,
			})

			if not flt(d.basic_rate) or d.t_warehouse or force:
				basic_rate = flt(get_incoming_rate(args), self.precision("basic_rate", d))
				if basic_rate > 0:
					d.basic_rate = basic_rate

			d.amount = flt(flt(d.transfer_qty) * flt(d.basic_rate))

	def update_valuation_rate(self):
		for d in self.get("items"):
			if d.transfer_qty:
				d.amount = flt(flt(d.basic_rate) * flt(d.qty))
				d.valuation_rate = flt(d.basic_rate)

	def set_total_amount(self):
		self.total_cogs = None
		self.total_cogs = sum([flt(item.amount) for item in self.get("items")])

	def check_si_qty_to_qty(self):
		for row in self.items:
			if row.sales_invoice:
				if flt(row.si_qty) < flt(row.qty):
					frappe.throw(_("Qty Item {0} in row {1} is greater than {2}").format(row.item_code, row.idx, row.si_qty))

	def check_write_off_account(self):
		if flt(self.unallocated_amount) != 0:
			if not self.write_off_account:
				frappe.throw(_("Write Off Account is mandatory if Unallocated Amount not 0"))

	def set_transfer_qty(self):
		for item in self.get("items"):
			if not flt(item.qty):
				frappe.throw(_("Row {0}: Qty is mandatory").format(item.idx))
			if not flt(item.conversion_factor):
				frappe.throw(_("Row {0}: UOM Conversion Factor is mandatory").format(item.idx))
			item.transfer_qty = flt(flt(item.qty) * flt(item.conversion_factor),
				self.precision("transfer_qty", item))

	def set_actual_qty(self):
		allow_negative_stock = cint(frappe.db.get_value("Stock Settings", None, "allow_negative_stock"))

		for d in self.get('items'):
			previous_sle = get_previous_sle({
				"item_code": d.item_code,
				"warehouse": d.t_warehouse,
				"posting_date": self.posting_date,
				"posting_time": self.posting_time
			})

			# get actual stock at source warehouse
			d.actual_qty = previous_sle.get("qty_after_transaction") or 0

			# validate qty during submit
			# if d.docstatus==1 and d.t_warehouse and not allow_negative_stock and d.actual_qty < d.transfer_qty:
			# 	frappe.throw(_("Row {0}: Qty not available for {4} in warehouse {1} at posting time of the entry ({2} {3})").format(d.idx,
			# 		frappe.bold(d.t_warehouse), formatdate(self.posting_date),
			# 		format_time(self.posting_time), frappe.bold(d.item_code))
			# 		+ '<br><br>' + _("Available qty is {0}, you need {1}").format(frappe.bold(d.actual_qty),
			# 			frappe.bold(d.transfer_qty)),
			# 		NegativeStockError, title=_('Insufficient Stock'))

	def copy_references(self):
		cost_center = frappe.db.sql("""select cost_center from `tabCompany` where `name` = %s""", self.company)[0][0]
		if self.get("references"):
			for d in self.get("references"):
				self.append("accounts", {
		            "account": self.credit_account,
		            "party_type": d.party_type,
		            "party": d.party,
		            "debit_in_account_currency": d.debit_in_account_currency,
		            "credit_in_account_currency": d.credit_in_account_currency,
		            "debit": d.debit_in_account_currency,
		            "credit": d.credit_in_account_currency,
					"reference_type": d.reference_type,
					"reference_name": d.reference_name,
					"cost_center": cost_center
				}).save()
		tax_nominal = flt(self.total_amount_include_vat) - flt(self.total_amount)
		if flt(tax_nominal) >= 1:
			self.append("accounts", {
				"reference_type": "",
				"account": self.vat_account,
				"debit_in_account_currency": tax_nominal,
				"debit": tax_nominal,
				"cost_center": cost_center
			}).save()
		if flt(self.unallocated_amount) > 0:
			self.append("accounts", {
				"reference_type": "",
	            "account": self.write_off_account,
				"debit_in_account_currency": 0,
				"credit_in_account_currency": self.unallocated_amount,
				"debit": 0,
				"credit": self.unallocated_amount,
				"cost_center": cost_center,
				"customer_code": self.customer
			}).save()
		self.append("accounts", {
			"reference_type": "",
            "account": self.debit_account,
            "debit_in_account_currency": self.total_amount,
            "debit": self.total_amount,
			"cost_center": cost_center
		}).save()

	def update_sales_invoice(self):
		for row in self.items:
			if row.sales_invoice:
				remaining_qty = frappe.db.sql("""select return_qty from `tabSales Invoice Item` where parent = %s and item_code = %s""", (row.sales_invoice, row.item_code))[0][0]
				update_return_qty = flt(remaining_qty) + flt(row.qty)
				frappe.db.sql("""update `tabSales Invoice Item` set return_qty = %s where parent = %s and item_code = %s""", (update_return_qty, row.sales_invoice, row.item_code))

	def stock_entry_insert(self):
		stock_entry = frappe.get_doc({
			"doctype": "Stock Entry",
			"purpose": "Material Receipt",
			"sales_return": self.name,
			"posting_date": self.posting_date,
			"posting_time": self.posting_time,
			"to_warehouse": self.to_warehouse,
			"total_incomig_value": self.total_cogs,
			"value_difference": self.total_cogs,
			"total_amount": self.total_cogs,
			"items": self.items
		})
		stock_entry.save()
		se = frappe.get_doc("Stock Entry", {"sales_return": self.name})
		se.submit()

	def journal_entry_insert(self):
		journal_entry = frappe.get_doc({
			"doctype": "Journal Entry",
			"voucher_type": "Journal Entry",
			"sales_return": self.name,
			"posting_date": self.posting_date,
			"company": self.company,
			"total_debit": self.total_return,
			"total_credit": self.total_return,
			"accounts": self.accounts,
			"rss_customer": self.customer
		})
		journal_entry.save()
		je = frappe.get_doc("Journal Entry", {"sales_return": self.name})
		je.submit()

	def update_sales_invoice2(self):
		for row in self.items:
			if row.sales_invoice:
				remaining_qty = frappe.db.sql("""select return_qty from `tabSales Invoice Item` where parent = %s and item_code = %s""", (row.sales_invoice, row.item_code))[0][0]
				update_return_qty = flt(remaining_qty) - flt(row.qty)
				frappe.db.sql("""update `tabSales Invoice Item` set return_qty = %s where parent = %s and item_code = %s""", (update_return_qty, row.sales_invoice, row.item_code))

	def stock_entry_cancel(self):
		se = frappe.get_doc("Stock Entry", {"sales_return": self.name})
		se.cancel()
		se.delete()

	def journal_entry_cancel(self):
		je = frappe.get_doc("Journal Entry", {"sales_return": self.name})
		je.cancel()
		je.delete()

@frappe.whitelist()
def get_warehouse_details(args):
	if isinstance(args, basestring):
		args = json.loads(args)

	args = frappe._dict(args)

	ret = {}
	if args.warehouse and args.item_code:
		args.update({
			"posting_date": args.posting_date,
			"posting_time": args.posting_time,
		})
		ret = {
			"actual_qty" : get_previous_sle(args).get("qty_after_transaction") or 0,
			"basic_rate" : get_incoming_rate(args),
			"valuation_rate" : get_incoming_rate(args)
		}

	return ret

@frappe.whitelist()
def get_item_rate(parent, item_code):
	sales = frappe.db.get_value("Sales Invoice", parent, "rss_sales_person")
	rate = frappe.db.sql("""select (rate/conversion_factor) from `tabSales Invoice Item` where parent = %s and item_code = %s""", (parent, item_code))[0][0]
	qty = frappe.db.sql("""select sum(qty - return_qty) from `tabSales Invoice Item` where item_code = %s and parent = %s""", (item_code, parent))[0][0]
	si_rate = {
		'si_rate': flt(rate),
		'sales_person': sales,
		'si_qty': qty
	}
	return si_rate

@frappe.whitelist()
def get_references(customer):
	si_list = []
	sales_invoice = frappe.db.sql("""select * from `tabSales Invoice` where docstatus = '1' and customer = %s and outstanding_amount > 0""", customer, as_dict=True)
	for si in sales_invoice:
		account = frappe.db.get_value("Company", si.company, "default_sales_return_account")
		si_list.append(frappe._dict({
	        'reference_name': si.name,
	        'posting_date': si.posting_date,
	        'total_amount': si.grand_total,
			'outstanding_amount': si.outstanding_amount,
			'party': si.customer,
			'account': account
	    }))
	return si_list
