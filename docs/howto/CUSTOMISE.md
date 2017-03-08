# Customising Forms: HOw-TO

This document explains all of the features of the deposit forms, and how their
behaviour can be modified.

Most simple modifications to the behaviour of the forms can be done by editing
the HTML5 templates.  More advanced changes would require you to modify 
the JavaScript that handles the page.

If you make changes to the metadata schema or the information attached
to the files, you will also need to modify the back-end's packaging mechanism.

All forms are created using Bootstrap, so all Bootstrap 3 classes can be used.

## File Locations

### HTML

HTML templates for forms can be found in:

    service/static/templates
    
Each forms interface consists on 3 templates:

1. list_<form type>.handlebars (e.g. list_thesis.handlebars) - this is the list page, which shows the user the items they have submitted
2. <form type>_form.handlebars (e.g. thesis_form.handlebars) - this is the actual form, which is likely the one you want to edit
3. <form type>.handlebars (e.g. thesis.handlebars) - this is the read-only/view page for the data for an item submitted through the form

### JavaScript

JavaScript can be found in:

    service/static/js

The List page depends on two files:

1. list_page.js - all the common mechanics for working with item lists
2. list_<form_type>.js - the specific invocation of the javascript for the item type

The Form page also depends on two files:

1. deposit_forms.js - all the common mechanics for working with deposit forms
2. <form_type>_form.js - the specific invocation of the javascript for the item type

The Show page also depends on two files:

1. show.js - all the common mechanics for workign with read-only/view pages
2. <form_type>.js - the specific invocation of the javascript for the item type.


### CSS

Lodestone specific CSS can be found in

    service/static/css
    
Additionally, the forms interface relies on several standard libraries
including Bootstrap 3.  More information about them can be found in the
DEPLOY.md documentation.

## Form Field Validation

Form field validation is done using Parsley: http://parsleyjs.org/

We currently use the following Parsley validation routines, but you may use any that are specified in their documentation

* data-parsley-required="true" - indicate that a field is mandatory
* data-parsley-type="email" - validate the contents of the form field as an email address
* data-parsley-pattern="<regular expression>" - validate that the contents of the form field match the regular expression

In addition we define our own two validators:

* data-parsley-word-limit="nnn" - specify a maximum number of words in the field.
* data-parsley-required-if-checked="<selector> <selector> ..." - specify one or more selectors which lead to fields which must be checked (i.e. radio or checkboxes) for the field to be required

See the below example for usage of each of these:

    <!-- ordinary required field -->
    <input type="checkbox" name="is_required" id="is_required" value="true"
        data-parsley-required="true" data-parsley-required-message="You must confirm">
    
    <!-- a required field that must also be an email address -->
    <input type="text" class="form-control" id="externalemail"
        data-parsley-required="true" data-parsley-type="email">
    
    <!-- a field that must be in the form of a big-endian date -->
    <input type="text" class="form-control" id="publication_date"
        data-parsley-pattern="\d{4}-\d{2}-\d{2}" data-parsley-pattern-message="Please enter a date in the format YYYY-MM-DD">

    <!-- a field that may not have more than 510 words -->
    <textarea class="form-control" id="abstract" 
        data-parsley-required="true" data-parsley-word-limit="510" data-parsley-word-limit-message="The text you have entered is too long">
    </textarea>
    
    <!-- this input has two selectors in data-parsley-required-if-checked - this means they both have to be checked for this to be required -->
    <input type="text" class="form-control" id="crsid"
        data-parsley-validate-if-empty="true" data-parsley-required-if-checked="#currently_employed_yes #some_other_selector" 
        data-parsley-required-if-checked-message="This value is required">

## Repeatable Form Sections

Repeatable form sections allow you to specify multiple fields that will be repeated as a whole together - e.g. an author's name, email address and ORCID.

The hierarchical structure of the HTML for a repeatable section is as follows:

* div which will contain all of the repeated/repeatable elements; it can have any id.
    * div which will contain a single repeatable element (which can be a group of form fields).  It should have an id of the form <entry_prefix>_0 for the first element.
        * labels, with their "for" attribute set correctly for the form control they refer to
        * inputs, textareas, other form controls.  These should have the class "repeatable_control" and name and id of the form <entry_prefix>-0-<field_name>.
        * button for removing this element; it can have any classes or id, and it should be hidden initially.
* button for adding new elements

