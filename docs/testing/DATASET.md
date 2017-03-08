# Dataset Walkthrough

This document describes the steps to go through and the things to check to experience
all the features of the system from the point of view of a user.

## 0. Set up the testing environment

You will want the app fully configured and deployed either in a testing environment or embedded into Drupal

You should ensure that the correct Zendesk credentials are set in the config (e.g. to the Sandbox)

You should ensure that DSpace is up, and the correct credentials are set in the config

DSpace should have a review workflow of at least one step set up, to prevent incoming content going directly into the archive.
You should set at least the "Accept/Reject/Edit Metadata" step for this test script, and be able to add the
item's DOI to the dc.identifier.doi field.

## 1. Authenticate

Authenticate within the deployment environment, either using SSO or the native (e.g. Drupal)
authentication system.

## 2. Initial List Data Page

Visit the initial "List Data" page.  If this is the first time you've used the system, this
should present an empty page with just a header and a link which reads "Add Data"

Click the "Add Data" link, which will take you to a blank data form.

## 3. Data Form - Submit Empty

The initial thesis form is blank.  Attempt to submit it without completing any information.
It should fail with a lot of field validation errors.

## 4. Data Form - Invalid Content

Complete all the required fields, but in cases where the content of the fields could be
invalid, say because they contain an email address, an orcid or a date, try filling
in content which should not be allowed.  

Some fields which require formatted content may not be required, but you should fill those in at this point too.
On fields where there is a word count, try exceeding the word count.

If you see a conditional field appear, leave it blank/do not fill it in at this stage.

Attempt to submit the form.  It should fail with validation errors on the fields where
you have supplied invalidly formatted content.

## 5. Data Form - Conditional Fields

Ensure that all the conditional fields work as expected.  Select the following options and ensure
that the conditional fields appear.  When those fields appear, leave them blank/enter invalid content
if possible, and attempt form submission.  It should fail with validation errors on the conditional
fields with invalid content.

* Do your data contain any personal/sensitive, commercially-sensitive or other forms of confidential/restricted information? - select YES

* Is your data supporting a publication? - select YES
    * Is your publication already published? - select NO
        * Does your data need to be embargoed until your publication is published? - select YES
    
* Are you currently employed or studying at the University? - select YES

* Choose a licence for your data - select OTHER

* Would you like us to publicise information about your data via our Twitter account? - select YES

## 6. Data Form - Control Buttons

Before correcting any of the validation errors, try out the Add/Remove buttons on repeatable
fields where they are available.  Ensure they work as expected.

Add multiple authors, resources and funders to test that functionality.

## 7. Data Form - Correcting Fields

Correct all the validation errors, and fill in all the other fields on the form.

Submit the form.  It should succeed without you uploading any files.  You will be redirected to the data
list page, with a success message.

We'll now submit another dataset with files attached before reviewing the
list data page.

## 8. Data Form - file upload interface

Try adding and removing files to ensure that the upload, remove and cancel behaviour is
working correctly.  To test the cancel behaviour, upload a larger file, which will give you
time to cancel the upload part way through.

The following actions are possible with the file upload interface, and you should try them all:

* Upload a file successfully
* Remove a file before it has been uploaded in the first place
* Remove a file after it has been uploaded
* Cancel an upload part way through

## 9. Data Form - submit item with files

Fill in the data form correctly, and then select one or more files from your computer
to upload through the interface.  You should also add file format and software metadata.

When you upload the file, you should see the file format and software metadata
reflected back to you.

Submit the form, which should be successful.  You will be redirected to the data
list page.

## 10. Data List - your recent submission

When you have submitted a new dataset, you will be redirected to the list page, and you should
see the following:

* A flash message thanking you for your submission
* A table with a summary of your data in the top row, with the status "Submitted"

Click on the names of the files you uploaded to confirm that they can be downloaded
at this point.

## 11. Confirmation email

Check your inbox and ensure that you have received a confirmation email

You should receive a confirmation email whether you attached files to the item or not.

You will receive a different confirmation email depending on whether you submitted a placeholder
record or not, so try submitting both types of item.

Review the text of the email and ensure the references to URLs, etc, are correct.

## 12. Trigger transfer to Zendesk and DSpace

If you are not already running the deposit task under supervisor (in which
case this step will happen automatically), you can trigger it from the command line with:

    python service/tasks/dataset_deposit.py

