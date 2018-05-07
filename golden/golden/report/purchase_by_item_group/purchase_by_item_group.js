// Copyright (c) 2016, RSS and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Purchase By Item Group"] = {
	"filters": [
		{
			"fieldname":"purchase_budget",
			"label": __("Purchase Budget"),
			"fieldtype": "Link",
			"options": "Purchase Budget",
			"reqd": 1,
			"get_query": function() {
				return {
					"doctype": "Purchase Budget",
					"filters": {
						"docstatus": 1,
					}
				}
			}
		},
	]
}
