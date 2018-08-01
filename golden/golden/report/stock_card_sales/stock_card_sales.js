// Copyright (c) 2016, RSS and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Stock Card Sales"] = {
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
			"fieldname":"item_code",
			"label": __("Item"),
			"fieldtype": "Link",
			"options": "Item",
			"reqd": 1
		},
		{
			"fieldname":"voucher_type",
			"label": __("Voucher Type"),
			"fieldtype": "Select",
			"options": [
				{ "value": "All", "label": __("All") },
				{ "value": "Transfer Order", "label": __("Transfer Order") },
				{ "value": "Delivery Order", "label": __("Delivery Order") },
				{ "value": "Stock Reconciliation", "label": __("Stock Reconciliation") },
				{ "value": "Sales Return", "label": __("Sales Return") },
				{ "value": "Receive Order", "label": __("Receive Order") },
				{ "value": "Purchase Return", "label": __("Purchase Return") }
			],
			"default": "All",
		},
		{
			"fieldname":"price_list",
			"label": __("Price List"),
			"fieldtype": "Link",
			"options": "Price List",
			"get_query": function() {
				return{
					filters: {
						'enabled': 1,
						'selling': 1
					}
				};
			}
		},
	]
}
