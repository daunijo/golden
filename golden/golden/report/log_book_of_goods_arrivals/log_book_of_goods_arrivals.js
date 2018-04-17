// Copyright (c) 2016, RSS and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Log Book of Goods Arrivals"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": __("From Modified Date"),
			"fieldtype": "Date",
			"width": "80",
			"default": frappe.datetime.month_start()
		},
		{
			"fieldname":"to_date",
			"label": __("To Modified Date"),
			"fieldtype": "Date",
			"width": "80",
			"default": frappe.datetime.month_end()
		}
	]
}
