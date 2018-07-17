// Copyright (c) 2018, RSS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Delivery Order', {
	setup: function(frm){
		frm.set_query("packing", "details", function (doc, cdt, cdn) {
			var c_doc= locals[cdt][cdn];
			items = $.map( cur_frm.doc.details, function(item,idx) { return item.packing } );
			added_items = items.join(",");
			return {
				query: "golden.golden.doctype.delivery_order.delivery_order.packing_query",
				filters: {
					'not_in': added_items
				}
			}
		});
		frm.set_query("contact_person", "details", function (doc, cdt, cdn) {
			var c_doc= locals[cdt][cdn];
			return {
				query: "golden.golden.doctype.delivery_order.delivery_order.contact_query",
				filters: {
					'link_name': c_doc.expedition
				}
			}
		});
		frm.set_query("expedition", "details", function (doc, cdt, cdn) {
			var c_doc= locals[cdt][cdn];
			return {
				filters: {
					'buying': 1
				}
			}
		});
		frm.set_query("contact_person", function(doc) {
			return {
				query: "golden.golden.doctype.delivery_order.delivery_order.contact_query",
				filters: {
					'link_name': doc.expedisi
				}
			}
		});
	},
	refresh: function(frm) {
		if(frm.doc.docstatus == 0 || frm.doc.__islocal){
			frm.events.set_read_only(frm);
			frm.events.get_packing_list(frm);
		}
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
	get_packing_list: function(frm){
		if(frm.doc.docstatus == 0 || frm.doc.__islocal) {
			frm.add_custom_button(__("Get Packing List"), function() {
				items = $.map( cur_frm.doc.details, function(item,idx) { return item.packing } )
				added_items = items.join(",")
				erpnext.utils.map_current_doc({
					method: "golden.golden.doctype.delivery_order.delivery_order.get_packing_list",
					source_doctype: "Packing",
					target: frm,
					setters:  {
						// company: frm.doc.company || undefined,
						customer: frm.doc.customer || undefined,
						sales_order: frm.doc.sales_order || undefined,
					},
					get_query_filters: {
						docstatus: 1,
						delivery_order: "",
						name: ["not in", added_items]
					}
				})
			});
		}
	},
	// barcode: function(frm){
	// 	frm.doc.barcode.keyup(function() {
	// 		msgprint(frm.doc.naming_series)
	// 	})
	// },
	// onload_post_render: function(frm) {
	// 	cur_frm.fields_dict.barcode.$input.on("change", function(evt){
	// 		frm.events.get_barcode(frm);
	// 	});
	// },
	get_barcode: function(frm){
		// frm.clear_table("bcode");
		items = $.map( cur_frm.doc.bcode, function(item,idx) { return "'"+item.barcode_1+"'" } )
		added_items = items.join(",")
		return frappe.call({
			method: 'golden.golden.doctype.delivery_order.delivery_order.get_packing_barcode',
			args: {
				barc: frm.doc.barcode,
				notin: added_items || "-"
			},
			callback: function(r, rt) {
				if(r.message){
					$.each(r.message, function(i, d){
						var c = frm.add_child("bcode");
						c.barcode = d.barcode;
						c.barcode_1 = d.barcode_1;
						c.box = d.box;
						c.packing = d.packing;
					})
					frm.events.set_details(frm);
					frm.set_value("barcode", "");
				}else{
					frm.set_value("barcode", "");
				}
				frm.refresh_fields();
			}
		})
	},
	set_details: function(frm){
		pc = $.map( cur_frm.doc.details, function(item,idx) { return "'"+item.packing+"'" } );
		pc_list = pc.join(",")
		return frappe.call({
			method: 'golden.golden.doctype.delivery_order.delivery_order.get_packing_from_barcode',
			args: {
				bcode: frm.doc.barcode,
				pl: pc_list || "-"
			},
			callback: function(r, rt) {
				if(r.message) {
					$.each(r.message, function(i, d) {
						var c = frm.add_child("details");
						c.packing = d.packing;
						c.customer = d.customer;
						c.customer_name = d.customer_name;
						c.packing_date = d.packing_date;
						c.total_box = d.total_box;
					})
					frm.refresh_fields();
				}
			}
		});
	},
});
frappe.ui.form.on("Delivery Order Detail", {
	packing: function(doc, cdt, cdn){
		var d = locals[cdt][cdn];
		if(d.packing){
			frappe.call({
				method: "frappe.client.get",
				args: {
					doctype: "Packing",
					filters:{
						name: d.packing,
					}
				},
				callback: function (data) {
					// no_do = data.message.name.replace('PL-', 'DO-');
					// frappe.model.set_value(cdt, cdn, "do_no", no_do);
					frappe.model.set_value(cdt, cdn, "packing_date", data.message.posting_date);
					frappe.model.set_value(cdt, cdn, "customer", data.message.customer);
					frappe.model.set_value(cdt, cdn, "customer_name", data.message.customer_name);
					frappe.model.set_value(cdt, cdn, "total_box", data.message.total_box);
					frappe.model.set_value(cdt, cdn, "sales_order", data.message.sales_order);
				}
			})
		}
	},
	expedition: function(doc, cdt, cdn){
		var d = locals[cdt][cdn];
		if (d.expedition){
			frappe.call({
				method: "frappe.client.get",
				args: {
					doctype: "Expedition",
					name: d.expedition
				},
				callback: function (data) {
					line1 = data.message.address;
					city = "\n"+data.message.city;
					state = "\n"+data.message.state;
					country = "\n"+data.message.country;
					join = line1+city+state+country;
					frappe.model.set_value(cdt, cdn, "expedition_address", join);
					frappe.model.set_value(cdt, cdn, "website", data.message.website);
				}
			})
		}
	},
	contact_person: function(doc, cdt, cdn){
		var d = locals[cdt][cdn];
		if(d.contact_person) {
			frappe.call({
				method: "golden.golden.doctype.delivery_order.delivery_order.get_expedition_detail",
				args:{
					name: d.contact_person
				},
				callback: function (r) {
					if(r.message) {
						frappe.model.set_value(cdt, cdn, r.message);
					}
				}
			})
		}else{
			frappe.model.set_value(cdt, cdn, "contact_name", "");
		}
	},
})
