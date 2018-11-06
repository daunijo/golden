frappe.ui.form.on("Purchase Order", {
	onload: function(frm){
		frm.set_query("rss_item_code", "items", function(doc, cdt, cdn) {
			var row = locals[cdt][cdn];
			return {
				query: "golden.golden.stock.item_query"
			}
		});
		frm.set_query("uom", "items", function(doc, cdt, cdn) {
			var row = locals[cdt][cdn];
			return {
				query: "golden.golden.stock.uom_query",
				filters: { 'item_code': row.rss_item_code }
			}
		});
	},
	refresh: function(frm){
		var df1 = frappe.meta.get_docfield("Purchase Order Item","item_name", frm.doc.name);
		df1.read_only = 1;
	},
})
frappe.ui.form.on('Purchase Order Item', {
	rss_item_code: function(frm, cdt, cdn){
		row = locals[cdt][cdn];
		frappe.model.set_value(cdt, cdn, "item_code", row.rss_item_code);
	},
})
