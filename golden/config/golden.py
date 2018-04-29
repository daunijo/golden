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
					"name": "Picking",
					"description": _("Picking.")
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
			"label": _("Masters"),
			"items": [
				{
					"type": "doctype",
					"name": "Expedition",
					"description": _("Expedition.")
				},
			]
		},
		{
			"label": _("Commission"),
			"items": [
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
			]
		},
	]
