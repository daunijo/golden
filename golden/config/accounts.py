from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("Billing"),
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
		}
    ]
