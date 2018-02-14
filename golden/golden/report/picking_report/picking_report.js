// Copyright (c) 2016, RSS and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Picking Report"] = {
	"filters": [
		{
			"fieldname": "picking",
					"label": __("Picking"),
					"fieldtype": "Link",
					"options": "Picking"
		},
		{
			"fieldname": "sales_order",
					"label": __("Sales Order"),
					"fieldtype": "Link",
					"options": "Sales Order"
		},
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"width": "80",
			"default": frappe.datetime.month_start()
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"width": "80",
			"default": frappe.datetime.month_end()
		},
	],
}
