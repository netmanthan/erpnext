// Copyright (c) 2019, Sparrownova Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on('Quality Feedback', {
	template: function(frm) {
		if (frm.doc.template) {
			frm.call('set_parameters');
		}
	}
});
