# How-To handle errors with the deposit process

If an error occurs when the background tasks attempt to deposit files
into DSpace, the designated email address will receive an error message.

You can specify the email address in your local.cfg:

    DEPOSIT_ERROR_EMAIL = "your email here"
    
The email will contain the job id which had the issue.

When running the following scripts, ensure you have activated the python
virtual environment:

    source [virtual env]/bin/activate

## Monitoring and checking task status

If you receive an error (or at any other time), you can check the status
of the task queues on the server with the following command:

    python service/tasks/task_status.py -v -r
    
This will output a full list of task queues, the number of items on each
queue, and the ids of items in the queues.  Omit the -v option for a shorter
summary.  Run the command without any arguments for the full help text.

You can, for example, look at just the ethesis deposit errors, thus:

    python service/tasks/task_status.py -v -r -m ethesis -t deposit
    
This will output something like this:

    [('Queue name', 'Length', 'Ids'), 
    ('ethesis_submit', '0', ''), 
    ('ethesis_submit_error', '1', 'ad8e6ab2-dc18-4b4f-aa14-5f7c2f148788')]

Options available for -m are:

* ethesis
* dataset

Options available for -t are:

* deposit
* poll

If you see one or more ids in a queue whose name ends with _error, you may
wish to investigate further.


## Investigating failed deposits

If a deposit error is encountered, the exception will be sent to the designated
email address, and will also be available in the task schedulers logs.

The zip file generated to be deposited will not be automatically deleted,
so it can be manually investigated for issues.  Files can be found in the directory:

    SWORD_DEPOSIT_DIR/<job_id>.zip

You can, for example, attempt to manually deposit this item into a test
system using something similar to the following curl command:

    curl -i -u <username>:<password> --data-binary "@<job_id>.zip" 
        -H "Content-Type: application/zip" 
        -H "Packaging: http://purl.org/net/sword/package/METSDSpaceSIP"  
        -H "Content-Disposition: filename=<job_id>.zip" 
        https://<dspace repository url>/swordv2/collection/<collection handle>
        
The errors you receive from trying this may indicate why the system is failing.


## Re-queueing jobs

If the deposit problem can be resolved without bug fixing the code (e.g. if
a network failure was the problem), jobs can be re-queued to be tried again.

To re-try a deposit, for example, you can use:

    python service/tasks/redo_tasks.py -m ethesis -t deposit -j <job_id>
    
This will move the specific job id from the deposit error queue to the deposit
queue, where it will be duly re-tried.  You can do this for any error for any
queue.  You can also do all errors at once with:

    python service/tasks/redo_tasks.py -m ethesis -t deposit -a
    
Options available for -m are:

* ethesis
* dataset

Options available for -t are:

* deposit
* poll

## Purging a job from the system

In the case that a job is irredeemably broken, it can be purged from the system
with the following command

    python service/tasks/purge_tasks.py -m ethesis -j <job_id>
    
Options available for -m are:

* ethesis
* dataset

WARNING: this will remove the job from ALL queues, remove ALL files associated
with the job on disk, and any deposit zip files associated with the job.  It is irreversible, so USE
WITH CAUTION.