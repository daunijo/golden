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
	],
	onload: function(report) {
		report.page.add_inner_button(__("Purchase Analysis"), function() {
			var filters = report.get_values();
			frappe.set_route('query-report', 'Purchase Analysis');
		}, __('Purchase'));
		report.page.add_inner_button(__("Purchase By Item Group"), function() {
			var filters = report.get_values();
			frappe.set_route('query-report', 'Purchase By Item Group');
		}, __('Purchase'));
	}
}