Consider the following simple example:

    <div id="authors_list">
        <div id="authors_0" class="repeatable_container">
            <label for="authors-0-name" class="control-label">Name</label>
            <input type="text" class="form-control repeatable-control" name="authors-0-name" id="authors-0-name">
            <button class="btn btn-danger remove_author" style="display: none;">Remove this author</button>
        </div>
    </div>
    <button class="btn btn-primary add_author">Add another author</button>

In order for this to be activated, some additional javascript is required:

    depositForms.bindRepeatable({
        list_selector: "#authors_list",
        entry_prefix: "authors",
        button_selector : ".add_author",
        limit: 10,
        enable_remove: true,
        remove_selector: ".remove_author",
        remove_behaviour: "hide"
    });

This tells the depositForms code the relevant jQuery selectors for the outer list element, the prefix to use when looking for the labels and form controls,
which buttons to bind the add/remove events to, and even specifies a maximum number of entries the user can make (optional).

Here's a more complex example, which includes a lot more layout code, and multiple form fields, though functionally it works just the same:

    <div id="authors_list">
        <div id="authors_0" class="repeatable_container">
            <div class="form-group">
                <label for="authors-0-first_name" class="control-label col-md-4">First name (or initial)*</label>
                <div class="col-md-7">
                    <input type="text" class="form-control repeatable-control" name="authors-0-first_name" id="authors-0-first_name">
                </div>
            </div>
            <div class="form-group">
                <label for="authors-0-last_name" class="control-label col-md-4">Last name*</label>
                <div class="col-md-7">
                    <input type="text" class="form-control repeatable-control" name="authors-0-last_name" id="authors-0-last_name">
                </div>
            </div>
            <div class="form-group">
                <label for="authors-0-orcid" class="control-label col-md-4">ORCID</label>
                <div class="col-md-7">
                    <input type="text" class="form-control repeatable-control" name="authors-0-orcid" id="authors-0-orcid">
                </div>
            </div>
            <div class="form-group">
                <label for="authors-0-supervisor" class="control-label col-md-4">Supervisor?</label>
                <div class="col-md-7">
                    <input class="repeatable-control" type="checkbox" name="authors-0-supervisor" id="authors-0-supervisor" value="true">
                </div>
            </div>
            <div class="form-group">
                <div class="col-md-7 col-md-offset-4">
                    <button class="btn btn-danger remove_author" id="remove_author" style="display: none;">Remove this author</button>
                </div>
            </div>
        </div>
    </div>
    <div class="form-group">
        <div class="col-md-7 col-md-offset-4">
            <button class="btn btn-primary addanother add_author" id="another_authors">Add another author</button>
        </div>
    </div>

This is activated and controlled by exactly the same javascript.  This means it's possible to modify the layout and the fields within a particular 
repeatable field set without modifying the javascript further.


## Reading data from the form

In order for data to be posted from the form to the back-end, it needs to be converted to JSON, which is
then sent via Lodestone's API to create or update records.

We have a mechanism which allows us to tag the form fields in such a way to allow us to automatically
extract that JSON from the form without writing any additional JavaScript, which supports the following
operations (which are covered in more detail further down):

* Tag whether a field should be read
* Read a form field as a single key/value pair
* Read a form field as a single key/value pair, but using nested objects
* Conditionally reading form fields, depending on the status of other form controls
* Read a group of repeatable form fields as a list of objects


### Tag whether a field should be read

To indicate that a field should be read, use

    data-read="true"
    
as the attribute on the form control.  For example:

    <textarea class="form-control" id="accessrights" 
              data-read="true">
    </textarea>

This should be attached to every form control that you want to read, and in the case of
radio buttons should be attached to each button individually.

### Read a form field as a single key/value pair

For a simple key/value entry in the resulting JSON, use:

    data-read-type="single"
    
as the attribute on the form control:

    <textarea class="form-control" id="accessrights" 
              data-read="true" data-read-type="single">
    </textarea>

This results in the JSON output

    {
        "accessrights" : "Whatever the user typed"
    }

### Read a form field as a single key/value pair, but using nested objects

Sometimes you want a set of values to appear inside a nested object, such as:

    {
        "licence" : {
            "type" : "CC BY",
            "uri" : "https://creativecommons.org/licenses/by/3.0/"
        }
    }
    
To configure the forms to do this, use the following

    data-read-type="single" data-read-separator="<nested field separator>"
    
