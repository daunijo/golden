// Copyright (c) 2016, RSS and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Stock Card Purchasing"] = {
	"filters": [
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
			"reqd": 1
		},
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			"reqd": 1
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1
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
			"fieldname":"item_code",
			"label": __("Item"),
			"fieldtype": "Link",
			"options": "Item"
		},
		{
			"fieldname":"item_group",
			"label": __("Item Group"),
			"fieldtype": "Link",
			"options": "Item Group"
		},
		{
			"fieldname":"brand",
			"label": __("Brand"),
			"fieldtype": "Link",
			"options": "Brand"
		},
		{
			"fieldname":"voucher_type",
			"label": __("Voucher Type"),
			"fieldtype": "Select",
			"options": [
				{ "value": "Transfer Order", "label": __("Transfer Order") },
				{ "value": "Delivery Order", "label": __("Delivery Order") },
				{ "value": "Stock Reconciliation", "label": __("Stock Reconciliation") },
				{ "value": "Sales Return", "label": __("Sales Return") },
				{ "value": "Receive Order", "label": __("Receive Order") },
				{ "value": "Purchase Return", "label": __("Purchase Return") }
			],
		},
	]
}
