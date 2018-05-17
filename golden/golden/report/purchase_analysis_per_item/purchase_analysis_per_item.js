// Copyright (c) 2016, RSS and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Purchase Analysis Per Item"] = {
	"filters": [
		{
			"fieldname":"item_group",
			"label": __("Item Group"),
			"fieldtype": "Link",
			"options": "Item Group",
			"reqd": 1,
			"get_query": function() {
				return {
					"doctype": "Item Group",
					"filters": {
						"is_group": 0,
					}
				}
			}
		},
	]
}
