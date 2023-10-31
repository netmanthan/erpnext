# Copyright (c) 2023, Sparrownova Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _, qb
from frappe.model.document import Document
from frappe.utils.data import comma_and


class RepostAccountingLedger(Document):
	def __init__(self, *args, **kwargs):
		super(RepostAccountingLedger, self).__init__(*args, **kwargs)
		self._allowed_types = set(
			["Purchase Invoice", "Sales Invoice", "Payment Entry", "Journal Entry"]
		)

	def validate(self):
		self.validate_vouchers()
		self.validate_for_closed_fiscal_year()
		self.validate_for_deferred_accounting()

	def validate_for_deferred_accounting(self):
		sales_docs = [x.voucher_no for x in self.vouchers if x.voucher_type == "Sales Invoice"]
		purchase_docs = [x.voucher_no for x in self.vouchers if x.voucher_type == "Purchase Invoice"]
		validate_docs_for_deferred_accounting(sales_docs, purchase_docs)

	def validate_for_closed_fiscal_year(self):
		if self.vouchers:
			latest_pcv = (
				frappe.db.get_all(
					"Period Closing Voucher",
					filters={"company": self.company},
					order_by="posting_date desc",
					pluck="posting_date",
					limit=1,
				)
				or None
			)
			if not latest_pcv:
				return

			for vtype in self._allowed_types:
				if names := [x.voucher_no for x in self.vouchers if x.voucher_type == vtype]:
					latest_voucher = frappe.db.get_all(
						vtype,
						filters={"name": ["in", names]},
						pluck="posting_date",
						order_by="posting_date desc",
						limit=1,
					)[0]
					if latest_voucher and latest_pcv[0] >= latest_voucher:
						frappe.throw(_("Cannot Resubmit Ledger entries for vouchers in Closed fiscal year."))

	def validate_vouchers(self):
		if self.vouchers:
			# Validate voucher types
			voucher_types = set([x.voucher_type for x in self.vouchers])
			if disallowed_types := voucher_types.difference(self._allowed_types):
				frappe.throw(
					_("{0} types are not allowed. Only {1} are.").format(
						frappe.bold(comma_and(list(disallowed_types))),
						frappe.bold(comma_and(list(self._allowed_types))),
					)
				)

	def get_existing_ledger_entries(self):
		vouchers = [x.voucher_no for x in self.vouchers]
		gl = qb.DocType("GL Entry")
		existing_gles = (
			qb.from_(gl)
			.select(gl.star)
			.where((gl.voucher_no.isin(vouchers)) & (gl.is_cancelled == 0))
			.run(as_dict=True)
		)
		self.gles = frappe._dict({})

		for gle in existing_gles:
			self.gles.setdefault((gle.voucher_type, gle.voucher_no), frappe._dict({})).setdefault(
				"existing", []
			).append(gle.update({"old": True}))

	def generate_preview_data(self):
		self.gl_entries = []
		self.get_existing_ledger_entries()
		for x in self.vouchers:
			doc = frappe.get_doc(x.voucher_type, x.voucher_no)
			if doc.doctype in ["Payment Entry", "Journal Entry"]:
				gle_map = doc.build_gl_map()
			else:
				gle_map = doc.get_gl_entries()

			old_entries = self.gles.get((x.voucher_type, x.voucher_no))
			if old_entries:
				self.gl_entries.extend(old_entries.existing)
			self.gl_entries.extend(gle_map)

	@frappe.whitelist()
	def generate_preview(self):
		from erpnext.accounts.report.general_ledger.general_ledger import get_columns as get_gl_columns

		gl_columns = []
		gl_data = []

		self.generate_preview_data()
		if self.gl_entries:
			filters = {"company": self.company, "include_dimensions": 1}
			for x in get_gl_columns(filters):
				if x["fieldname"] == "gl_entry":
					x["fieldname"] = "name"
				gl_columns.append(x)

			gl_data = self.gl_entries
		rendered_page = frappe.render_template(
			"erpnext/accounts/doctype/repost_accounting_ledger/repost_accounting_ledger.html",
			{"gl_columns": gl_columns, "gl_data": gl_data},
		)

		return rendered_page

	def on_submit(self):
		if len(self.vouchers) > 1:
			job_name = "repost_accounting_ledger_" + self.name
			frappe.enqueue(
				method="erpnext.accounts.doctype.repost_accounting_ledger.repost_accounting_ledger.start_repost",
				account_repost_doc=self.name,
				is_async=True,
				job_name=job_name,
			)
			frappe.msgprint(_("Repost has started in the background"))
		else:
			start_repost(self.name)


@frappe.whitelist()
def start_repost(account_repost_doc=str) -> None:
	if account_repost_doc:
		repost_doc = frappe.get_doc("Repost Accounting Ledger", account_repost_doc)

		if repost_doc.docstatus == 1:
			# Prevent repost on invoices with deferred accounting
			repost_doc.validate_for_deferred_accounting()

			for x in repost_doc.vouchers:
				doc = frappe.get_doc(x.voucher_type, x.voucher_no)

				if repost_doc.delete_cancelled_entries:
					frappe.db.delete("GL Entry", filters={"voucher_type": doc.doctype, "voucher_no": doc.name})
					frappe.db.delete(
						"Payment Ledger Entry", filters={"voucher_type": doc.doctype, "voucher_no": doc.name}
					)

				if doc.doctype in ["Sales Invoice", "Purchase Invoice"]:
					if not repost_doc.delete_cancelled_entries:
						doc.docstatus = 2
						doc.make_gl_entries_on_cancel()

					doc.docstatus = 1
					doc.make_gl_entries()

				elif doc.doctype in ["Payment Entry", "Journal Entry"]:
					if not repost_doc.delete_cancelled_entries:
						doc.make_gl_entries(1)
					doc.make_gl_entries()

				frappe.db.commit()


def validate_docs_for_deferred_accounting(sales_docs, purchase_docs):
	docs_with_deferred_revenue = frappe.db.get_all(
		"Sales Invoice Item",
		filters={"parent": ["in", sales_docs], "docstatus": 1, "enable_deferred_revenue": True},
		fields=["parent"],
		as_list=1,
	)

	docs_with_deferred_expense = frappe.db.get_all(
		"Purchase Invoice Item",
		filters={"parent": ["in", purchase_docs], "docstatus": 1, "enable_deferred_expense": 1},
		fields=["parent"],
		as_list=1,
	)

	if docs_with_deferred_revenue or docs_with_deferred_expense:
		frappe.throw(
			_("Documents: {0} have deferred revenue/expense enabled for them. Cannot repost.").format(
				frappe.bold(comma_and([x[0] for x in docs_with_deferred_expense + docs_with_deferred_revenue]))
			)
		)
