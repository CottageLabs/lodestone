# Lodestone functional description

Lodestone provides a remote JavaScript form interface for metadata
and file upload, and a user-facing management environment for interacting
with items created via the form.  It also provides a Python-based back-end
for receiving items created through the form, and managing interactions
with the repository.

Items created via the form are synchronised into the specified
SWORDv2-compliant repository, using a METS-based deposit package format.

The following files describe the parts of the application:

* Overview of Architecture - OVERVIEW.md
* Form Submission API - FORM_API.md
* Deposit Packaging Format - PACKAGE.md
* SWORDv2 protocol operations - SWORD.md