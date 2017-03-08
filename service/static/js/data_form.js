jQuery(document).ready(function() {

    var selector = "#data_container";
    var formSelector = "#data_form";

    var MIMEMAP = {
        "image/tiff" : {format: "Tagged Image File Format (tiff)", software: "Image viewer"},
        "text/plain" : {format: "7-bit ASCII Text", software: "Text editor"},
        "image/png" : {format: "Portable Network Graphics (png)", software: "Image viewer"},
        "application/xml" : {format: "xml", software: "Text editor"},
        "text/xml" : {format: "xmlL", software: "Text editor"},
        "image/jpeg" : {format: "jpeg", software: "Image viewer"},
        "text/csv" : {format: "Comma Separated Values (csv)", software: "Text editor"},
        "application/pdf" : {format: "pdf", software: "Acrobat Reader"},
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" : {format: "Microsfot Excel spreadsheet (xlsx)", software: "Microsoft Excel"},
        "image/bmp" : {format: "bmp", software: "Image viewer"},
        "application/json" : {format: "JavaScript Object Notation (json)", software: "Text editor"},
        "application/vnd.ms-excel" : {format: "Microsfot Excel 97 spreadsheet (xls)", software: "Microsoft Excel 97"},
        "text/html" : {format: "Hypertext Markup Language (html)", software: "Text editor"},
        "application/postscript" : {format: "Encapsulated PostScript File Format", software: "Acrobat Reader"},
        "application/mp4" : {format: "mp4", software: "Video player"},
        "video/mp4" : {format: "mp4", software: "Video player"},
        "application/rtf" : {format: "rtf", software: "Open Office"},
        "text/rtf" : {format: "rtf", software: "Open Office"},
        "application/vnd.rar" : {format: "Compressed file (zip)", software: "7-zip"},
        "application/msword" : {format: "Microsoft Word 97 document (doc)", software: "Microsoft Word 97"},
        "application/mathematica" : {format: "Mathematica notebook file", software: "Mathematica Notebook"},
    };

    var EXTMAP = {
        "gz" : {format: "GZIP Compressed Tar Archive file (gz)", software: "7-zip"},
        "tgz" : {format: "GZIP Compressed Tar Archive file (tgz)", software: "7-zip"},
        "docx" : {format: "Microsoft Word document (docx)", software: "Microsoft Word"},
        "ppt" : {format: "Microsoft Powerpoint 97 document (ppt)", software: "Microsoft Powerpoint 97"},
        "pptx" : {format: "Microsoft Powerpoint document (pptx)", software: "Microsoft Powerpoint"},
        "zip" : {format: "Compressed file (zip)", software: "7-zip"}
    };

    var formBindings = function() {

        // show or hide the information box about confidential information
        $("input[name=confidential_information]").bind("change", function(event) {
            event.preventDefault();
            var val = $(this).val();
            if (val === "true") {
                $("#confidential_information_optional").show();
            } else {
                $("#confidential_information_optional").hide();
            }
        });

        // show or hide the publication details section
        $("input[name=has_publication]").bind("change", function(event) {
            event.preventDefault();
            var val = $(this).val();
            if (val === "true") {
                $("#publication_details").show();
            } else {
                $("#publication_details").hide();
            }
        });

        // show or hide the embargo information section
        var embargoShowHide = function() {
            var isNotPublished = $("#publication_published_no").is(":checked");
            if (isNotPublished) {
                $("#if_not_published").show();
            } else {
                $("#if_not_published").hide();
            }
        };
        $("input[name=publication_published]").bind("change", function(event) {
            event.preventDefault();
            embargoShowHide();
        });

        // show or hide the embargo information section
        $("input[name=embargo]").bind("change", function(event) {
            event.preventDefault();
            var val = $(this).val();
            if (val === "true") {
                $("#if_embargoed").show();
            } else {
                $("#if_embargoed").hide();
            }
        });

        // set up the date picker fields
        $('.datepicker').datepicker({dateFormat:'yy-mm-dd'});

        // auto fill the research data title, if a publication title is set (and no research data title is already set)
        $("#publicationtitle").bind("change", function(event) {
            var pubtitle = $(this).val();
            var was = $(this).attr("data-was");
            var prefix = "Research data supporting";

            var wastitle = prefix + " '" + was + "'";
            var newtitle = prefix + " '" + pubtitle + "'";

            var current = $("#title").val();
            if (!current || current === wastitle ) {
                $("#title").val(newtitle);
            }

            $(this).attr("data-was", pubtitle);
        });

        $("#orcid-less-more").bind("click", function(event) {
            event.preventDefault();
            var state = $(this).attr("data-state");
            if (state === "closed") {
                $("#orcid-info").slideDown();
                $(this).attr("data-state", "open").html("Less about ORCID");
            } else {
                $("#orcid-info").slideUp();
                $(this).attr("data-state", "closed").html("More about ORCID");
            }
        });

        depositForms.bindRepeatable({
            button_selector : ".add_author",
            list_selector: "#authors_list",
            entry_prefix: "authors",
            enable_remove: true,
            remove_selector: ".remove_author",
            remove_behaviour: "hide"
        });

        $("#keywords").select2({
            minimumInputLength: 1,
            tags: [],
            tokenSeparators: [","],
            maximumSelectionSize: 50,
            initSelection : function (element, callback) {
                var data = [];
                $(element.val().split(",")).each(function () {
                    data.push({id: this, text: this});
                });
                callback(data);
            }
        });

        depositForms.bindRepeatable({
            button_selector : ".add_resource",
            list_selector: "#resources_list",
            entry_prefix: "resources",
            enable_remove: true,
            remove_selector: ".remove_resource",
            remove_behaviour: "hide"
        });

        depositForms.bindRepeatable({
            button_selector : ".add_funder",
            list_selector: "#funder_list",
            entry_prefix: "funders",
            enable_remove: true,
            remove_selector: ".remove_funder",
            remove_behaviour: "hide"
        });

        // show or hide the crsid box
        $("input[name=currently_employed]").bind("change", function(event) {
            event.preventDefault();
            var val = $(this).val();
            if (val === "true") {
                $("#if_employed").show();
            } else {
                $("#if_employed").hide();
            }
        });

        // show or hide the crsid box
        $("input[name=rights]").bind("change", function(event) {
            event.preventDefault();
            var val = $(this).val();
            if (val === "Other") {
                $("#if_rights_other").show();
            } else {
                $("#if_rights_other").hide();
            }
        });

        // show or hide the crsid box
        $("input[name=publicise]").bind("change", function(event) {
            event.preventDefault();
            var val = $(this).val();
            if (val === "true") {
                $("#if_publicise").show();
            } else {
                $("#if_publicise").hide();
            }
        });

        $(".thisisme").bind("change", function(event) {
            var el = $(this);
            if (el.is(":checked")) {
                var parent = el.parents(".repeatable_container");
                var idx = parent.attr("id").split("_")[1];
                var gnSel = "#authors-" + idx + "-given_names";
                var fnSel = "#authors-" + idx + "-family_name";
                var gn = parent.find(gnSel).val();
                var fn = parent.find(fnSel).val();

                $("#given_names").val(gn);
                $("#family_name").val(fn);
            }
        });

        var action = $(selector).attr("data-api");
        depositForms.bindFileUpload({
            selector: "#file",
            baseUrl: action,
            fileSizeLimit:  2000000000,      // 2Gb
            totalSizeLimit: 20000000000,     // 20Gb
            getFormData : function(queued, id) {
                var desc = queued.find("input[name=file_format_" + id + "]").val();
                var soft = queued.find("input[name=software_" + id + "]").val();

                return [
                    {name: 'file_format', value: desc},
                    {name: 'software', value: soft}
                ];
            },
            onAdd : function(data, id) {
                var name = data.files[0].name;
                var ext = name.substring(name.lastIndexOf(".") + 1);
                var type = data.files[0].type;
                var software = "";
                if (type in MIMEMAP) {
                    software = MIMEMAP[type]["software"];
                    type = MIMEMAP[type]["format"];
                } else if (ext in EXTMAP) {
                    software = EXTMAP[ext]["software"];
                    type = EXTMAP[ext]["format"];
                }
                data.container.find(".file_format_input").attr("name", "file_format_" + id).val(type);
                data.container.find(".software_input").attr("name", "software_" + id).val(software);
                data.container.find(".file_format_label").attr("for", "file_format_" + id);
                data.container.find(".software_label").attr("for", "software_" + id);
            },
            beforeRedraw : function(data) {
                var format = data.container.find(".file_format_input").val();
                var soft = data.container.find(".software_input").val();

                if (!format) {
                    format = "<em>No format provided</em>";
                }
                if (!soft) {
                    soft = "<em>No software provided</em>";
                }

                return {"format" : format, "soft" : soft}
            },
            afterRedraw : function(data, fromBefore) {
                data.container.find(".file_format").html(fromBefore.format);
                data.container.find(".software").html(fromBefore.soft);
            },
            restoreMemory : function(fileEntry) {
                var memory = {};
                if (fileEntry.file_format && fileEntry.file_format.length > 0) {
                    memory["format"] = fileEntry.file_format[0];
                }
                if (fileEntry.software && fileEntry.software.length > 0) {
                    memory["soft"] = fileEntry.software[0];
                }
                return memory;
            }
        });

        $("#save").bind("click", depositForms.save);
        $('#submit').bind('click', depositForms.submit);
    };

    var LICENSES = {
        "CC BY-NC-ND 4.0" : "https://creativecommons.org/licenses/by-nc-nd/4.0/",
        "CC BY-NC-SA 4.0" : "https://creativecommons.org/licenses/by-nc-sa/4.0/",
        "CC BY-NC 4.0" : "https://creativecommons.org/licenses/by-nc/4.0/",
        "CC BY-ND 4.0" : "https://creativecommons.org/licenses/by-nd/4.0/",
        "CC BY-SA 4.0" : "https://creativecommons.org/licenses/by-sa/4.0/",
        "CC BY 4.0" : "https://creativecommons.org/licenses/by/4.0/",
        "CC0" : "https://creativecommons.org/publicdomain/zero/1.0/",
        "GPLv3" : "https://www.gnu.org/licenses/gpl-3.0.en.html"
    };

    var sortRights = function(record) {
        if (!record.rights) {
            return;
        }
        if (record.rights === "Other") {
            if (record.other_license) {
                record["license"] = {};
                if (record.other_license.text) {
                    record["license"]["text"] = record.other_license.text;
                }
                if (record.other_license.uri) {
                    record["license"]["uri"] = record.other_license.uri;
                }
            }
        } else if (record.rights) {
            record["license"] = {"text" : record.rights, "uri" : LICENSES[record.rights]};
        }

        delete record["rights"];
    };

    var populateLicense = function(obj) {
        if (!obj.text) {
            return;
        }
        if (obj.text in LICENSES) {
            var el = $("[name='rights'][value='" + obj.text + "']");
            if (el) {
                el.prop("checked", true);
                el.attr("value", obj.text);
                el.trigger("change");
            }
        } else {
            var el = $("[name='rights'][value='Other']");
            depositForms._setVal({element: el, val: "Other"});
            el.trigger("change");

            var textEl = $("[id='other_license___text']");
            depositForms._setVal({element: textEl, val: obj.text});

            if (obj.uri) {
                var uriEl = $("[id='other_license___uri']");
                depositForms._setVal({element: uriEl, val: obj.uri});
            }
        }
    };

    depositForms.startup({
        selector: selector,
        form_selector: formSelector,
        minFiles: 0,
        validate: true,
        bindings: formBindings,
        enhanceRecord: sortRights,
        populators: {
            license : populateLicense
        }
    });
});