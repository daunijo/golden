# -*- coding: utf-8 -*-
# Copyright (c) 2018, RSS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import msgprint, _

class Expedition(Document):
	def validate(self):
		if not self.buying and not self.selling:
			frappe.throw(_("You must check buying and/or selling"))