For example, to produce the above JSON output:

    <input type="text" class="form-control" id="licence___name"
           data-read="true" data-read-type="single" data-read-separator="___">
                       
    <input type="text" class="form-control" id="licence___uri"
           data-read="true" data-read-type="single" data-read-separator="___" data-read-if-checked="#rights_other">

The string "___" in the name or id of the field indicates that the fields should be nested at that point.

You can use any string to nest the fields in this way, you just need to specify it in data-read-separator

### Conditionally reading form fields, depending on the status of other form controls

If you wish the value of one field to only be included in the output JSON
if one or more radio button or checkbox is checked, you can add the following

    data-read-if-checked="<selector> <selector> ..."
    
For example:
    
    <input type="radio" name="example_radio" id="example_radio_true" value="true"
           data-read="true" data-read-type="single">
                    
    <input type="radio" name="example_radio" id="example_radio_false" value="false"
           data-read="true" data-read-type="single">
                           
    <input type="text" class="form-control" id="other_value"
           data-read="true" data-read-type="single" data-read-if-checked="#example_radio_true">
           
if example_radio_false is checked, the output JSON would be:

    {
        example_radio: false
    }

if example_radio_true is checked, the output JSON would be:

    {
        example_radio: true,
        other_value: "Whatever the user input"
    }

Note that if the value of a radio button or checkbox is set to "true" or "false",
these will be automatically converted to boolean values in the JSON.


###  Read a group of repeatable form fields as a list of objects

This is for use with the repeatable form field groups described above.

For each field within a repeatable group, you need to provide the type "object-list" and 3 further pieces of configuration, set
similarly to the following:

    data-read-type="object-list"
    data-read-index-pattern="<prefix>-(\d+)-.*" 
    data-read-list-field="<target list field>" 
    data-read-field-pattern="<prefix>-\d+-(.*)"

The **data-read-index-pattern** is a regular expression which tells the form reader where to find the index number of the field in the name or id of the form control.

For example, if the form field is called "authors-2-first_name", this should yield "2".

The **data-read-list-field** tells us which field in the resulting JSON to place the list of objects read from the repeatable form fields.

The **data-read-field-pattern** is a regular expression which tells the form reader where to find the actual field name to use in the form's field name or id.

For example, if the form field is called "authors-2-first_name", this should yield "first_name".

Using the simple example from above, imagine there are two authors specified:

    <div id="authors_list">
        <div id="authors_0" class="repeatable_container">
            <label for="authors-0-name" class="control-label">Name</label>
            <input type="text" class="form-control repeatable-control" name="authors-0-name" id="authors-0-name"
                data-read="true" data-read-type="object-list" data-read-index-pattern="authors-(\d+)-.*" data-read-list-field="authors" data-read-field-pattern="authors-\d+-(.*)">
            <button class="btn btn-danger remove_author">Remove this author</button>
        </div>
        <div id="authors_1" class="repeatable_container">
            <label for="authors-1-name" class="control-label">Name</label>
            <input type="text" class="form-control repeatable-control" name="authors-1-name" id="authors-1-name"
                data-read="true" data-read-type="object-list" data-read-index-pattern="authors-(\d+)-.*" data-read-list-field="authors" data-read-field-pattern="authors-\d+-(.*)">
            <button class="btn btn-danger remove_author" style="display: none;">Remove this author</button>
        </div>
    </div>
    <button class="btn btn-primary add_author">Add another author</button>

The resulting JSON output would be:

    {
        "authors" : [
            {"name" : "First author's name"},
            {"name" : "Second author's name"}
        ]
    }

