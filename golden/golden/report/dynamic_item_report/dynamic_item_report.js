// Copyright (c) 2016, RSS and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Dynamic Item Report"] = {
	"filters": [
		{
			"fieldname":"limit",
			"label": __("Limit"),
			"fieldtype": "Select",
			"options": '20\n100\n500\nNo Limit',
			"default": "20"
		},
		{
			"fieldname":"item_code",
			"label": __("Item Code"),
			"fieldtype": "Link",
			"options": "Item"
		},
		{
			"fieldname":"price_list",
			"label": __("Price List"),
			"fieldtype": "Link",
			"options": "Price List",
			"get_query": function() {
				return {
					"doctype": "Price List",
					"filters": {
						"selling": 1
					}
				}
			}
		},
		{
			"fieldname":"warehouse",
			"label": __("Warehouse"),
			"fieldtype": "Link",
			"options": "Warehouse",
			"get_query": function() {
				return {
					"doctype": "Warehouse",
					"filters": {
						"type": "Warehouse",
						"disabled": 0
					}
				}
			}
		},
	]
}
