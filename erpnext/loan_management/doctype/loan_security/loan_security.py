# Copyright (c) 2019, Sparrownova Technologies and contributors
# For license information, please see license.txt


# import frappe
from frappe.model.document import Document


class LoanSecurity(Document):
	def autoname(self):
		self.name = self.loan_security_name