This can also be applied to more complex repeated field groups in the same way.  Consider the more advanced example from above:

    <div id="authors_list">
        <div id="authors_0" class="repeatable_container">
            <div class="form-group">
                <label for="authors-0-first_name" class="control-label col-md-4">First name (or initial)*</label>
                <div class="col-md-7">
                    <input type="text" class="form-control repeatable-control" name="authors-0-first_name" id="authors-0-first_name"
                           data-read="true" data-read-type="object-list" data-read-index-pattern="authors-(\d+)-.*" data-read-list-field="authors" data-read-field-pattern="authors-\d+-(.*)">
                </div>
            </div>
            <div class="form-group">
                <label for="authors-0-last_name" class="control-label col-md-4">Last name*</label>
                <div class="col-md-7">
                    <input type="text" class="form-control repeatable-control" name="authors-0-last_name" id="authors-0-last_name"
                           data-read="true" data-read-type="object-list" data-read-index-pattern="authors-(\d+)-.*" data-read-list-field="authors" data-read-field-pattern="authors-\d+-(.*)">
                </div>
            </div>
            <div class="form-group">
                <label for="authors-0-orcid" class="control-label col-md-4">ORCID</label>
                <div class="col-md-7">
                    <input type="text" class="form-control repeatable-control" name="authors-0-orcid" id="authors-0-orcid"
                           data-read="true" data-read-type="object-list" data-read-index-pattern="authors-(\d+)-.*" data-read-list-field="authors" data-read-field-pattern="authors-\d+-(.*)">
                </div>
            </div>
            <div class="form-group">
                <label for="authors-0-supervisor" class="control-label col-md-4">Supervisor?</label>
                <div class="col-md-7">
                    <input class="repeatable-control" type="checkbox" name="authors-0-supervisor" id="authors-0-supervisor" value="true"
                           data-read="true" data-read-type="object-list" data-read-index-pattern="authors-(\d+)-.*" data-read-list-field="authors" data-read-field-pattern="authors-\d+-(.*)">
                </div>
            </div>
            <div class="form-group">
                <div class="col-md-7 col-md-offset-4">
                    <button class="btn btn-danger remove_author" id="remove_author" style="display: none;">Remove this author</button>
                </div>
            </div>
        </div>
        
        <div id="authors_1", class="repeatable_container"> ... other authors ... </div>
        
    </div>
    <div class="form-group">
        <div class="col-md-7 col-md-offset-4">
            <button class="btn btn-primary addanother add_author" id="another_authors">Add another author</button>
        </div>
    </div>

This would output the JSON:

    {
        "authors" : [
            {
                "first_name" : "Author's first name",
                "last_name" : "Author's last name",
                "orcid" : "Author's ORCID",
                "supervisor" : true,
            },
            ... other authors ...
        ]
    }
    

## File Upload

File upload is handled by a standard library that understands the process of selecting files,
adding associated file metadata, and uploading those files along with the metadata to 
the back-end.

A file upload therefore consists of:

* A file upload box
* Metadata about the total file size (the sum of all files)
* A list of files either uploaded or queued to be uploaded
* A template HTML fragment for files queued to be uploaded
* A template HTML fragment for files already uploaded

The most basic but complete file upload HTML would look as follows:
    
    <!-- top level layout for the upload form - here we find the input box, total file size metadata, and the empty div into which
        uploaded/queued files will go -->
    <input id="file" class="form-control" type="file" name="file">
    <span id="sum_file_sizes">Nothing yet</span> uploaded/queued
    <span id="remaining_file_sizes">0</span>
    <div id="upload_queue"></div>
    
    <!-- layout template for a file that has been queued -->
    <div id="queued_file_template" style="display:none">
        <div class="queued_file_filename">FILENAME</div>
        <div class="queued_file_size">FILESIZE</div>
        
        <button class="btn btn-primary file_upload_button">Upload</button><br>
        <button class="btn btn-danger file_remove_button">Remove</button>
        
        <!-- if you want an upload progress bar, include this code -->
        <div class="progress progress-striped active" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0">
            <div class="progress-bar progress-bar-success" style="width:0%;"></div>
        </div>
    </div>
    
    <!-- layout template for a file that has been uploaded -->
    <div id="uploaded_file_template" style="display:none">
        <div class="uploaded_file_filename">FILENAME</div>
        <div class="uploaded_file_size">FILESIZE</div>
        
        <button class="btn btn-danger file_remove_button">Remove</button>
    </div>

There are a number of element ids available, such that if they are present will be automatically populated for you with
the relevant information.  These are:

* sum_file_sizes - the total size of all files uploaded/queued so far
* remaining_file_sizes - the total remaining space you have for uploading files
* queued_file_filename - the name of a file queued for upload
* queued_file_size - the size of a file queued for upload
* uploaded_file_name - the name of a file that has already been uploaded
* uploaded_file_size - the size of a file that has already been uploaded

There should also be a buttons with the following classes available within the templates:

* file_upload_button - for uploading a queued file
* file_remove_button - for unqueueing a queued file or removing an uploaded file

