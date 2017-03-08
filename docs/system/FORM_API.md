# Lodestone Form REST API

TODO - Anusha to review

There are two main endpoints for depositing form data:

1. For E-Theses: /ethesis

2. For Research Data: /data

Both behave identically, and only exist to logically separate different types
of form front-end

## /ethesis OR /data

### GET

returns
> 200 OK
> JSON body containing {'data': list_of_records_and_their_metadata, 'success': True}

### POST

___params: thesis_data___    

Files [/docs/system/etheses_examples/example_ethesis_record.json](/docs/system/etheses_examples/example_ethesis_record.json) and 
[/docs/system/etheses_examples/example_ethesis_record2.json](/docs/system/etheses_examples/example_ethesis_record2.json) describe an example dictionary (sent as json object) the server is expecting as thesis data

returns
> 201 created with location header
> JSON body containing location {'data': '/ethesis/\<uuid\>', 'success': True}

_If no data is posted or error occurs saving data_

returns
> 400

## /ethesis/\<uuid\> OR /data/\<uuid\>

### GET

___uuid exists___

returns
> 200 OK
> JSON body containing {'data': metadata, 'success': True}
> [Example thesis record](/docs/system/etheses_examples/example_thesis_record.json)

___uuid does not exist___

returns
> 404 Not found

### PUT (/ethesis/\<uuid\> or /ethesis/new)  OR (/data/\<uuid\> or /data/new)
  
___params: thesis_data___    

Files [/docs/system/etheses_examples/example_ethesis_record.json](/docs/system/etheses_examples/example_ethesis_record.json) and 
[/docs/system/etheses_examples/example_ethesis_record2.json](/docs/system/etheses_examples/example_ethesis_record2.json) describe an example dictionary (sent as json object) 
the server is expecting as thesis data.

If in place of the uuid, the keyword "new" is used in the url, a uuid will be created (i.e. PUT to /ethesis/new)

___New uuid and thesis data posted___

returns
> 201 created with location header
> JSON body containing location {'data': '/ethesis/\<uuid\>', 'success': True}

___Existing uuid and thesis data posted___    

returns
> 204 No content

___If no data is posted or error occurs saving data___

returns
> 400 Bad request

### DELETE

___uuid does not exist___

returns
> 404 Not found

___uuid exists and status == draft___

ES object and files deleted

returns
> 200 OK

___uuid exists and status != draft___

returns
> 405 Method not allowed


## /ethesis/\<uuid\>/files OR /data/\<uuid\>/files

### GET

___uuid exists___

returns
> 200 OK
> JSON body containing {'data': list_of_files, 'success': True}

___uuid does not exist___

returns
> 404 Not found

### POST (/ethesis/\<uuid\>/files or /ethesis/new/files) OR (/data/\<uuid\>/files or /data/new/files)

___params: file, file_description, software___

returns
> 201 created with location header of file
> JSON body containing location of file {'data': '/ethesis/\<uuid\>/files/\<file_name\>', 'success': True}

Note:

* If the uuid did not previously exist a basic metadata record with status draft and file details is created
* If the uuid exists, the file details are added to the existing record

___without file___

returns
> 400 Bad request

## /ethesis/\<uuid\>/files/\<file_name\> OR /data/\<uuid\>/files/\<file_name\>

### GET

___uuid does not exist or file does not exist___

returns
> 404 Not found

___uuid exists and file exists___

returns
> file_content
> 200 OK

### DELETE

___uuid or file does not exist___

returns
> 404 Not found

___uuid exists, file exists and status == draft___

File deleted and ES object updated

returns
> 200 OK

___uuid exists and status != draft___

returns
> 405 Method not allowed

