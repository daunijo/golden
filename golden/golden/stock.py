from __future__ import unicode_literals
import frappe
from frappe.utils import nowdate, cstr, flt, now, getdate, add_months
from frappe import msgprint, _
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc

@frappe.whitelist()
def make_material_transfer(source_name, target_doc=None):
    def set_missing_values(source, target):
        target.purpose = "Material Transfer"
        target.run_method("set_missing_values")

    doc = get_mapped_doc("ITO", source_name, {
		"ITO": {
			"doctype": "Stock Entry",
			"validation": {
				"docstatus": ["=", 1],
			},
			"field_map":{
				"name": "ito",
                "warehouse": "from_warehouse"
			},
		},
		"ITO Item": {
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
