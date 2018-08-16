# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"module_name": "Golden",
			"color": "#F39C12",
			"icon": "fa fa-rocket",
			"type": "module",
			"label": _("Golden")
		},
		{
			"module_name": "RS",
			"color": "#4286f4",
			"icon": "octicon octicon-database",
			"label": _("Receiver Staff"),
			"type": "module"
		},
	]
