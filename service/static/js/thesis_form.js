jQuery(document).ready(function() {

    var selector = "#thesis_container";
    var formSelector = "#thesis_form";

    var formBindings = function() {

        var action = $(selector).attr("data-api");
        depositForms.bindFileUpload({
            selector: "#file",
            baseUrl: action,
            getFormData : function(queued, id) {
                var desc = queued.find("input[name=file_description_" + id + "]").val();
                var soft = queued.find("input[name=software_" + id + "]").val();

                return [
                    {name: 'file_description', value: desc},
                    {name: 'software', value: soft}
                ];
            },
            onAdd : function(data, id) {
                data.container.find(".file_description_input").attr("name", "file_description_" + id);
                data.container.find(".software_input").attr("name", "software_" + id);
                data.container.find(".file_description_label").attr("for", "file_description_" + id);
                data.container.find(".software_label").attr("for", "software_" + id);
            },
            beforeRedraw : function(data) {
                var desc = data.container.find(".file_description_input").val();
                var soft = data.container.find(".software_input").val();

                if (!desc) {
                    desc = "<em>No description provided</em>";
                }
                if (!soft) {
                    soft = "<em>No software provided</em>";
                }

                return {"desc" : desc, "soft" : soft}
            },
            afterRedraw : function(data, fromBefore) {
                data.container.find(".file_description").html(fromBefore.desc);
                data.container.find(".software").html(fromBefore.soft);
            },
            restoreMemory : function(fileEntry) {
                var memory = {};
                if (fileEntry.file_description && fileEntry.file_description.length > 0) {
                    memory["desc"] = fileEntry.file_description[0];
                }
                if (fileEntry.software && fileEntry.software.length > 0) {
                    memory["soft"] = fileEntry.software[0];
                }
                return memory;
            }
        });

        // bind all the form fields/functions
        $('.datepicker').datepicker({
            dateFormat:'yy-mm-dd',
            maxDate: new Date()
        });

        depositForms.wordLimit({
            selector: "#abstract",
            output: "#abstract_wordcount",
            limit: 500
        });

        $("#keywords").select2({
            minimumInputLength: 1,
            tags: [],
            tokenSeparators: [","],
            maximumSelectionSize: 50
        });

        $("#language").select2({
            maximumSelectionSize: 3
        });

        depositForms.bindRepeatable({
            button_selector : ".add_supervisor",
            list_selector: "#supervisors_list",
            entry_prefix: "supervisors",
            enable_remove: true,
            remove_selector: ".remove_supervisor",
            remove_behaviour: "hide",
            limit: 5
        });

        $('#ask_college').hide();
        $("#ask_institution").hide();
        var institution = function() {
            $('#ask_college').hide();
            $("#ask_institution").hide();
            var inst = $('#awarding_institution').val();
            if (inst === 'University of XXXXXXXX') {
                $('#ask_college').show();
            } else if ( inst === "Other") {
                $("#ask_institution").show();
            }
        };
        $('#awarding_institution').bind('change', institution);

        $('#degree optgroup').hide();
        var level = function() {
            $('#degree optgroup').hide();
            if ( $('#qualification_level').val() && $('#qualification_level').val().length ) {
                $('#degree optgroup[label="' + $('#qualification_level').val() + '"]').show();
            }
        };
        $('#qualification_level').bind('change',level);

        $(".tool").bind("mouseover", function(event) {
            depositForms.showTooltip(this);
        }).bind("mouseout", function(event) {
            depositForms.hideTooltip(this);
        });

        var restrict = function() {
            $('#ask_restrict_reason').hide();
            $('#ask_cc').hide();
            if ( $('#restrict_indefinite').is(':checked') || $('#restrict_two').is(':checked') || $('#restrict_one').is(':checked') ) {
                $('#ask_restrict_reason').show();
            }
            if ( $('#restrict_two').is(':checked') || $('#restrict_one').is(':checked') || $('#restrict_none').is(':checked') ) {
                $('#ask_cc').show();
            }
        };
        $('.restrict').bind('change', restrict);

        $("#save").bind("click", depositForms.save);
        $('#submit').bind('click', depositForms.submit);
    };

    var validation = function() {
        for (var i = 0; i < depositForms.uploadedFiles.length; i++) {
            if (depositForms.uploadedFiles[i].type === "application/pdf") {
                return true;
            }
        }
        return "You must upload one or more PDF files";
    };

    var licenceURIs = function(record) {
        var uris = {
            "CC BY-NC-ND (Attribution-NonCommercialNoDerivs)" : "https://creativecommons.org/licenses/by-nc-nd/4.0/",
            "CC BY-NC-SA (Attribution-NonCommercial-ShareAlike)" : "https://creativecommons.org/licenses/by-nc-sa/4.0/",
            "CC BY-NC (Attribution-NonCommercial)" : "https://creativecommons.org/licenses/by-nc/4.0/",
            "CC BY-ND (Attribution-NoDerivs)" : "https://creativecommons.org/licenses/by-nd/4.0/",
            "CC BY-SA (Attribution-ShareAlike)" : "https://creativecommons.org/licenses/by-sa/4.0/",
            "CC BY (Attribution)" : "https://creativecommons.org/licenses/by/4.0/"
        };

        if (record.license && record.license.text) {
            if (record.license.text in uris) {
                record.license.uri = uris[record.license.text];
            }
        }
    };

    var populateInstitution = function(val) {
        var opts = $("#awarding_institution option");
        var allowed = [];
        for (var i = 0; i < opts.length; i++) {
            allowed.push($(opts[i]).attr("value"));
        }

        var pd = $("#awarding_institution");
        if ($.inArray(val, allowed) > -1) {
            depositForms._setVal({element: pd, val: val});
            pd.trigger("change");
        } else {
            var input = $("#other_institution");
            depositForms._setVal({element: pd, val: "Other"});
            pd.trigger("change");
            depositForms._setVal({element: input, val: val});
        }
    };

    depositForms.startup({
        selector: selector,
        form_selector: formSelector,
        validate: true,
        bindings: formBindings,
        additionalValidation : validation,
        enhanceRecord: licenceURIs,
        allowEditAll: true,
        populators : {
            awarding_institution : populateInstitution
        }
    });
});