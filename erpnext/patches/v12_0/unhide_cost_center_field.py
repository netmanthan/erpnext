# Copyright (c) 2017, NETMANTHAN TECHNOLOGIES and Contributors
# License: GNU General Public License v3. See license.txt


import frappe


def execute():
	frappe.db.sql(
		"""
		DELETE FROM `tabProperty Setter`
		WHERE doc_type in ('Sales Invoice', 'Purchase Invoice', 'Payment Entry')
		AND field_name = 'cost_center'
		AND property = 'hidden'
	"""
	)
