// known issue with Drupal not setting $
if (!$) {
    var $ = jQuery;
}

var depositForms = {
    activeParsley : false,
    currentUUID : false,
    submitEnabled: true,
    params: false,
    queuedFiles: [],
    uploadedFiles: [],
    fu_params: {},

    startup : function(params) {
        depositForms.params = params;
        if (!depositForms.params.hasOwnProperty("minFiles")) {
            depositForms.params.minFiles = 1;
        }
        if (!depositForms.params.hasOwnProperty("validate")) {
            depositForms.params.validate = true;
        }

        var object_id = getParameterByName('id');
        if (object_id) {
            var data_url = $(depositForms.params.selector).attr("data-api");
            if (data_url[data_url.length - 1] == "/") {
                data_url = data_url.substr(0, data_url.length - 1);
            }
            var url = data_url + "/" + object_id;
            $.get(url, function(data) {
                depositForms.startupPart1a(data.data);
            });
        } else {
            depositForms.startupPart1a(false);
        }
    },

    startupPart1a : function(obj) {
        // if we've been given an object, and we are not allowed to edit it, work that out now
        if (obj && obj.status && obj.status.code) {
            if (obj.status.code !== "draft" && !depositForms.params.allowEditAll) {
                $(depositForms.params.selector).html("This item can no longer be edited.");
                return;
            }
        }

        var template = $(depositForms.params.selector).attr("data-template");

        //Retrieve the template data from the template file
        if ($(depositForms.params.selector).html() === '') {
            $.get(template, function(template) {
                depositForms.startupPart2(template, obj);
            });
        } else {
            depositForms.startupPart3(obj);
        }
    },

    startupPart2 : function(template, obj) {
        // compile the template
        var templateScript = Handlebars.compile(template);
        var form_html = templateScript();
        $(depositForms.params.selector).append(form_html);
        depositForms.startupPart3(obj);
    },

    startupPart3 : function(obj) {
        // register our custom Parsley validators
        window.Parsley.addValidator("requiredIfChecked", {
            validateString : function(value, requirement) {
                var checkCount = 0;
                var selectors = requirement.split(" ");
                for (var i = 0; i < selectors.length; i++) {
                    var selector = selectors[i];
                    if ($(selector).is(":checked")) {
                        checkCount++;
                    }
                }
                if (checkCount === selectors.length) {
                    return !!value;
                }
                return true;
            },
            validateMultiple : function(values, requirement) {
                if (values.length > 0) {
                    return this.validateString("true", requirement);
                } else {
                    return this.validateString("", requirement);
                }
            },
            priority: 33
        });
        window.Parsley.addValidator("wordLimit" ,{
            validateString : function(value, requirement) {
                var wc = depositForms._countWords({
                    separator: " ",
                    normaliseSeparator: true,
                    value: value
                });
                var limit = parseInt(requirement);
                return wc <= limit
            }
        });
        window.Parsley.addValidator("requiredIfVal", {
            validateString : function(value, requirement) {
                var bits = requirement.split(" ");
                var selector = bits.shift();
                var valueSection = bits.join(" ");
                var val = valueSection.substring(1, valueSection.length - 1);   // strip the quote marks
                if ($(selector).val() === val) {
                    return !!value;
                }
                return true;
            }
        });

        if (obj) {
            depositForms.currentUUID = obj.id;
        } else {
            depositForms.currentUUID = depositForms.generateUUID();
        }

        depositForms.bounceParsley();
        depositForms.params.bindings();

        // finally, populate the form if we have data
        if (obj) {
            depositForms.populateForm({
                obj: obj
            });
        }
    },

    enableSubmit : function() {
        depositForms.submitEnabled = true;
        $('#submit').removeAttr("disabled").html("Submit");
    },

    disableSubmit : function() {
        $("#submit").attr("disabled", "disabled");
        depositForms.submitEnabled = false;
    },

    repeat : function(params) {
        var button_selector = params.button_selector;
        var list_selector = params.list_selector;
        var entry_prefix = params.entry_prefix;
        var enable_remove = params.enable_remove || false;
        var remove_behaviour = params.remove_behaviour || "hide";
        var remove_selector = params.remove_selector;
        var remove_callback = params.remove_callback;
        var limit = params.limit || false;

        var source = "";
        var first = true;
        var max = 0;
        var attributes = {};

        // first, get rid of the validation, which will confuse matters when we repeat the field
        depositForms.destroyParsley();

        var blocks = $(list_selector).children();
        var count = blocks.length;
        if (limit !== false && count >= limit) {
            depositForms.bounceParsley();
            return 0;
        }

        blocks.each(function () {
            var bits = $(this).attr("id").split("_");
            var n = parseInt(bits[bits.length - 1]);
            if (n > max) {
                max = n
            }
            if (first) {
                first = false;
                source = $(this).html();
                $(this).each(function () {
                    $.each(this.attributes, function () {
                        attributes[this.name] = this.value;
                    });
                });
            }
        });

        var nid = entry_prefix + "_" + (max + 1);
        var attrs = "";
        for (var key in attributes) {
            if (key != "id") {
                attrs += key + "='" + attributes[key] + "'"
            }
        }
        var ns = "<div id='" + nid + "' " + attrs + ">" + source + "</div>";

        // append a new section with a new, higher number (and hide it)
        $(list_selector).append(ns);

        $("#" + nid).find(".repeatable-control").each(function () {
            var name = $(this).attr("name");
            var bits = name.split("-");
            bits[1] = max + 1;
            var newname = bits.join("-");

            var el = $(this);
            var itype = el.attr("type");
            el.attr("name", newname)
                .attr("id", newname);
            if (itype !== "checkbox" && itype !== "radio") {
                el.val("");
            }

            $("#" + nid).find("label[for=" + name + "]").attr("for", newname);
        });

        if (enable_remove) {
            if (remove_behaviour === "hide") {
                $(remove_selector).show();
            } else if (remove_behaviour === "disable") {
                $(remove_selector).removeAttr("disabled");
            }
            $(remove_selector).unbind("click")
                .click(function (event) {
                    event.preventDefault();
                    $(this).parents(".repeatable_container").remove();

                    if ($(list_selector).children().size() == 1) {
                        if (remove_behaviour === "hide") {
                            $(remove_selector).hide();
                        } else if (remove_behaviour === "disable") {
                            $(remove_selector).attr("disabled", "disabled");
                        }
                    }
                    $(button_selector).removeAttr("disabled");

                    if (remove_callback) {remove_callback()}
                    depositForms.bounceParsley();
                    depositForms.enableSubmit();
                    depositForms.bounceFormWatchers();
                }
            );
        }

        depositForms.bounceParsley();
        depositForms.enableSubmit();
        depositForms.bounceFormWatchers();

        if (limit !== false) {
            return limit - (count + 1);
        } else {
            return -1;
        }
    },

    bindRepeatable: function (params) {
        var button_selector = params.button_selector;
        var list_selector = params.list_selector;
        var entry_prefix = params.entry_prefix;
        var enable_remove = params.enable_remove || false;
        var remove_selector = params.remove_selector;
        var remove_behaviour = params.remove_behaviour || "hide";
        var before_callback = params.before_callback;
        var more_callback = params.more_callback;
        var remove_callback = params.remove_callback;
        var limit = params.limit || false;

        $(button_selector).click(function (event) {
            event.preventDefault();

            if (before_callback) { before_callback() }

            var remaining = depositForms.repeat({
                button_selector: button_selector,
                list_selector : list_selector,
                entry_prefix : entry_prefix,
                enable_remove : enable_remove,
                remove_behaviour: remove_behaviour,
                remove_selector : remove_selector,
                remove_callback : remove_callback,
                limit: limit
            });

            // each time it is used, re-bind it, as there may now be more
            // than one "more" button
            $(button_selector).unbind("click");
            if (remaining === 0) {
                $(button_selector).attr("disabled", "disabled");
            }
            depositForms.bindRepeatable(params);

            if (more_callback) { more_callback() }
        })
    },

    generateUUID : function() {
        var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            var r = Math.random()*16|0, v = c == 'x' ? r : (r&0x3|0x8);
            return v.toString(16);
        });
        return uuid;
    },

    readForm : function() {
        var record = {};
        var lists = {};

        $("[data-read=true]").each(function() {
            var element = $(this);

            var type = element.attr("data-read-type");
            var tag = element.prop("tagName");
            var val = element.val();
            var separator = element.attr("data-read-separator");
            var valSeparator = element.attr("data-read-value-separator");
            var ifChecked = element.attr("data-read-if-checked");
            var readIfNot = element.attr("data-read-if-not");
            var readIfVal = element.attr("data-read-if-val");

            // don't read the value if it is conditional on another field being checked
            if (ifChecked) {
                var checkCount = 0;
                var selectors = ifChecked.split(" ");
                for (var i = 0; i < selectors.length; i++) {
                    if ($(selectors[i]).is(":checked")) {
                        checkCount++;
                    }
                }
                if (checkCount < selectors.length) {
                    return;
                }
            }

            // don't read the field if the value is in the list of values not to read
            if (readIfNot) {
                // strip the leading and tailing quotes
                readIfNot = readIfNot.substring(1, readIfNot.length - 1);

                // split the values out
                var vals = readIfNot.split("' '");

                // don't read this field, if the value is in the list
                for (var i = 0; i < vals.length; i++) {
                    if (vals[i] === val) {
                        return;
                    }
                }
            }

            // only read this field if some other field value is set as specified
            if (readIfVal) {
                var rivbits = readIfVal.split(" ");
                var selector = rivbits.shift();
                var valueSection = rivbits.join(" ");
                var rivval = valueSection.substring(1, valueSection.length - 1);   // strip the quote marks
                if ($(selector).val() !== rivval) {
                    return;
                }
            }

            var field = element.attr("data-read-field");
            if (!field) {
                field = element.attr("name");
            }
            if (!field) {
                field = element.attr("id");
            }

            if (separator) {
                var bits = field.split(separator);
                field = bits.join(".");
            }

            if (tag === "INPUT") {
                var itype = element.attr("type");
                if (itype === "checkbox") {
                    if (!$(this).is(':checked')) {
                        return;
                    }
                    if (val === "true") {
                        val = true;
                    } else if (val === "false") {
                        val = false;
                    }
                } else if (itype === "radio") {
                    if (!$(this).is(':checked')) {
                        return;
                    }
                    if (val === "true") {
                        val = true;
                    } else if (val === "false") {
                        val = false;
                    }
                }
            }
            // FIXME: we'll also have to handle select2 enabled fields

            // don't store empty vals
            if (val === "" || val === null) {
                return;
            }

            if (valSeparator) {
                val = val.split(valSeparator)
            }

            var subField = null;
            if (type === "object-list") {
                var listField = element.attr("data-read-list-field");
                var indexRx = element.attr("data-read-index-pattern");
                var fieldRx = element.attr("data-read-field-pattern");

                var idx = field.match(indexRx)[1];
                subField = field.match(fieldRx)[1];
                field = listField;

                if (!lists[field]) {
                    lists[field] = {};
                }
                if (!lists[field][idx]) {
                    lists[field][idx] = {};
                }
            }

            if (type === "single") {
                depositForms.set_path(record, field, val);
            } else if (type === "object-list" && lists.hasOwnProperty(field) && lists[field].hasOwnProperty(idx)) {
                depositForms.set_path(lists[field][idx], subField, val);
            }
        });


        for (var field in lists) {
            var loopupTable = {};
            var indexes = [];

            for (var idx in lists[field]) {
                var i = parseInt(idx);
                loopupTable[i] = idx;
                indexes.push(i);
            }

            indexes.sort();
            var newList = [];
            for (var i = 0; i < indexes.length; i++) {
                var idx = indexes[i];
                var original = loopupTable[idx];
                newList.push(lists[field][original]);
            }

            depositForms.set_path(record, field, newList);
        }

        return record;
    },

    populateForm : function(params) {
        var context = params.context;
        var obj = params.obj;

        var fields = Object.keys(obj);
        for (var i = 0; i < fields.length; i++) {
            var key = fields[i];
            var value = obj[key];

            if (depositForms.params.populators && depositForms.params.populators[key]) {
                depositForms.params.populators[key](value);

            } else if (key === "files") {
                for (var j = 0; j < value.length; j++) {
                    var fileEntry = value[j];
                    var file = {
                        name: fileEntry.file_name,
                        type: fileEntry.file_mime_type,
                        size: fileEntry.file_size
                    };

                    var id = depositForms.generateUUID();
                    var container = depositForms._fu_make_container(id);

                    var remember = {};
                    if (depositForms.fu_params.restoreMemory) {
                        remember = depositForms.fu_params.restoreMemory(fileEntry);
                    }

                    depositForms._fu_add_uploaded({
                        file: file,
                        container: container,
                        remember: remember
                    });
                }

                depositForms._announceFileSizeInfo({totalSizeLimit: depositForms.fu_params.totalSizeLimit});

            } else if (depositForms._isPrimitiveNonBool(value)) {
                // ordinary key/value pair
                var el = depositForms._findFormElements({context: context, key: key});
                if (el) {
                    depositForms._setVal({element: el, val: value});
                    el.trigger("change");
                }

            } else if (value === true || value === false) {
                // boolean key/value pair
                var el = depositForms._findFormElements({context: context, key: key});
                if (el) {
                    var type = el.attr("type");
                    if (!type) {
                        continue;
                    }
                    type = type.toLowerCase();
                    if (type === "checkbox") {
                        if (value === true) {
                            depositForms._setVal({element: el, val: "true"});
                            el.trigger("change");
                        }
                    } else if (type === "radio") {
                        for (var j = 0; j < el.length; j++) {
                            var rel = $(el[j]);
                            if (rel.attr("value") === "true" && value === true) {
                                depositForms._setVal({element: rel, val: "true"});
                                rel.trigger("change");
                            } else if (rel.attr("value") === "false" && value === false) {
                                depositForms._setVal({element: rel, val: "false"});
                                rel.trigger("change");
                            }
                        }
                    }
                }

            } else if ($.isPlainObject(value) && !$.isArray(value)) {
                // a sub-object
                if (depositForms.params.populators && depositForms.params.populators[key]) {
                    depositForms.params.populators[key](value);
                } else {
                    var separator = "___";
                    var innerContext = key + separator;
                    depositForms.populateForm({
                        context: innerContext,
                        obj: value
                    })
                }

            } else if ($.isArray(value) && value.length > 0) {
                // an array
                if ($.isPlainObject(value[0])) {
                    var innerContext = key + "___";
                    var repeatButton = $("[data-repeat-for='" + key + "']");
                    if (repeatButton.length > 0)
                    {
                        for (var j = 1; j < value.length; j++) {
                            repeatButton.trigger("click");
                        }
                    }

                    for (var j = 0; j < value.length; j++) {
                        if (repeatButton.length > 0) {
                            innerContext = key + "-" + String(j) + "-";
                        }
                        depositForms.populateForm({
                            context : innerContext,
                            obj: value[j]
                        });
                    }
                } else {
                    var el = depositForms._findFormElements({context: context, key: key});
                    if (el) {
                        depositForms._setVal({element: el, val: value});
                    }
                }
            }
        }
    },

    _isPrimitiveNonBool : function(v) {
        return !($.isPlainObject(v) || $.isArray(v) || v === false || v === true)
    },

    _findFormElements : function(params) {
        var context = params.context;
        var field = params.key;
        var container = $(depositForms.params.form_selector);

        if (context) {
            field = context + field;
        }

        var selectors = [
            "input[name='" + field + "']",
            "input[id='" + field + "']",
            "textarea[name='" + field + "']",
            "textarea[id='" + field + "']",
            "select[name='" + field + "']",
            "select[id='" + field + "']"
        ];

        var el = false;
        for (var i = 0; i < selectors.length; i++) {
            var jqel = $(selectors[i], container);
            if (jqel.length > 0) {
                el = jqel;
                break;
            }
        }

        return el;
    },

    _setVal : function(params) {
        var jqel = params.element;
        var val = params.val;

        // some properties we might be interested in
        var tag = jqel.prop("tagName");
        var type = jqel.attr("type");

        var cattr = jqel.attr("class");
        var classes = [];
        if (cattr) {
            classes = cattr.split(" ");
        }
        var isSelect2 = false;
        for (var i = 0; i < classes.length; i++) {
            if (classes[i].lastIndexOf("select2", 0) === 0) {
                isSelect2 = true;
            }
        }

        // if this is a select2 select box, setting the val directly won't have the desired
        // effect, and we want to use the select2 native method
        if (tag && tag.toLowerCase() === "select" && isSelect2) {
            jqel.select2("val", val);
            return;
        } else if (tag && tag.toLowerCase() === "input" && isSelect2) {
            var sdata = [];
            for (var i = 0; i < val.length; i++) {
                sdata.push({id: val[i], text: val[i]});
            }
            jqel.select2("data", sdata);
            return;
        }

        // if this is a checkbox or radio, check it, and ensure that the value is set appropriately
        if (type && (type.toLowerCase() === "checkbox" || type.toLowerCase() === "radio")) {
            jqel.prop("checked", true);
            jqel.attr("value", val);
            return;
        }

        // finally, jquery's default value setter - will work for most form elements
        jqel.val(val);
    },

    set_path : function(obj, path, value) {
        var parts = path.split(".");
        var context = obj;

        for (var i = 0; i < parts.length; i++) {
            var p = parts[i];

            if (!context.hasOwnProperty(p) && i < parts.length - 1) {
                context[p] = {};
                context = context[p];
            } else if (context.hasOwnProperty(p) && i < parts.length - 1) {
                context = context[p];
            } else {
                context[p] = value;
            }
        }
    },

    fileSize : function(num) {
        var size = num;

        var suffixes = ["bytes", "Kb", "Mb", "Gb"];
        var suffixPointer = 0;

        while (size >= 1000 && suffixPointer < suffixes.length - 1) {
            size = size / 1000;
            suffixPointer++;
        }

        var nf = depositForms.numFormat({
            decimalPlaces: 1,
            thousandsSeparator: ",",
            suffix: " " + suffixes[suffixPointer]
        });
        return nf(size);
    },

    numFormat : function(params) {
        var prefix = params.prefix || "";
        var zeroPadding = params.zeroPadding || false;
        var decimalPlaces = params.decimalPlaces !== undefined ? params.decimalPlaces : false;
        var thousandsSeparator = params.thousandsSeparator || false;
        var decimalSeparator = params.decimalSeparator || ".";
        var suffix = params.suffix || "";

        return function(num) {
            // ensure this is really a number
            num = parseFloat(num);

            // first off we need to convert the number to a string, which we can do directly, or using toFixed if that
            // is suitable here
            if (decimalPlaces !== false) {
                num = num.toFixed(decimalPlaces);
            } else {
                num  = num.toString();
            }

            // now "num" is a string containing the formatted number that we can work on

            var bits = num.split(".");

            if (zeroPadding !== false) {
                var zeros = zeroPadding - bits[0].length;
                var pad = "";
                for (var i = 0; i < zeros; i++) {
                    pad += "0";
                }
                bits[0] = pad + bits[0];
            }

            if (thousandsSeparator !== false) {
                bits[0] = bits[0].replace(/\B(?=(\d{3})+(?!\d))/g, thousandsSeparator);
            }

            if (bits.length == 1) {
                return prefix + bits[0] + suffix;
            } else {
                return prefix + bits[0] + decimalSeparator + bits[1] + suffix;
            }
        }
    },

    showTooltip : function(element) {
        var tip = $(element).attr("data-tooltip");
        var pos = $(element).position();
        $("#visible_tooltip").remove();
        $("body").append('<div id="visible_tooltip">' + tip + '</div>');
        $("#visible_tooltip").css("position", "absolute")
            .css("top", pos.top)
            .css("left", pos.left);
    },

    hideTooltip : function(element) {
        $("#visible_tooltip").remove();
    },

    _readAndSend : function(params) {
        var code = params.code;
        var redirect = params.redirect;

        // first read the record out of the form
        var record = depositForms.readForm();

        // now augment it with the relevant user data
        var username = $(depositForms.params.selector).attr("data-username");
        var useremail = $(depositForms.params.selector).attr("data-email");
        var userssid = $(depositForms.params.selector).attr("data-ssid");
        var user_auth = {
            "name": username,
            "email": useremail,
            "session_id": userssid
        };
        record["user_auth"] = user_auth;

        // set the record status.  At the moment this is just hard-coded to submit, but later this might
        // be a "draft" status
        record["status"] = {"code" : code};

        if (depositForms.params.enhanceRecord) {
            depositForms.params.enhanceRecord(record);
        }

        var action = $(depositForms.params.selector).attr("data-api") + depositForms.currentUUID;

        // submit to the endpoint
        $.ajax({
            type: "PUT",
            url: action,
            processData: false,
            async: false,
            cache: false,
            contentType: 'application/json; charset=utf-8',
            data: JSON.stringify(record),
            success: function(data) {
                window.location.href = redirect;
            },
            error: function(data) {
                // console.log(data);
                depositForms.enableSubmit();
                alert('Sorry, there was an error with your submission, please try again');
            }
        });
    },

    save : function(event) {
        event.preventDefault();
        $("#save").html("Saving");

        var url = $(depositForms.params.selector).attr("data-redirect");
        url = url.split("#")[0];
        depositForms._readAndSend({code: "draft", redirect: url});
    },

    submit : function(event) {
        event.preventDefault();
        if (!depositForms.submitEnabled) {
            return;
        }

        // disable the save button, to avoid multiple presses
        depositForms.disableSubmit();
        depositForms.bounceFormWatchers();

        if (depositForms.params.validate) {
            var valid = depositForms.activeParsley.validate();
            if (!valid) {
                return;
            }

            if ($("#upload_queue .successfully_uploaded").length < depositForms.params.minFiles) {
                alert("You must upload " + depositForms.params.minFiles + " or more files before submitting");
                depositForms.enableSubmit();
                return;
            }

            if (depositForms.params.additionalValidation) {
                var msg = depositForms.params.additionalValidation();
                if (msg !== true) {
                    alert(msg);
                    return;
                }
            }
        }

        $("#submit").html("Submitting");

        var url = $(depositForms.params.selector).attr("data-redirect");
        depositForms._readAndSend({code: "submit", redirect: url});
    },

    _fu_make_container : function(id) {
        return $('<div class="queued_file" data-id="' + id + '"></div>').appendTo("#upload_queue");
    },

    _fu_add_queued : function(data) {
        depositForms.queuedFiles.push({
            name: data.files[0].name,
            type: data.files[0].type,
            size: data.files[0].size
        });
        depositForms._announceFileSizeInfo({totalSizeLimit: depositForms.fu_params.totalSizeLimit});

        var id = depositForms.generateUUID();
        data.container = depositForms._fu_make_container(id);

        var size = depositForms.fileSize(data.files[0].size);

        var template = $("#queued_file_template").html();
        data.container.html(template);
        data.container.find(".queued_file_filename").html(data.files[0].name);
        data.container.find(".queued_file_size").html(size);

        depositForms.fu_params.onAdd(data, id);

        data.context = data.container.find(".file_upload_button");
        data.context.bind("click", function(event) {
            event.preventDefault();
            $(this).attr("disabled", "disabled")
                .parents(".queued_file").attr("data-submitting", "true")
                .find(".file_remove_button").attr("disabled", "disabled");
            data.container.find(".upload_bar").show();
            data.submit();
        });

        data.remove = data.container.find(".file_remove_button");
        data.remove.bind("click", function(event) {
            event.preventDefault();
            $(this).parents(".queued_file").remove();
            depositForms._removeFileRecord({
                register: depositForms.queuedFiles,
                filename: data.files[0].name
            });
            depositForms._announceFileSizeInfo({totalSizeLimit: depositForms.fu_params.totalSizeLimit});
        });

        data.cancel = data.container.find(".upload_cancel_button");
        data.cancel.bind("click", function(event) {
            event.preventDefault();
            data.abort();   // this will call the cancel code via the "fail" handler
            // depositForms._fu_cancel(data);
        })
    },

    _fu_add_uploaded : function(params) {
        var file = params.file;
        var container = params.container;
        var remember = params.remember;

        depositForms.uploadedFiles.push({
            name: file.name,
            type: file.type,
            size: file.size
        });

        var size = depositForms.fileSize(file.size);

        var template = $("#uploaded_file_template").html();
        container.html(template);
        container.find(".uploaded_file_filename").html(file.name);
        container.find(".uploaded_file_size").html(size);

        depositForms.fu_params.afterRedraw({container: container}, remember);

        var remove = container.find(".file_remove_button");
        remove.bind("click", function(event) {
            event.preventDefault();
            var that = this;
            var filename = file.name;
            // submit to the endpoint
            $.ajax({
                type: "DELETE",
                url: depositForms.fu_params.baseUrl + depositForms.currentUUID + '/files/' + encodeURIComponent(filename),
                processData: false,
                async: false,
                cache: false,
                success: function(data) {
                    $(that).parents(".queued_file").remove();
                    depositForms._removeFileRecord({
                        register: depositForms.uploadedFiles,
                        filename: filename
                    });
                    depositForms._announceFileSizeInfo({totalSizeLimit: depositForms.fu_params.totalSizeLimit});
                },
                error: function(data) {
                    console.log(data);
                    alert('Sorry, there was a problem deleting the file, please try again');
                }
            });
        });
    },

    _fu_cancel : function(data) {
        // data.abort();
        // FIXME: this isn't quite right - investigate
        depositForms._removeFileRecord({
            register: depositForms.queuedFiles,
            filename: data.files[0].name
        });
        depositForms._announceFileSizeInfo({totalSizeLimit: depositForms.fu_params.totalSizeLimit});
        if (data.container)
        {
            data.container.find(".file_upload_button").removeAttr("disabled");
            data.container.find(".file_remove_button").removeAttr("disabled");
            data.container.find(".upload_bar").hide().find('.progress')
                .attr('aria-valuenow', 0)
                .children().first().css('width', "0%");
        }
    },

    bindFileUpload : function(params) {
        depositForms.fu_params = {
            fileSizeLimit : 0,
            totalSizeLimit: 0
        };
        $.extend(depositForms.fu_params, params);

        // for convenience, some shortcuts
        var selector = depositForms.fu_params.selector;
        var fileSizeLimit = depositForms.fu_params.fileSizeLimit;
        var totalSizeLimit = depositForms.fu_params.totalSizerLimit;

        depositForms._announceFileSizeInfo({totalSizeLimit: totalSizeLimit});

        $(selector).fileupload({
            url: depositForms.fu_params.baseUrl + depositForms.currentUUID + '/files',
            dataType: 'json',
            formData: function(form) {
                var queued = form.find(".queued_file[data-submitting=true]");
                var id = queued.attr("data-id");
                queued.removeAttr("data-submitting");

                return depositForms.fu_params.getFormData(queued, id);
            },
            add: function (e, data) {
                // first check that the file size is less than the file size limit
                if (fileSizeLimit > 0 && data.files[0].size > fileSizeLimit) {
                    data.abort();
                    var limit = depositForms.fileSize(fileSizeLimit);
                    alert("You attempted to upload a file which is greater than the file size limit of " + limit + ".  Please choose a smaller file.");
                    return;
                }

                // then check that the file size doesn't make the total file size greater than the total size limit
                if (totalSizeLimit > 0) {
                    var totalBeforeUpload = depositForms._sumFileSizes();
                    var totalAfterUpload = totalBeforeUpload + data.files[0].size;
                    if (totalAfterUpload > totalSizeLimit) {
                        data.abort();
                        var limit = depositForms.fileSize(totalSizeLimit);
                        alert("You attempted to upload a file which took you over the total upload size limit of " + limit + ".  Please choose a smaller file.");
                        return;
                    }
                }

                depositForms._fu_add_queued(data);
            },
            progress: function (e, data) {
                if (e.isDefaultPrevented()) {
                    return false;
                }
                var progress = Math.floor(data.loaded / data.total * 100);
                if (data.container) {
                    data.container.each(function () {
                        $(this).find('.progress')
                            .attr('aria-valuenow', progress)
                            .children().first().css(
                                'width',
                                progress + '%'
                            );
                    });
                }
            },
            done: function(e, data) {
                if (!data.result || (!data.result.success)) {
                    alert("File upload failed, please try again");
                    doCancel(data);
                    return;
                }

                depositForms._removeFileRecord({
                    register: depositForms.queuedFiles,
                    filename: data.files[0].name
                });

                var remember = depositForms.fu_params.beforeRedraw(data);

                depositForms._fu_add_uploaded({
                    file: data.files[0],
                    container: data.container,
                    remember: remember
                });

                depositForms.enableSubmit();
            },
            fail: function (e, data) {
                // "abort" is a deliberate act, so we know it was thrown on purpose, so we don't report it to the user
                if (data.errorThrown !== "abort") {
                    alert("File upload failed, with the error: " + data.errorThrown + ".  Please try again, and if the problem persists please contact an administrator");
                }
                depositForms._fu_cancel(data);
            }
        });
    },

    wordLimit : function(params) {
        var separator = params.separator !== undefined ? params.separator : " ";
        var normaliseSeparator = params.normaliseSeparator !== undefined ? params.normaliseSeparator : true;
        $(params.output).html("<strong>" + params.limit + "</strong> words remaining");
        $(params.selector).on("keyup", function(event) {
            var val = $(this).val();
            var wc = depositForms._countWords({
                separator: separator,
                normaliseSeparator: normaliseSeparator,
                value: val
            });
            var remaining = params.limit - (wc - 1);
            if (remaining >= 0) {
                $(params.output).html("<strong>" + remaining + "</strong> words remaining");
            } else {
                remaining = remaining * -1;
                $(params.output).html("<span style='color: #ff0000'><strong>" + remaining + "</strong> words over limit</span>");
            }

        })
    },

    destroyParsley : function() {
        if (depositForms.activeParsley) {
            depositForms.activeParsley.destroy();
        }
        $(".has-error").removeClass("has-error");
    },

    bounceParsley : function() {
        depositForms.destroyParsley();
        depositForms.activeParsley = $(depositForms.params.form_selector).parsley();
    },

    bounceFormWatchers: function() {
        $(".form-control").off("change.Submit").on("change.Submit", function (event) {
            depositForms.enableSubmit()
        });
        $("input[type=checkbox]").off("change.Submit").on("change.Submit", function (event) {
            depositForms.enableSubmit()
        });
        $("input[type=radio]").off("change.Submit").on("change.Submit", function (event) {
            depositForms.enableSubmit()
        });
    },

    _countWords : function(params) {
        var normaliseSeparator = params.normaliseSeparator !== undefined ? params.normaliseSeparator : true;
        var separator = params.separator !== undefined ? params.separator : " ";
        var val = params.value;
        if (normaliseSeparator) {
            var double = separator + separator;
            while (val.indexOf(double) > -1) {
                val = val.replace(double, separator);
            }
        }
        var words = val.split(separator);
        return words.length;
    },

    _removeFileRecord : function(params) {
        var register = params.register;
        var filename = params.filename;

        var idx = -1;
        for (var i = 0; i < register.length; i++) {
            if (register[i].name === filename) {
                idx = i;
            }
        }
        if (idx > -1) {
            register.splice(idx, 1);
        }
    },

    _sumFileSizes : function() {
        var total = 0;
        for (var i = 0; i < depositForms.uploadedFiles.length; i++) {
            total += depositForms.uploadedFiles[i].size;
        }
        for (var i = 0; i < depositForms.queuedFiles.length; i++) {
            total += depositForms.queuedFiles[i].size;
        }
        return total;
    },

    _announceFileSizeInfo : function(params) {
        var totalSizeLimit = params.totalSizeLimit;

        var totalUploadSize = depositForms._sumFileSizes();
        var total = depositForms.fileSize(totalUploadSize);
        var remainingUploadSize = totalSizeLimit - totalUploadSize;
        var remaining = depositForms.fileSize(remainingUploadSize);

        $("#sum_file_sizes").html(total);
        $("#remaining_file_sizes").html(remaining);
    }
};