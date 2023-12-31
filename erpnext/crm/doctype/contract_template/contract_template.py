# Copyright (c) 2018, Sparrownova Technologies and contributors
# For license information, please see license.txt


import json

import frappe
from frappe.model.document import Document
from frappe.utils.jinja import validate_template


class ContractTemplate(Document):
	def validate(self):
		if self.contract_terms:
			validate_template(self.contract_terms)


@frappe.whitelist()
def get_contract_template(template_name, doc):
	if isinstance(doc, str):
		doc = json.loads(doc)

	contract_template = frappe.get_doc("Contract Template", template_name)
	contract_terms = None

	if contract_template.contract_terms:
		contract_terms = frappe.render_template(contract_template.contract_terms, doc)

	return {"contract_template": contract_template, "contract_terms": contract_terms}
