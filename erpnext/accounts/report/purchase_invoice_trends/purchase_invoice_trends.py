# Copyright (c) 2015, NETMANTHAN TECHNOLOGIES. and Contributors
# License: GNU General Public License v3. See license.txt


from erpnext.controllers.trends import get_columns, get_data


def execute(filters=None):
	if not filters:
		filters = {}
	data = []
	conditions = get_columns(filters, "Purchase Invoice")
	data = get_data(filters, conditions)

	return conditions["columns"], data
