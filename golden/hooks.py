# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "golden"
app_title = "Golden"
app_publisher = "RSS"
app_description = "App for Golden"
app_icon = "fa fa-rocket"
app_color = "#F39C12"
app_email = "develop@ridhosribumi.com"
app_license = "RSS"
fixtures = ["Custom Script", "Custom Field"]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/golden/css/golden.css"
app_include_css = "/assets/golden/css/custom.css"
# app_include_js = "/assets/golden/js/golden.js"

# include js, css files in header of web template
# web_include_css = "/assets/golden/css/golden.css"
# web_include_js = "/assets/golden/js/golden.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
	"Journal Entry": "public/js/journal_entry.js",
	"Warehouse": "public/js/warehouse.js",
	"Stock Entry": "public/js/stock_entry.js",
	"Stock Reconciliation": "public/js/stock_reconciliation.js",
	"Item": "public/js/item.js",
	"Purchase Order": "public/js/purchase_order.js",
	"Purchase Receipt": "public/js/purchase_receipt.js",
	"Purchase Invoice": "public/js/purchase_invoice.js",
	"Sales Order": "public/js/sales_order.js",
	"Delivery Note": "public/js/delivery_note.js",
	"Sales Invoice": "public/js/sales_invoice.js"
}
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
doctype_tree_js = {
	"Warehouse" : "public/js/warehouse_tree.js"
}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}


# Home Pages
# ----------
website_context = {
	"favicon": 	"/files/icon.png"
}
# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "golden.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "golden.install.before_install"
# after_install = "golden.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "golden.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }
on_login = "golden.golden.reference.login_action"

dump_report_map = "golden.golden.report_data_map.data_map"

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    "Sales Order": {
		"on_change":[
			"golden.golden.reference.change_sales_order"
		],
		"validate": "golden.golden.reference.validate_sales_order",
        "on_submit": [
            "golden.golden.reference.submit_sales_order",
            "golden.golden.reference.submit_sales_order_2",
            "golden.golden.reference.submit_sales_order_3",
            "golden.golden.reference.submit_sales_order_4",
            "golden.golden.reference.submit_sales_order_5",
            "golden.golden.reference.submit_sales_order_6",
            "golden.golden.reference.cancel_sales_order_4",
            "golden.golden.reference.submit_sales_order_7"
        ],
        "on_cancel": [
            "golden.golden.reference.cancel_sales_order",
            "golden.golden.reference.cancel_sales_order_2",
            "golden.golden.reference.cancel_sales_order_3",
            "golden.golden.reference.submit_sales_order_4",
            "golden.golden.reference.submit_sales_order_6",
            "golden.golden.reference.cancel_sales_order_4",
            "golden.golden.reference.cancel_sales_order_5"
        ]
    },
    "Delivery Note": {
        "on_submit": [
            "golden.golden.reference.submit_delivery_note"
        ],
        "on_cancel": [
            "golden.golden.reference.cancel_delivery_note_1",
            "golden.golden.reference.cancel_delivery_note_2"
        ]
    },
    "Sales Invoice": {
        "validate": [
            "golden.golden.reference.validate_sales_invoice"
        ],
        "on_submit": [
            "golden.golden.reference.submit_sales_invoice"
        ],
        "on_cancel": [
            "golden.golden.reference.cancel_sales_invoice"
        ]
    },
    "Purchase Invoice": {
        "validate": "golden.golden.reference.validate_purchase_invoice",
        "on_submit": [
			"golden.golden.reference.submit_purchase_invoice_1",
			"golden.golden.reference.submit_purchase_invoice_2"
		],
        "on_cancel": [
			"golden.golden.reference.cancel_purchase_invoice_1",
			"golden.golden.reference.cancel_purchase_invoice_2"
		]
    },
    "Stock Entry": {
        "on_submit": [
            "golden.golden.reference.submit_stock_entry"
            # "golden.golden.reference.cancel_sales_order_3",
            # "golden.golden.reference.cancel_sales_order_4"
        ]
    },
    "Warehouse": {
		"validate": "golden.golden.reference.validate_warehouse",
        "on_update": [
			"golden.golden.reference.update_warehouse",
			"golden.golden.reference.update_warehouse_2"
		]
    }
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"golden.tasks.all"
# 	],
# 	"daily": [
# 		"golden.tasks.daily"
# 	],
# 	"hourly": [
# 		"golden.tasks.hourly"
# 	],
# 	"weekly": [
# 		"golden.tasks.weekly"
# 	]
# 	"monthly": [
# 		"golden.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "golden.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "golden.event.get_events"
# }
