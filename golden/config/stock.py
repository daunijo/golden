from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("Stock Transactions"),
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
			"label": _("Reports"),
			"items": [
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
			]
		}
    ]
