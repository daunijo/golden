from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("Buying"),
			"items": [
				{
					"type": "doctype",
					"name": "Purchase Return",
					"description": _("Purchase Return.")
				},
			]
		},
		{
			"label": _("Selling"),
			"items": [
				{
					"type": "doctype",
					"name": "Sales Return",
					"description": _("Sales Return.")
				},
				{
					"type": "doctype",
					"name": "Sales Invoice Summary",
					"description": _("Sales Invoice Summary.")
				},
				{
					"type": "doctype",
					"name": "Summary Generator",
					"description": _("Summary Generator.")
				},
				{
					"type": "doctype",
					"name": "Invoice Keeptrack",
					"description": _("Invoice Keeptrack.")
				},
			]
		},
		{
			"label": _("Stock"),
			"items": [
				{
					"type": "doctype",
					"name": "Picking Order",
					"description": _("Picking Order.")
				},
				{
					"type": "doctype",
					"name": "Batch Picking",
					"description": _("Batch Picking.")
				},
				{
					"type": "doctype",
					"name": "Transfer Order",
					"description": _("Transfer Order.")
				},
				{
					"type": "doctype",
					"name": "Packing",
					"description": _("Packing.")
				},
				{
					"type": "doctype",
					"name": "Delivery Order",
					"description": _("Delivery Order.")
				},
				{
					"type": "doctype",
					"name": "Delivery Keeptrack",
					"description": _("Delivery Keeptrack.")
				},
				{
					"type": "doctype",
					"name": "Delivery Return",
					"description": _("Delivery Return.")
				},
				{
					"type": "doctype",
					"name": "Receive Order",
					"description": _("Receive Order.")
				},
			]
		},
		{
			"label": _("Payment"),
			"items": [
				{
					"type": "doctype",
					"name": "Payment Entry Receive",
					"description": _("Payment Entry Receive.")
				},
				{
					"type": "doctype",
					"name": "Payment Entry Pay",
					"description": _("Payment Entry Pay.")
				},
			]
		},
		{
			"label": _("Masters"),
			"items": [
				{
					"type": "doctype",
					"name": "City",
					"description": _("City.")
				},
				{
					"type": "doctype",
					"name": "Employee Settings",
					"description": _("Employee Settings.")
				},
				{
					"type": "doctype",
					"name": "Expedition",
					"description": _("Expedition.")
				},
				{
					"type": "doctype",
					"name": "Region",
					"description": _("Region.")
				},
				{
					"type": "doctype",
					"name": "Warehouse Routing",
					"description": _("Warehouse Routing.")
				},
			]
		},
		{
			"label": _("Commission"),
			"items": [
				{
					"type": "doctype",
					"name": "Commission Percentage",
					"description": _("Commission Percentage.")
				},
				{
					"type": "doctype",
					"name": "Purchase Budget",
					"description": _("Purchase Budget.")
				},
				{
					"type": "doctype",
					"name": "Sales Commission",
					"description": _("Sales Commission.")
				},
				{
					"type": "doctype",
					"name": "Sales Target",
					"description": _("Sales Target.")
				},
			]
		},
		{
			"label": _("Report"),
			"items": [
				{
					"type": "report",
					"name": "Annual Sold Summary Report",
					"doctype": "Receive Order",
					"is_query_report": True
				},
				{
					"type": "report",
					"name": "Dynamic Item Report",
					"doctype": "Item",
					"is_query_report": True
				},
				{
					"type": "report",
					"name": "Dynamic Item Report - Purchase",
					"doctype": "Item",
					"is_query_report": True
				},
				{
					"type": "report",
					"name": "Purchase Analysis",
					"doctype": "Item",
					"is_query_report": True
				},
				{
					"type": "report",
					"name": "Purchase Analysis Per Item",
					"doctype": "Item",
					"is_query_report": True
				},
				{
					"type": "report",
					"name": "Purchase By Item Group",
					"doctype": "Purchase Budget",
					"is_query_report": True
				},
				{
					"type": "report",
					"name": "Purchase & Sales Trends",
					"doctype": "Item",
					"is_query_report": True
				},
				{
					"type": "page",
					"name": "sales-analytics-sp",
					"label": _("Sales Analytics - Sales Person"),
					"icon": "fa fa-bar-chart",
				},
				{
					"type": "report",
					"name": "Stock Card",
					"doctype": "Stock Ledger Entry",
					"is_query_report": True
				},
				{
					"type": "report",
					"name": "Stock Card Sales",
					"doctype": "Stock Ledger Entry",
					"is_query_report": True
				},
				{
					"type": "report",
					"name": "Stock Card Purchasing",
					"doctype": "Stock Ledger Entry",
					"is_query_report": True
				},
				{
					"type": "report",
					"name": "Stock Card by Location",
					"doctype": "Stock Ledger Entry",
					"is_query_report": True
				},
			]
		},
	]
