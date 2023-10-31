// Copyright (c) 2019, NETMANTHAN TECHNOLOGIES. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.ui.form.on('Newsletter', {
	refresh() {
		erpnext.toggle_naming_series();
	}
});
