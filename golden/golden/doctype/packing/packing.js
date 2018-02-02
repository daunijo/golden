// Copyright (c) 2018, RSS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Packing', {
	setup: function(frm){
		frm.set_query('customer', function(doc) {
			return {
				filters: { 'disabled': 0 }
			}
		});
		frm.set_query("shipping_address_name", function(doc) {
			return {
				query: "golden.golden.purchase.address_query",
				filters: {
					'link_name': doc.customer
				}
			}
		});
		frm.set_query("company_address", function(doc) {
			return {
				query: "golden.golden.purchase.address_query",
				filters: {
					'link_name': doc.customer
				}
			}
		});
		frm.set_query("item_code", "items", function (doc, cdt, cdn) {
			var c_doc= locals[cdt][cdn];
			return {
				filters: {
					'disabled': 0
				}
			}
		});
		frm.set_query('expense_account', 'items', function(doc, cdt, cdn) {
			if (erpnext.is_perpetual_inventory_enabled(doc.company)) {
				return {
					filters: {
						"report_type": "Profit and Loss",
						"company": doc.company,
						"is_group": 0
					}
				}
			}
		});
	},
	barcode: function(frm, cdt, cdn){
		var bcode="<img src='http://www.barcodes4.me/barcode/c128a/myfilename.png?value="+frm.doc.barcode+"'>"
//		var bcode="<img src='http://www.barcodes4.me/barcode/c128b/"+frm.doc.barcode+".gif'>"

		var html="<div class='row'><div class='col-md-6'>"+bcode+"</div></div>"
		$(cur_frm.fields_dict.barcode_img.wrapper).html(html);
		frm.refresh_fields();
	},
	refresh: function(frm) {
		frm.events.set_read_only(frm);
	},
	set_posting_time: function(frm){
		frm.events.set_read_only(frm);
	},
	set_read_only: function(frm){
		if(frm.doc.set_posting_time == 1){
			frm.set_df_property("posting_date", "read_only", false);
			frm.set_df_property("posting_time", "read_only", false);
		}else{
			frm.set_df_property("posting_date", "read_only", true);
			frm.set_df_property("posting_time", "read_only", true);
		}
	},
	customer: function(frm){
		frm.events.get_customer_name(frm);
	},
	get_customer_name: function(frm){
		frappe.call({
			"method": "frappe.client.get",
			args: {
				doctype: "Customer",
				name: frm.doc.customer
			},
			callback: function (data) {
				frm.set_value("customer_name", data.message.customer_name);
			}
		})
	},
	posting_date: function(frm){
		frm.set_value("transaction_date", frm.doc.posting_date);
	},
	shipping_address_name: function(frm){
		if(frm.doc.shipping_address_name != undefined){
			frappe.call({
				method: "frappe.client.get",
				args: {
					doctype: "Address",
					name: frm.doc.shipping_address_name
				},
				callback: function (data) {
					line1 = data.message.address_line1
					if(data.message.address_line2 != undefined){
						line2 = "\n"+data.message.address_line2
					}else{
						line2 = ""
					}
					city = "\n"+data.message.city
					country = "\n"+data.message.country
					if(data.message.pincode != undefined){
						pincode = "\n"+data.message.pincode
					}else{
						pincode = ""
					}
					join = line1+line2+city+country+pincode;
					frm.set_value("shipping_address", join);
				}
			})
		}else{
			frm.set_value("shipping_address", "");
		}
	},
	company_address: function(frm){
		if(frm.doc.shipping_address_name != undefined){
			frappe.call({
				method: "frappe.client.get",
				args: {
					doctype: "Address",
					name: frm.doc.company_address
				},
				callback: function (data) {
					line1 = data.message.address_line1
					if(data.message.address_line2 != undefined){
						line2 = "\n"+data.message.address_line2
					}else{
						line2 = ""
					}
					city = "\n"+data.message.city
					country = "\n"+data.message.country
					if(data.message.pincode != undefined){
						pincode = "\n"+data.message.pincode
					}else{
						pincode = ""
					}
					join = line1+line2+city+country+pincode;
					frm.set_value("company_address_display", join);
				}
			})
		}else{
			frm.set_value("company_address_display", "");
		}
	},
	get_picking_item: function(frm){
		if(frm.doc.sales_order){
			return frappe.call({
				method: 'golden.golden.stock.get_picking',
				args: {
					sales_order: frm.doc.sales_order
				},
				callback: function(r, rt) {
					if(r.message) {
						$.each(r.message, function(i, d) {
							var c = frm.add_child("picking_list");
							c.picking = d.picking;
						})
						frm.refresh_fields();
					}
				}
			})
		}
	},
});
frappe.ui.form.on("Packing Item", {
	expense_account: function(frm, dt, dn) {
		var d = locals[dt][dn];
		frm.update_in_all_rows('items', 'expense_account', d.expense_account);
	},
	cost_center: function(frm, dt, dn) {
		var d = locals[dt][dn];
		frm.update_in_all_rows('items', 'cost_center', d.cost_center);
	}
});