In order for the file upload to work, it needs to be initialised in JavaScript.  The above HTML
fragment can be activated in the most simple possible way as follows:
            
    depositForms.bindFileUpload({
        selector: "#file",
        baseUrl: "/data/",
        fileSizeLimit:  2000000000,      // 2Gb
        totalSizeLimit: 20000000000     // 20Gb
    });

The file upload also supports handling of custom metadata to be attached to the files being
uploaded.  Consider the following, slightly more advanced HTML fragment which includes 
input boxes for file format and software:
    
    <input id="file" class="form-control" type="file" name="file">
    <span id="sum_file_sizes">Nothing yet</span> uploaded/queued
    <span id="remaining_file_sizes">0</span>
    <div id="upload_queue"></div>

    <div id="queued_file_template" style="display:none">
        
        <div class="queued_file_filename">FILENAME</div>
        <div class="not_yet_uploaded">NOT YET UPLOADED</div>
        <div class="queued_file_size">FILESIZE</div>
        
        <!-- input boxes which allow the user to add metadata to the queued file -->
        <input type="text" class="form-control file_format_input" name="file_format">
        <input type="text" class="form-control software_input" name="software">
        
        <button class="btn btn-primary file_upload_button">Upload</button><br>
        <button class="btn btn-danger file_remove_button">Remove</button>
        
        <div class="progress progress-striped active" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0">
            <div class="progress-bar progress-bar-success" style="width:0%;"></div>
        </div>
    </div>
    
    <div id="uploaded_file_template" style="display:none">
        
        <div class="uploaded_file_filename">FILENAME</div>
        <div class="successfully_uploaded">SUCCESSFULLY UPLOADED</div>
        <div class="uploaded_file_size">FILESIZE</div>
        
        <!-- space to display the metadata values that the user entered while the file was queued -->
        <div class="file_format">FORMAT</div>
        <div class="col-md-9 software">SOFTWARE</div>
        
        <button class="btn btn-danger file_remove_button">Remove</button>
    </div>
    
Most of the additional complexity here is in the JavaScript, which requires you to specify 4 handlers
to work with the file metadata:

* onAdd - a function which runs when the file is first added to the queue
* getFormData - a function which can read the form data for the specified file from the page
* beforeRedraw - a function which runs before the uploaded file is redrawn on the page
* afterRedraw - a function which runs after the uploaded file is redrawn on the page

To see how these are used, consider the JavaScript which goes along with our more advanced
metadata-enabled file upload HTML, with commentary inline:

    depositForms.bindFileUpload({
        selector: "#file",
        baseUrl: "/data/",
        fileSizeLimit:  2000000000,      // 2Gb
        totalSizeLimit: 20000000000,     // 20Gb
        
        // when the file is first added, we take the input fields for our custom metadata, which
        // were specified in the HTML template, and we rename them - we append the id of the upload
        // (which is given to us as an argument to the function), so that later we can unambiguously
        // identify the metadata for this particular file upload, in case there are multiple queued
        // files on the page at any one time.
        onAdd : function(data, id) {
            data.container.find(".file_format_input").attr("name", "file_format_" + id).val(data.files[0].type);
            data.container.find(".software_input").attr("name", "software_" + id);
            data.container.find(".file_format_label").attr("for", "file_format_" + id);
            data.container.find(".software_label").attr("for", "software_" + id);
        },
        
        // get the file format and software metadata from the form.  Notice that we use the id of the
        // upload (which is again passed in to the function) to identify the correct form fields for
        // the file.  We return a javascript object with the key/value pairs for the metadata.
        getFormData : function(queued, id) {
            var desc = queued.find("input[name=file_format_" + id + "]").val();
            var soft = queued.find("input[name=software_" + id + "]").val();

            return [
                {name: 'file_format', value: desc},
                {name: 'software', value: soft}
            ];
        },
        
        // before the redraw happens, we check the current container to see if the user
        // gave us any data in our form fields.  If not, we set some default values that
        // will be displayed when we draw.  We return a javascript object which contains
        // the key/value pairs for the metadata we want to display.
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
        
        // once the redraw has completed, we can insert our custom file format and software
        // values into the template.  The value of fromBefore is what was returned by the
        // function beforeRedraw above.
        afterRedraw : function(data, fromBefore) {
            data.container.find(".file_format").html(fromBefore.format);
            data.container.find(".software").html(fromBefore.soft);
        }
    });