var showPage = {
    params: false,

    accessTypeMap : {
        "restrict_none" : "No restriction",
        "restrict_one" : "Restrict access for one year",
        "restrict_two" : "Restrict access for two years",
        "restrict_indefinite" : "Restrict access indefinitely"
    },

    statusMap : {
        "draft" : "Draft",
        "submit" : "Submitted",
        "review" : "Under Review",
        "inprogress" : "Rejected",
        "inreview" : "Under Review",
        "archived" : "Approved",
        "withdrawn" : "Withdrawn",
        "error" : "Error",
        "tombstone" : "Rejected"
    },

    months : [
        "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
    ],

    startup : function(params) {
        showPage.params = params;
        var template_url = $(params.selector).attr("data-template");
        var back_link = $(params.selector).attr("data-back-link");

        if ($(showPage.params.selector).html() === '') {
            $.get(template_url, function(template) {
                var templateScript = Handlebars.compile(template);

                var thesis_id = getParameterByName('id');
                var data_url = $(showPage.params.selector).attr("data-api");
                var url = data_url + "/" + thesis_id;

                $.get(url, function(data) {
                    data = data["data"];
                    data["back_link"] = back_link;
                    data["api_base_url"] = data_url;

                    if ("access" in data && "type" in data["access"]) {
                        data["access"]["human_type"] = data["access"]["type"];
                        if (data["access"]["type"] in showPage.accessTypeMap) {
                            data["access"]["human_type"] = showPage.accessTypeMap[data["access"]["type"]]
                        }
                    }

                    if ("last_updated" in data) {
                        data["human_last_updated"] = showPage.formatDate({dateStr: data.last_updated});
                    }

                    if ("created_date" in data) {
                        data["human_created_date"] = showPage.formatDate({dateStr: data.created_date});
                    }

                    // set a human readable status code
                    if ("status" in data && "code" in data["status"]) {
                        data["status"]["display"] = data["status"]["code"];
                        if (data["status"]["code"] in showPage.statusMap) {
                            data["status"]["display"] = showPage.statusMap[data["status"]["code"]];
                        }
                    }

                    // construct a URL for each file
                    if ("files" in data) {
                        for (var j = 0; j < data.files.length; j++) {
                            var file = data.files[j];
                            if (file.file_url.substring(0, 4) === "http") {
                                // this is an absolute URL
                                file["access_url"] = file.file_url;
                            } else {
                                file["access_url"] = data_url + "/" + data.id + "/files/" + file.file_name;
                            }
                            if (!("visible" in file)) {
                                file["visible"] = true;
                            }
                        }
                    }

                    var show_html = templateScript(data);
                    $(showPage.params.selector).append(show_html);
                });
            });
        }
    },

    formatDate : function(params) {
        var dateStr = params.dateStr;
        var d = new Date(dateStr);
        var out = d.getUTCDate().toString() + " ";
        out += showPage.months[d.getUTCMonth()] + " ";
        out += d.getUTCFullYear().toString() + " at ";
        out += d.getUTCHours().toString() + ":";
        if  (d.getUTCMinutes() < 10) {
            out += "0";
        }
        out += d.getUTCMinutes().toString();
        return out;
    }
};
