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
