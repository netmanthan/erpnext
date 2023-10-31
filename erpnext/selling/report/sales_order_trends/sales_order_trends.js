// Copyright (c) 2015, Sparrownova Technologies and Contributors
// License: GNU General Public License v3. See license.txt

frappe.require("assets/erpnext/js/sales_trends_filters.js", function() {
	frappe.query_reports["Sales Order Trends"] = {
		filters: erpnext.get_sales_trends_filters()
	}
});
