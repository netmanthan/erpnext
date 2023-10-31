# Copyright (c) 2015, NETMANTHAN TECHNOLOGIES. and Contributors
# License: GNU General Public License v3. See license.txt


import frappe


def execute():
	frappe.delete_doc("Page", "modules_setup")
