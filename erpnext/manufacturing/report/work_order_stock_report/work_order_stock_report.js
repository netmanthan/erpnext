// Copyright (c) 2016, Sparrownova Technologies and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Work Order Stock Report"] = {
	"filters": [
		{
			"fieldname": "warehouse",
			"label": __("Warehouse"),
			"fieldtype": "Link",
			"options": "Warehouse"
		}
	]
}
