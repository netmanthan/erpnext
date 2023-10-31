// Copyright (c) 2015, Sparrownova Technologies and Contributors
// License: GNU General Public License v3. See license.txt

frappe.require("assets/erpnext/js/purchase_trends_filters.js", function() {
	frappe.query_reports["Purchase Invoice Trends"] = {
		filters: erpnext.get_purchase_trends_filters()
	}
});
