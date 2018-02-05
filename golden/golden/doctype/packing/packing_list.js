frappe.listview_settings['Packing'] = {
	add_fields: ["customer", "status",	"company"],
	get_indicator: function(doc) {
		if(doc.status==="Submitted") {
			return [__("Submitted"), "blue", "status,=,Submitted"];
		} else if(doc.status==="Sent") {
			return [__("Sent"), "green", "status,=,Sent"];
    }
	}
};
