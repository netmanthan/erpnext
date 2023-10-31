// Copyright (c) 2016, NETMANTHAN TECHNOLOGIES. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Item Price Stock"] = {
	"filters": [
		{
			"fieldname":"item_code",
			"label": __("Item"),
			"fieldtype": "Link",
			"options": "Item"
		}
	]
}
