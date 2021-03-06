// Copyright (c) 2016, RSS and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Stock Position"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"width": "80",
			"reqd": 1,
			"default": frappe.sys_defaults.year_start_date,
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"width": "80",
			"reqd": 1,
			"default": frappe.datetime.get_today()
		},
		{
			"fieldname": "item_group",
			"label": __("Item Group"),
			"fieldtype": "Link",
			"width": "80",
			"options": "Item Group"
		},
		{
			"fieldname": "item_code",
			"label": __("Item"),
			"fieldtype": "Link",
			"width": "80",
			"options": "Item"
		},
		{
			"fieldname":"warehouse",
			"label": __("Warehouse"),
			"fieldtype": "Link",
			"options": "Warehouse",
			"get_query": function() {
				return{
					filters: {
						'is_group': 1,
						'type': "Warehouse"
					}
				};
			}
		},
		{
			"fieldname":"section",
			"label": __("Section"),
			"fieldtype": "Link",
			"options": "Warehouse",
			"get_query": function() {
				return{
					filters: {
						'is_group': 1,
						'type': "Section"
					}
				};
			}
		},
		{
			"fieldname":"location",
			"label": __("Location"),
			"fieldtype": "Link",
			"options": "Warehouse",
			"get_query": function() {
				return{
					filters: {
						'is_group': 0,
						'type': "Location"
					}
				};
			}
		},
		{
			"fieldname": "show_variant_attributes",
			"label": __("Show Variant Attributes"),
			"fieldtype": "Check"
		},
	]
}
