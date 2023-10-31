// Copyright (c) 2022, Sparrownova Technologies and contributors
// For license information, please see license.txt

frappe.listview_settings['Subcontracting Order'] = {
	get_indicator: function (doc) {
		const status_colors = {
			"Draft": "grey",
			"Open": "orange",
			"Partially Received": "yellow",
			"Completed": "green",
			"Partial Material Transferred": "purple",
			"Material Transferred": "blue",
			"Closed": "red",
			"Cancelled": "red",
		};
		return [__(doc.status), status_colors[doc.status], "status,=," + doc.status];
	},
};