// Copyright (c) 2018, RSS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Batch Picking', {
	refresh: function(frm) {

	},
	validate: function(frm){
		frm.events.set_details(frm);
		frm.events.set_detail_items(frm);
	},
	set_details: function(frm){
		frm.clear_table("details");
		return frappe.call({
			method: 'golden.golden.doctype.batch_picking.batch_picking.get_details',
			args: {
				start_from: frm.doc.from,
				end_from: frm.doc.to
			},
			callback: function(r, rt) {
				if(r.message) {
					$.each(r.message, function(i, d) {
						var c = frm.add_child("details");
						c.picking = d.picking;
						c.delivery_date = d.delivery_date;
						c.address_display = d.address_display;
						c.priority = d.priority;
					})
					frm.refresh_fields();
				}
			}
		})
	},
	set_detail_items: function(frm){
		frm.clear_table("items");
		return frappe.call({
			method: 'golden.golden.doctype.batch_picking.batch_picking.get_detail_items',
			args: {
				start_from: frm.doc.from,
				end_from: frm.doc.to
			},
			callback: function(r, rt) {
				if(r.message) {
					$.each(r.message, function(i, d) {
						var c = frm.add_child("items");
						c.item_code = d.item_code;
						c.item_name = d.item_name;
						c.qty = d.qty;
						c.stock_uom = d.stock_uom;
						c.uom = d.uom;
						c.conversion_factor = d.conversion_factor;
						c.location = d.location;
						c.qty_taken = d.qty_taken;
						c.picking = d.picking;
						c.urut = d.sequence;
					})
					frm.refresh_fields();
				}
			}
		})
	},
});
