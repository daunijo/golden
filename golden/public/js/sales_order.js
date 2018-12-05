frappe.ui.form.on("Sales Order", {
	refresh: function(frm){
		//frm.clear_custom_button(__('Invoice'));
		//cur_frm.page.get_inner_group_button(__("Invoice")).find("button").addClass("hide");
		if(frm.doc.__islocal){
			frm.set_value("golden_status", "Draft");
		}
		var df1 = frappe.meta.get_docfield("Sales Order Item","ordered_qty", cur_frm.doc.name);
		df1.hidden = 1;
		var df2 = frappe.meta.get_docfield("Sales Order Item","delivered_qty", cur_frm.doc.name);
		df2.hidden = 1;
		var df3 = frappe.meta.get_docfield("Sales Order Item","billed_amt", cur_frm.doc.name);
		df3.hidden = 1;
		var df4 = frappe.meta.get_docfield("Sales Order Item","valuation_rate", cur_frm.doc.name);
		df4.hidden = 1;
		var df5 = frappe.meta.get_docfield("Sales Order Item","gross_profit", cur_frm.doc.name);
		df5.hidden = 1;
		frm.set_query("uom", "items", function(doc, cdt, cdn) {
			var row = locals[cdt][cdn];
			return {
				query: "golden.golden.stock.uom_query",
				filters: { 'item_code': row.rss_item_code }
			}
		});
	},
	onload: function(frm){
		frm.set_query('rss_warehouse', function(doc) {
			return {
				filters: {
					"is_group": 1,
					"type": "Warehouse"
				}
			}
		});
		frm.set_query("warehouse", "replenishment_warehouse", function(doc, cdt, cdn) {
			var row = locals[cdt][cdn];
			return {
				filters: {
					"is_group": 1,
					"type": "Warehouse"
				}
			}
		});
		frm.set_query("rss_item_code", "items", function(doc, cdt, cdn) {
			var row = locals[cdt][cdn];
			return {
				query: "golden.golden.stock.item_query"
			}
		});
		frm.set_query("rss_sales_person", function(doc) {
			return {
				query: "golden.golden.doctype.employee_settings.employee_settings.employee_query",
				filters: { 'department': 'sales' }
			}
		});
		frm.set_query("default_gudang", "items", function(doc, cdt, cdn) {
			var d = locals[cdt][cdn];
			return {
				filters: [
					['is_group', '=', 1]
				]
			}
		});
		frm.set_query("default_section", "items", function (doc, cdt, cdn) {
			var row = locals[cdt][cdn];
			return {
				filters: {
					'is_group': 1,
					'type': 'Section',
					'parent': row.default_gudang
				}
			}
		});
		frm.set_query("default_location", "items", function (doc, cdt, cdn) {
			var row = locals[cdt][cdn];
			return {
				filters: {
					'is_group': 0,
					'type': 'Location',
					'parent': row.default_section
				}
			}
		});
	},
	validate: function(frm){
		frm.doc.title = frm.doc.customer
	},
	customer: function(frm){
		if(frm.doc.customer){
			frappe.call({
				method: "frappe.client.get",
				args: {
					doctype: "Customer",
					filters:{
						name: frm.doc.customer,
					}
				},
				callback: function (data) {
					if(data.message){
						frm.set_value("rss_sales_person", data.message.rss_sales_person);
						frm.set_value("rss_sales_name", data.message.rss_sales_name);
					}
				}
			})
		}else{
			frm.set_value("rss_sales_person", "");
			frm.set_value("rss_sales_name", "");
		}
	},
	rss_sales_person: function(frm) {
		if(frm.doc.rss_sales_person){
			frm.set_value("employee", frm.doc.rss_sales_person);
		}else{
			frm.set_value("employee", "");
		}
	},
	template_warehouse: function(frm) {
		if(frm.doc.template_warehouse){
			frm.events.get_warehouse_from_template(frm);
			frm.events.get_detail_template_warehouse(frm);
		}
	},
	get_warehouse_from_template: function(frm) {
		frappe.call({
			method: "frappe.client.get",
			args:{
				doctype: "Warehouse Routing",
				filters:{
					name: frm.doc.template_warehouse
				}
			},
			callback: function(data){
				frm.set_value("rss_warehouse", data.message.warehouse);
			}
		});
	},
	get_detail_template_warehouse: function(frm) {
		frm.clear_table("replenishment_warehouse");
		return frappe.call({
			method: 'golden.golden.doctype.warehouse_routing.warehouse_routing.get_template_warehouse',
			args: {
				tw: frm.doc.template_warehouse || undefined
			},
			callback: function(r, rt) {
				if(r.message) {
					$.each(r.message, function(i, d) {
						var c = frm.add_child("replenishment_warehouse");
						c.warehouse = d.warehouse;
					})
					frm.refresh_fields();
				}
			}
		});
	},
})
frappe.ui.form.on('Sales Order Item', {
	rss_item_code: function(frm, cdt, cdn){
		row = locals[cdt][cdn];
		frappe.model.set_value(cdt, cdn, "item_code", row.rss_item_code);
	},
	item_code: function(frm, cdt, cdn){
		row = locals[cdt][cdn];
		frappe.call({
			method: "frappe.client.get",
			args: {
				doctype: "Item",
				name: row.item_code
			},
			callback: function (data) {
				if(!row.rss_item_code){
					frappe.model.set_value(cdt, cdn, "rss_item_code", data.message.item_code);
				}
				frappe.model.set_value(cdt, cdn, "default_gudang", data.message.default_gudang);
				frappe.model.set_value(cdt, cdn, "default_section", data.message.default_section);
				frappe.model.set_value(cdt, cdn, "default_location", data.message.default_location);
			}
		})
		if(row.item_code){
			frappe.call({
				"method" : "golden.golden.stock.set_qty_stock",
				args: {
					name: row.item_code
				},
				callback: function(r){
					if(r.message) {
						frappe.model.set_value(cdt, cdn, r.message);
					}
				},
			});
		}
	},
	default_location: function(frm, cdt, cdn){
		row = locals[cdt][cdn];
		frappe.model.set_value(cdt, cdn, "warehouse", row.default_location);
		frappe.call({
			method: "frappe.client.get",
			args:{
				doctype: "Warehouse",
				filters:{
					name: row.default_location
				}
			},
			callback: function(data){
				frappe.model.set_value(cdt, cdn, "default_section", data.message.parent_warehouse);
			}
		});
	},
	default_section: function(frm, cdt, cdn){
		row = locals[cdt][cdn];
		frappe.call({
			method: "frappe.client.get",
			args:{
				doctype: "Warehouse",
				filters:{
					name: row.default_section
				}
			},
			callback: function(data){
				frappe.model.set_value(cdt, cdn, "default_gudang", data.message.parent_warehouse);
			}
		});
	}
})
cur_frm.cscript['Make Packing'] = function() {
	frappe.model.open_mapped_doc({
		method: "golden.golden.stock.make_packing_list",
		frm: cur_frm
	})
}
