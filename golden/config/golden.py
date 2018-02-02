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
					"name": "ITO",
					"description": _("ITO.")
				},
				{
					"type": "doctype",
					"name": "Packing",
					"description": _("Packing.")
				},
				{
					"type": "doctype",
					"name": "Delivery Keeptrack",
					"description": _("Delivery Keeptrack.")
				},
			]
		},
	]
