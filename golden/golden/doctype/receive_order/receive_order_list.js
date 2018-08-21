frappe.listview_settings['Receive Order'] = {
	add_fields: ["expedition", "status",	"company"],
	get_indicator: function(doc) {
		if(doc.status==="Submitted") {
			return [__("Submitted"), "blue", "status,=,Submitted"];
		} else if(doc.status==="Completed") {
			return [__("Completed"), "green", "status,=,Completed"];
    } else if(doc.status==="Partial Bill") {
			return [__("Partial Bill"), "orange", "status,=,Partial Bill"];
		} else if(doc.status==="Draft") {
			return [__("Draft"), "red", "status,=,Draft"];
    } else if(doc.status==="Cancelled") {
			return [__("Cancelled"), "red", "status,=,Cancelled"];
		}
	}
};
