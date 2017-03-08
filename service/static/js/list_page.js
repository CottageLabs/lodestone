var listPage = {

    params: false,

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
        listPage.params = params;
        var template_url = $(params.selector).attr("data-template");
        var add_item_link = $(params.selector).attr("data-add-item");
        var show_item_link = $(params.selector).attr("data-show-item");
        var username = $(params.selector).attr("data-username");

        if ($(listPage.params.selector).html() === '') {
            $.get(template_url, function(template) {
                var templateScript = Handlebars.compile(template);
                var data_url = $(listPage.params.selector).attr("data-api");
                $.get(data_url, { username: username }, function(data) {
                    data["add_item_link"] = add_item_link;
                    data["show_item_link"] = show_item_link;
                    data["api_base_url"] = data_url;

                    for (var i = 0; i < data.data.length; i++) {
                        var record = data.data[i];

                        // set a human readable status code
                        record["status"]["display"] = record["status"]["code"];
                        if (record["status"]["code"] in listPage.statusMap) {
                            record["status"]["display"] = listPage.statusMap[record["status"]["code"]];
                        }
                        if (record["status"]["code"] === "draft") {
                            record["status"]["editable"] = true;
                        }

                        // construct a URL for each file
                        if ("files" in record) {
                            for (var j = 0; j < record.files.length; j++) {
                                var file = record.files[j];
                                if (file.file_url.substring(0, 4) === "http") {
                                    // this is an absolute URL
                                    file["access_url"] = file.file_url;
                                } else {
                                    file["access_url"] = data_url + "/" + record.id + "/files/" + file.file_name;
                                }
                                if (!("visible" in file)) {
                                    file["visible"] = true;
                                }
                            }
                        }

                        // create a human readable date
                        record["human_last_updated"] = listPage.formatDate({dateStr: record.last_updated});
                    }

                    var list_html = templateScript(data);
                    $(listPage.params.selector).append(list_html);
                    listPage.startupPart2();
                });
            });
        }
    },

    startupPart2 : function() {
        if (window.location.hash) {
            var id = window.location.hash.substring(1);
            var section = $("#" + id).show();
        }
    },

    formatDate : function(params) {
        var dateStr = params.dateStr;
        var d = new Date(dateStr);
        var out = d.getUTCDate().toString() + " ";
        out += listPage.months[d.getUTCMonth()] + " ";
        out += d.getUTCFullYear().toString() + " at ";
        out += d.getUTCHours().toString() + ":";
        if  (d.getUTCMinutes() < 10) {
            out += "0";
        }
        out += d.getUTCMinutes().toString();
        return out;
    }
};
