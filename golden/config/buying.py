from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("Purchasing"),
			"items": [
				{
					"type": "doctype",
					"name": "Purchase Return",
					"description": _("Purchase Return.")
				},
			]
		}
    ]
