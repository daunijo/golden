frappe.ui.form.on("Purchase Invoice", {
	onload: function(frm){
		frm.set_query('receive_order_1', function(doc) {
			return {
				query: "golden.golden.purchase.receive_order_query",
				filters: { 'supplier': doc.supplier }
			}
		});
		frm.set_query('receive_order_2', function(doc) {
			return {
				query: "golden.golden.purchase.receive_order_query",
				filters: { 'supplier': doc.supplier }
			}
		});
/*
		frm.set_query("rss_item_code", "items", function(doc, cdt, cdn) {
			var row = locals[cdt][cdn];
			return {
				query: "golden.golden.stock.item_query"
			}
		});
*/
		frm.set_query("rss_item_code", "items", function(doc, cdt, cdn) {
			var row = locals[cdt][cdn];
			return {
				query: "golden.golden.stock.pi_item_query",
				filters: { 'supplier': doc.supplier }
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
		frm.clear_custom_button();
	//	frm.events.add_custom_button(frm);
	},
	non_inventory_item: function(frm){
	//	frm.events.add_custom_button(frm);
	},
	make_read_only: function(frm){
		var df1 = frappe.meta.get_docfield("Purchase Order Item","item_name", frm.doc.name);
		df1.read_only = 1;
	},
	add_custom_button: function(frm){
		if((frm.doc.docstatus == 0 || frm.doc.__islocal) && frm.doc.supplier && !frm.doc.non_inventory_item){
		frm.add_custom_button(__("Purchase Order"), function() {
			items = $.map( cur_frm.doc.items, function(item,idx) { return item.purchase_order } )
			added_items = items.join(",")
			erpnext.utils.map_current_doc({
				method: "erpnext.buying.doctype.purchase_order.purchase_order.make_purchase_invoice",
				source_doctype: "Purchase Order",
				target: frm,
				setters: {
					//supplier: frm.doc.supplier || undefined,
				},
				get_query_filters: {
					docstatus: 1,
					company: frm.doc.company,
					supplier: frm.doc.supplier || None,
					status: "To Bill",
					name: ["not in", added_items]
				}
			})
		}, __("Get items from"));
		}
		frm.clear_custom_button();
	},
	get_receive_order_items: function(frm){
		if(frm.doc.receive_order_1 && frm.doc.receive_order_2){
			ro = frm.doc.receive_order_1+"||"+frm.doc.receive_order_2
		}else if(frm.doc.receive_order_1 && !frm.doc.receive_order_2){
			ro = frm.doc.receive_order_1
		}else if(!frm.doc.receive_order_1 && frm.doc.receive_order_2){
			ro = frm.doc.receive_order_2
		}
		frm.events.get_po_due_date(frm, ro);
		frm.events.get_ro_items(frm, ro);
	},
	get_po_due_date: function(frm, ro){
		return frappe.call({
			method: "golden.golden.doctype.receive_order.receive_order.get_po_due_date",
			args:{
				supplier: frm.doc.supplier,
				ro: ro,
				based_on: frm.doc.due_date_base_on
			},
			callback: function(r) {
				if(r.message) {
					frm.set_value(r.message);
				}
			}
		})
	},
	get_ro_items: function(frm, ro){
		frm.clear_table("items");
		return frappe.call({
			method: 'golden.golden.doctype.receive_order.receive_order.get_picking_items',
			args: {
				supplier: frm.doc.supplier,
				ro: ro
			},
			callback: function(r, rt) {
				if(r.message) {
					$.each(r.message, function(i, d) {
						var c = frm.add_child("items");
						c.rss_item_code = d.item_code;
						c.item_code = d.item_code;
						c.item_name = d.item_name;
						c.description = d.description;
						c.qty = d.qty;
						c.uom = d.uom;
						c.stock_uom = d.stock_uom;
						c.rate = d.rate;
						c.purchase_order = d.purchase_order;
						c.warehouse = d.warehouse;
						c.amount = d.amount;
						c.po_detail = d.po_detail;
						c.receive_order = d.receive_order;
						c.receive_order_item = d.ro_detail;
					})
					frm.refresh_fields();
				}
			}
		});

	},
})
frappe.ui.form.on('Purchase Invoice Item', {
	rss_item_code: function(frm, cdt, cdn){
		row = locals[cdt][cdn];
		frappe.model.set_value(cdt, cdn, "item_code", row.rss_item_code);
	},
})
