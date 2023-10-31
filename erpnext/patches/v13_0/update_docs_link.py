# Copyright (c) 2023, Sparrownova Technologies and Contributors
# License: MIT. See LICENSE


import frappe


def execute():
	navbar_settings = frappe.get_single("Navbar Settings")
	for item in navbar_settings.help_dropdown:
		if item.is_standard and item.route == "https://sparrownova.com/docs/user/manual":
			item.route = "https://docs.sparrownova.com/docs/v14/user/manual/en/introduction"

	navbar_settings.save()
