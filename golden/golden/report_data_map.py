from __future__ import unicode_literals

data_map = {
	"Employee": {
		"columns": ["name"],
		"conditions": ["status = 'Active'"],
		"order_by": "name"
	},
	"Sales Invoice": {
		"columns": ["name", "customer", "posting_date", "company", "employee"],
		"conditions": ["docstatus=1"],
		"order_by": "posting_date",
		"links": {
            "employee":["Employee", "name"]
		}
	},
	"Sales Order": {
		"columns": ["name", "customer", "transaction_date as posting_date", "company", "employee"],
		"conditions": ["docstatus=1"],
		"order_by": "transaction_date",
		"links": {
            "employee":["Employee", "name"]
		}
	},
	"Delivery Note": {
		"columns": ["name", "customer", "posting_date", "company", "employee"],
		"conditions": ["docstatus=1"],
		"order_by": "posting_date",
		"links": {
            "employee":["Employee", "name"]
		}
	},
}