You can stop the script after a few seconds, once the output indicates that
it has been successful, otherwise it will remain running indefinitely (which is its
correct normal behaviour).

## 13. Data List - updated status

Reload the dataset list page, and you should see that the status has changed to "Under Review"

## 14. Zendesk

Go to the relevant Zendesk instance (production or sandbox, depending on the environment you 
are testing in), and confirm that the submission has arrived there.  Check that all the fields
you expect to be populated are populated.

## 15. DSpace - workflow review

Go to the relevant DSpace instance, log in as an administrator responsible for the
data collection workflow, and go to your "Submission" page.  You should see the dataset
submitted above in your task pool.

Take the task, and then open the item and confirm that it contains all the metadata and files
that you expect to see in workflow.  For example use "Show full item record" to see all the
metadata.  You may not be able to see all the files in the workflow, depending on your configuration.

At this point, you should add the field dc.identifier.doi to the item, and populate it with the
item's DOI (unless this will happen automatically before the item reaches the archive).  

If your metadata form doesn't allow you to add the DOI (the default DSpace forms do not), then you can
just progress the item to the archive, and then use "Edit Item" to add the metadata through the
administrators view.  Just make sure that Lodestone is not polling your DSpace instance regularly
if you take this approach.


## ALTERNATIVE DSPACE BEHAVIOURS

At this point one of two things can happen in DSpace:

1. The item can be reviewed and passed through the workflow to the archive.  See steps **16** - **19**.

2. The item can be rejected and removed from DSpace.  See steps **20** to **23**

## 16. DSpace - archive item

Progress the item through the DSpace workflow and into the archive.

At that point it is easy to select "Edit this Item" from the context menu on the left (of a standard
DSpace 5.x) and review the bitstream policies, bundle structure and full metadata.  
 
Ensure these are as expected.

## 17. Poll DSpace for an update

Now that the item is archived, we can poll DSpace to get an update on the status, and to retrieve
the DOI.

If you are not already running the DSpace tasks under supervisor (in which case this step will
happen automatically every hour), you can trigger it from the command line with:

    python service/tasks/dataset_poll.py
    
You can stop the script after a few seconds, once the output indicates that
it has been successful, otherwise it will remain running indefinitely.

## 18. Zendesk - added DOI

Check the ticket in Zendesk to confirm that the DOI assigned to the item has been added
to it.

## 19. Data List - updated status, file urls and repository link

Reload the data list page, and you should see that the status has changed to "Approved".

The status "Approved" should have become a link to the DSpace item page for the submission.

At this point, as the item has been archived, the local copies of the files have been removed,
and you can check this on the local disk if desired.

Note that the file names are still linked, and that the links lead to the SWORD urls in DSpace.
Check that these links work - they may require authentication.

## 20. Read-only view

On the list page, click the dataset title to go to the read-only view of the item.

Confirm that all the metadata fields you expect to see appear on this page, including the
newly acquired Repository URL.

Note that the file names are linked, and that the links lead to the SWORD urls in DSpace.
Check that these links work - they may require authentication.

**This path through the test ends here**


## 20. DSpace - reject and remove item

Reject the item from the workflow (e.g. from the Accept/Reject/Edit Metadata step of the standard
DSpace workflow configuration).  This will return the item to the sword account's
workspace.

Go to the sword account's workspace, where you should now see the item in the "Unfinished Submissions"
list.  Select the checkbox by the item and click "Remove Selected Submissions".  This will 
remove all record of the item from DSpace.

## 21. Poll DSpace for an update (or lack of one)

Now that the item has been removed from DSpace, we should poll to find that out.

If you are not already running the DSpace tasks under supervisor (in which case this step will
happen automatically every hour), you can trigger it from the command line with:

    python service/tasks/dataset_poll.py
    
You can stop the script after a few seconds, once the output indicates that
it has been successful, otherwise it will remain running indefinitely.

## 22. Data List - updated status and no file urls

Reload the data list page, and you should see that the status has changed to "Rejected"

At this point, as the item has been removed, the local copies of the files have been removed,
and all references to files in DSpace have been removed.

## 23. Read-only view

On the list page, click the dataset title to go to the read-only view of the item.

Confirm that all the metadata fields you expect to see appear on this page.

Note that there is no file section on this page, as no files are linked any more.

**This path through the test ends here**