from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("Receiving"),
			"items": [
				{
					"type": "doctype",
					"name": "Receive Order",
					"description": _("Receive Order.")
				},
			]
		}
    ]
