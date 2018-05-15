// Copyright (c) 2018, RSS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Packing', {
	setup: function(frm){
		frm.set_query('customer', function(doc) {
			return {
				filters: { 'disabled': 0 }
			}
		});
		frm.set_query('packer', function(doc) {
			return {
				filters: { 'department': 'Packer' }
			}
		});
		frm.set_query('checker', function(doc) {
			return {
				filters: { 'department': 'Checker' }
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
		frm.set_query("picker", "picking_list", function (doc, cdt, cdn) {
			var c_doc= locals[cdt][cdn];
			return {
				filters: {
					'department': 'Picker'
				}
			}
		});
		frm.set_query("packer", "picking_list", function (doc, cdt, cdn) {
			var c_doc= locals[cdt][cdn];
			return {
				filters: {
					'department': 'Packer'
				}
			}
		});
	},
	onload: function(frm, cdt, cdn){
		if (!frm.doc.__islocal || frm.doc.docstatus == 0){
			var bcode = "http://www.barcodes4.me/barcode/c39/"+frm.doc.name+".png"
			frm.set_value("barcode_image", bcode);
			frm.refresh_fields();
		}
	},
	refresh: function(frm) {
		if(frm.doc.docstatus == 0 || frm.doc.__islocal){
			frm.events.set_read_only(frm);
			frm.events.get_picking_order(frm);
		}
	},
	get_picking_order: function(frm){
		if(frm.doc.docstatus == 0 || frm.doc.__islocal) {
			frm.add_custom_button(__("Get Picking Order"), function() {
				erpnext.utils.map_current_doc({
					method: "golden.golden.doctype.packing.packing.get_picking_list",
					source_doctype: "Picking Order",
					target: frm,
					setters:  {
						customer: frm.doc.customer || undefined,
//						sales_order: undefined,
					},
					get_query_filters: {
						docstatus: 1,
						packing: ""
//						sales_order: frm.doc.sales_order
					}
				})
			});
		}
	},
	validate: function(frm){
		frm.clear_table("simple");
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
	//	frm.events.get_picking_order(frm);
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
});
frappe.ui.form.on("Packing Item", {
	box: function(frm, cdt, cdn){
		var row = locals[cdt][cdn];
		if(row.box) {
			var stringsearch = ",",str = row.box;
			for(var i=count=0; i<str.length; count+=+(stringsearch===str[i++]));
			if(count >= 1){
				banyak = count;
				var arr = row.box.split(',');
				maks = 0;
				maks = arr[0];
				for(nn=1; nn<=banyak; nn++){
					if(arr[nn] >= maks){
						maks = arr[nn];
					}
				}
				sisa = maks;
			}else{
				sisa = row.box;
			}
			frappe.model.set_value(cdt, cdn, "maks_box", sisa);
		}
	},
	is_full: function(frm, cdt, cdn){
		var row = locals[cdt][cdn];
		if(row.is_full){
			frappe.model.set_value(cdt, cdn, "qty_packing", row.qty);
		}
	}
});
