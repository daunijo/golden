frappe.listview_settings['Sales Invoice Summary'] = {
	add_fields: ["customer", "status",	"company"],
	get_indicator: function(doc) {
		if(doc.status==="Submitted") {
			return [__("Submitted"), "blue", "status,=,Submitted"];
		} else if(doc.status==="Completed") {
			return [__("Completed"), "green", "status,=,Completed"];
    }
	}
};
