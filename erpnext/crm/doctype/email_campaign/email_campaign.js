// Copyright (c) 2019, Sparrownova Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on('Email Campaign', {
	email_campaign_for: function(frm) {
		frm.set_value('recipient', '');
	}
});
