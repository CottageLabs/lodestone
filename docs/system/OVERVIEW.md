# Lodestone architecture overview

[Insert Diagram]

The application consists of two distinct parts:

1. A back-end which provides a form submission API and the ability to
synchronise content with a SWORDv2-compliant repository

2. A front-end application which provides a form-submission and file upload
environment which communicates with the back-end via the form submission API

The front-end consists of a number of form templates which are augmented with
JavaScript to provide a rich user experience.  These forms may carry out
two actions:

1. Add files to a new or existing item.  Files may also come with file-specific
metadata

2. Add metadata to a new or existing item.

These operations may happen in either order, such that an item on the back-end
can be created in a number of steps over time.

Once the user asserts that a record is complete (by hitting Save on the form),
the back-end will add the item to an asychronous deposit queue, which will
package the metadata and files into a METS-based package format (a format 
understood by default by DSpace), and deposit them to a specified collection
in the repository using SWORDv2.

Once the item has been deposited, the back-end will continually monitor
the item's status using the url provided by the SWORDv2 interface.  When
the item changes status (e.g. as it moves through the repository workflow),
Lodestone will update its record of the item, until such time as
the item reaches the archive.  

At this point, Lodestone will delete its cached copies of the files 
uploaded by the user, but will keep the metadata.

TODO - Anusha to review