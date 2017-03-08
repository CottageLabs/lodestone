# Thesis Walkthrough

This document describes the steps to go through and the things to check to experience
all the features of the system from the point of view of a user.

## 0. Set up the testing environment

You will want the app fully configured and deployed either in a testing environment or embedded into Drupal

You should ensure that the correct Zendesk credentials are set in the config (e.g. to the Sandbox)

You should ensure that DSpace is up, and the correct credentials are set in the config

DSpace should have a review workflow of at least one step set up, to prevent incoming content going directly into the archive.

## 1. Authenticate

Authenticate within the deployment environment, either using SSO or the native (e.g. Drupal)
authentication system.

## 2. Initial List Theses Page

Visit the initial "List Theses" page.  If this is the first time you've used the system, this
should present an empty page with just a header and a link which reads "Add Thesis"

Click the "Add Thesis" link, which will take you to a blank thesis form.

## 3. Thesis Form - Submit Empty

The initial thesis form is blank.  Attempt to submit it without completing any information.
It should fail with a lot of field validation errors.

## 4. Thesis Form - Invalid Content

Complete all the required fields, but in cases where the content of the fields could be
invalid, say because they contain an email address, an orcid or a date, try filling
in content which should not be allowed.  Some fields which require formatted content
may not be required, but you should fill those in at this point too.  On fields where
there is a word count, try exceeding the word count.

Attempt to submit the form.  It should fail with validation errors on the fields where
you have supplied invalidly formatted content.

## 5. Thesis Form - Control Buttons

Before correcting any of the validation errors, try out the Add/Remove buttons on repeatable
fields where they are available.  Ensure they work as expected.

Add a second supervisor if you like, to test that functionality.

## 6. Thesis Form - Correcting Fields

Correct all the validation errors, and fill in all the other fields on the form.

Attempt to submit the form.  It should fail complaining that you have not uploaded any
files.

## 7. Thesis Form - upload a file, not PDF

Select a file from your computer that is not a PDF, and upload it through the file
upload interface.  You may add or not the file description and software metadata.

Attempt to submit the form.  It should fail complaining that you have not uploaded a PDF.

## 8. Thesis Form - file upload interface

Try adding and removing files to ensure that the upload, remove and cancel behaviour is
working correctly.  To test the cancel behaviour, upload a larger file, which will give you
time to cancel the upload part way through.

The following actions are possible with the file upload interface, and you should try them all:

* Upload a file successfully
* Remove a file before it has been uploaded in the first place
* Remove a file after it has been uploaded
* Cancel an upload part way through

## 9. Thesis Form - upload a PDF

Select a file from your computer that IS a PDF and upload it through the file upload 
interface.  You should also add file description and software metadata.

When you upload the file, you should see the file description and software metadata
reflected back to you.

Submit the form, which should be successful.  You will be redirected to the thesis
list page.

## 10. Thesis List - your recent submission

When you have submitted a new thesis, you will be redirected to the list page, and you should
see the following:

* A flash message thanking you for your submission
* A table with a summary of your thesis in the top row, with the status "Submitted"

Click on the names of the files you uploaded to confirm that they can be downloaded
at this point.

## 11. Confirmation email

Check your inbox and ensure that you have received a confirmation email

## 12. Trigger transfer to Zendesk and DSpace

If you are not already running the deposit task under supervisor (in which
case this step will happen automatically), you can trigger it from the command line with:

    python service/tasks/ethesis_deposit.py

You can stop the script after a few seconds, once the output indicates that
it has been successful, otherwise it will remain running indefinitely (which is its
correct normal behaviour).

## 13. Thesis List - updated status

Reload the thesis list page, and you should see that the status has changed to "Under Review"

## 14. Zendesk

Go to the relevant Zendesk instance (production or sandbox, depending on the environment you 
are testing in), and confirm that the submission has arrived there.  Check that all the fields
you expect to be populated are populated.

## 15. DSpace - workflow review

Go to the relevant DSpace instance, log in as an administrator responsible for the
theses collection workflow, and go to your "Submission" page.  You should see the thesis
submitted above in your task pool.

Take the task, and then open the item and confirm that it contains all the metadata and files
that you expect to see in workflow.  For example use "Show full item record" to see all the
metadata.  You may not be able to see all the files in the workflow, depending on your configuration.


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

Now that the item is archived, we can poll DSpace to get an update on the status.

If you are not already running the DSpace tasks under supervisor (in which case this step will
happen automatically every hour), you can trigger it from the command line with:

    python service/tasks/ethesis_poll.py
    
You can stop the script after a few seconds, once the output indicates that
it has been successful, otherwise it will remain running indefinitely.


## 18. Thesis List - updated status, file urls and repository link

Reload the thesis list page, and you should see that the status has changed to "Approved".

The status "Approved" should have become a link to the DSpace item page for the submission.

At this point, as the item has been archived, the local copies of the files have been removed,
and you can check this on the local disk if desired.

Note that the file names are still linked, and that the links lead to the SWORD urls in DSpace.
Check that these links work - they should not require authentication, as the item has been
published in DSpace.


## 19. Read-only view

On the list page, click the thesis title to go to the read-only view of the item.

Confirm that all the metadata fields you expect to see appear on this page, including the
newly acquired Repository URL.

Note that the file names are linked, and that the links lead to the SWORD urls in DSpace.
Check that these links work - they should not require authentication, as the item has been
published in DSpace.

**This path through the test ends here**

## 20. DSpace - reject and remove item

Reject the item from the workflow (e.g. from the Accept/Reject step of the standard
DSpace workflow configuration).  This will return the item to the sword account's
workspace.

Go to the sword account's workspace, where you should now see the item in the "Unfinished Submissions"
list.  Select the checkbox by the item and click "Remove Selected Submissions".  This will 
remove all record of the item from DSpace.


## 21. Poll DSpace for an update (or lack of one)

Now that the item has been removed from DSpace, we should poll to find that out.

If you are not already running the DSpace tasks under supervisor (in which case this step will
happen automatically every hour), you can trigger it from the command line with:

    python service/tasks/ethesis_poll.py
    
You can stop the script after a few seconds, once the output indicates that
it has been successful, otherwise it will remain running indefinitely.


## 22. Thesis List - updated status and no file urls

Reload the thesis list page, and you should see that the status has changed to "Rejected"

At this point, as the item has been removed, the local copies of the files have been removed,
and all references to files in DSpace have been removed.

## 23. Read-only view

On the list page, click the thesis title to go to the read-only view of the item.

Confirm that all the metadata fields you expect to see appear on this page.

Note that there is no file section on this page, as no files are linked any more.

**This path through the test ends here**