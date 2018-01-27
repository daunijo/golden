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
app_include_css = "/files/custom.css"
# app_include_js = "/assets/golden/js/golden.js"

# include js, css files in header of web template
# web_include_css = "/assets/golden/css/golden.css"
# web_include_js = "/assets/golden/js/golden.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

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

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    "Sales Order": {
        "on_submit": [
            "golden.golden.reference.submit_sales_order",
            "golden.golden.reference.submit_sales_order_2",
            "golden.golden.reference.submit_sales_order_3",
            "golden.golden.reference.submit_sales_order_4"
        ],
        "on_cancel": [
            "golden.golden.reference.cancel_sales_order",
            "golden.golden.reference.cancel_sales_order_2"
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
