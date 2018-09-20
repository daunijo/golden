frappe.treeview_settings['Warehouse'] = {
	get_tree_nodes: "erpnext.stock.doctype.warehouse.warehouse.get_children",
	add_tree_node: "erpnext.stock.doctype.warehouse.warehouse.add_node",
	get_tree_root: false,
	root_label: "Warehouses",
	filters: [{
		fieldname: "company",
		fieldtype:"Select",
		options: $.map(locals[':Company'], function(c) { return c.name; }).sort(),
		label: __("Company"),
		default: frappe.defaults.get_default('company') ? frappe.defaults.get_default('company'): ""
	}],
	fields:[
		{
			fieldtype:'Data',
			fieldname: 'warehouse_name',
			label:__('New Warehouse Name'),
			reqd:true
		},
		{
			fieldtype:'Check',
			fieldname:'is_group',
			label:__('Is Group'),
			description: __("Child nodes can be only created under 'Group' type nodes")
		},
		{
			fieldtype:'Link',
			fieldname:'account',
			label:__('Account'),
			options: "Account",
			reqd:true,
			get_query: function() {
				return {
					filters: [
						["Account", "is_group", "=", 0],
						["Account", "account_type", "=", "Stock"],
						["Account", "company", "=", frappe.defaults.get_default('company')]
					]
				}
			},
		},
		{
			fieldtype:'Select',
			fieldname:'type',
			label:__('Type'),
			options: ['Warehouse', 'Section', 'Location'].join('\n'),
			reqd:true,
		},
		{
			fieldtype:'Link',
			fieldname:'parent_warehouse',
			label:__('Parent Warehouse'),
		  options: "Warehouse",
			hidden:true,
			depends_on: 'eval:doc.type=="Warehouse"',
		  // description: __("Optional. Sets company's default currency, if not specified."),
			get_query: function() {
					return {
						// query: "erpnext.controllers.queries.warehouse_query",
						filters: [
							["Warehouse", "is_group", "=", 1],
							["Warehouse", "type", "=", "Warehouse"]
						]
					}
			}
		},
		{
			fieldtype:'Link',
			fieldname:'parent_warehouse_rss',
			label:__('Parent Warehouse'),
		  options: "Warehouse",
			depends_on: 'eval:(doc.type=="Section" || doc.type=="Location")',
		  // description: __("Optional. Sets company's default currency, if not specified."),
			get_query: function() {
					return {
						// query: "erpnext.controllers.queries.warehouse_query",
						filters: [
							["Warehouse", "is_group", "=", 1],
							["Warehouse", "type", "=", "Warehouse"]
						]
					}
			}
		},
		{
			fieldtype:'Link',
			fieldname:'parent_section_rss',
			label:__('Parent Section'),
		  options: "Warehouse",
			depends_on: 'eval:doc.type=="Location"',
		  // description: __("Optional. Sets company's default currency, if not specified."),
			get_query: function() {
				return {
					// query: "erpnext.controllers.queries.warehouse_query",
					filters: [
						["Warehouse", "is_group", "=", 1],
						["Warehouse", "type", "=", "Section"]
					]
				}
			}
		},
	],
	ignore_fields:["parent_warehouse"],
	ignore_fields:["parent_warehouse_rss"],
	ignore_fields:["parent_section_rss"],
	onrender: function(node) {
		if (node.data && node.data.balance!==undefined) {
			$('<span class="balance-area pull-right text-muted small">'
			+ format_currency(Math.abs(node.data.balance), node.data.company_currency)
			+ '</span>').insertBefore(node.$ul);
		}
	},

	onload: function(treeview) {
		function get_company() {
			return treeview.page.fields_dict.company.get_value();
		};

		treeview.page.add_inner_button(__("Chart of Accounts"), function() {
			frappe.set_route('Tree', 'Account', {
				company: get_company(),
			});
		}, __('View'));
  },
}
