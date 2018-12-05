frappe.ui.form.on("Sales Invoice", {
	refresh: function(frm){
		frm.clear_custom_button();
		frm.set_df_property("project", "read_only", 1);
		frm.set_df_property("is_pos", "hidden", 1);
		frm.set_df_property("update_stock", "hidden", 1);
		var df = frappe.meta.get_docfield("Sales Invoice Item", "barcode", frm.doc.name);
		df.hidden = 1;
	},
	onload: function(frm){
		frm.set_query("rss_sales_order", function(doc) {
			return {
				filters: [
					['golden_status', '=', 'Wait for Delivery and Bill'],
					['customer', '=', doc.customer],
					['status', '!=', 'Completed']
				]
			}
		});
		frm.set_query("rss_sales_person", function(doc) {
			return {
				query: "golden.golden.doctype.employee_settings.employee_settings.employee_query",
				filters: { 'department': 'sales' }
			}
		});
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
	validate: function(frm){
/*
		if(frm.doc.rss_get_item_count == 0){
			msgprint("You have not clicked 'Update Items'");
			validated = false;
		}
*/
	},
/*	rss_get_items: function(frm){
		frm.set_value("rss_get_item_count", "1");
		var tbl = frm.doc.items|| [];
		var i = tbl.length;
		while (i--) {
			if(frm.doc.items[i].sales_order != ""){
				frm.set_value("rss_sales_order", frm.doc.items[i].sales_order);
			}
		}
		frm.events.items_from_delivery(frm);
		frm.refresh_fields();
	},
*/
	rss_get_items: function(frm){
		frm.clear_table("items");
		return frappe.call({
			method: 'golden.golden.selling.get_items_from_dn',
			args: {
				sales_order: frm.doc.rss_sales_order
			},
			callback: function(r, rt) {
				if(r.message) {
					$.each(r.message, function(i, d) {
						var c = frm.add_child("items");
						c.rss_item_code = d.rss_item_code;
						c.item_code = d.item_code;
						c.item_name = d.item_name;
						c.description = d.description;
						c.image = d.image;
						c.qty = d.qty;
						c.stock_uom = d.stock_uom;
						c.uom = d.uom;
						c.conversion_factor = d.conversion_factor;
						c.stock_qty = d.stock_qty;
						c.price_list_rate = d.price_list_rate;
						c.base_price_list_rate = d.base_price_list_rate;
						c.margin_type = d.margin_type;
						c.discount_percentage = d.discount_percentage;
						c.rate = d.rate;
						c.amount = d.amount;
						c.base_rate = d.base_rate;
						c.base_amount = d.base_amount;
						c.net_rate = d.net_rate;
						c.net_amount = d.net_amount;
						c.base_net_rate = d.base_net_rate;
						c.base_net_amount = d.base_net_amount;
						c.income_account = d.income_account;
						c.expense_account = d.expense_account;
						c.warehouse = d.warehouse;
						c.sales_order = d.sales_order;
						c.so_detail = d.so_detail;
						c.delivery_note = d.delivery_note;
						c.dn_detail = d.dn_detail;
						c.picking_order = d.picking_order;
					})
					frm.events.set_parents(frm);
					frm.refresh_fields();
				}
			}
		})
	},
	set_parents: function(frm){
		frappe.call({
			method: "frappe.client.get",
			args: {
				doctype: "Sales Order",
				filters:{
					name: frm.doc.rss_sales_order,
				}
			},
			callback: function (data) {
				if(data.message){
					frm.set_value("rss_sales_person", data.message.rss_sales_person);
					frm.set_value("rss_sales_name", data.message.rss_sales_name);
					frm.set_value("selling_price_list", data.message.selling_price_list);
					frm.set_value("employee", data.message.rss_sales_person);
				}
			}
		})
	},
	rss_sales_person: function(frm) {
		if(frm.doc.rss_sales_person){
			frm.set_value("employee", frm.doc.rss_sales_person);
		}else{
			frm.set_value("employee", "");
		}
	},
});
frappe.ui.form.on("Sales Invoice Item", {
	rss_item_code: function(frm, cdt, cdn){
		row = locals[cdt][cdn];
		frappe.model.set_value(cdt, cdn, "item_code", row.rss_item_code);
	},
	validate: function(frm, cdt, cdn){
		row = locals[cdt][cdn];
		frappe.model.set_value(cdt, cdn, "picking_order", "");
	}
})
