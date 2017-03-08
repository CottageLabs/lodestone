from octopus.core import app
from redis import Redis
import csv
from datetime import datetime
import os


class TaskStatus:
    """
    get status of tasks from redis

    from service.tasks.task_status import TaskStatus
    r = TaskStatus(verbose=[True|False], csv_format=[True|false])
        # verbose = True => report on all queues including queues of length zero.
        #                For queues of non-zero length, also include the job ids
        # verbose = False => For all queues of non-zero length, report on length of queue
        #
        # csv_format = True => Save report to disk in csv format.
        # csv_format = False => return a python list of tuples


    r.generate_all() # get status of queues and error queues

    r.generate_specific(model, task) # get status of specific model and task and its corresponding error queue
        # Model has to be one of 'ethesis' or 'dataset'
        # Task has to be one of 'deposit', 'poll' or 'ticket create'
    """

    def __init__(self, verbose=False, csv_format=True):
        self.r = Redis()
        self.verbose = verbose
        self.csv_format = csv_format
        self.queue = None
        self.report_dir = app.config.get('REDIS_STATUS_DIR')
        self.report_file = os.path.join(self.report_dir, "%s.csv" % datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"))
        self.queues = [
            app.config.get('DATASET_SUBMIT_QUEUE'),
            app.config.get('DATASET_POLL_QUEUE'),
            app.config.get('ETHESIS_SUBMIT_QUEUE'),
            app.config.get('ETHESIS_POLL_QUEUE')
        ]

    def generate_all(self):
        if self.verbose:
            report = [('Queue name', 'Length', 'Ids')]

        error_queues = []
        for queue in self.queues:
            error_queues.append("%s_error" % queue)
        all_queues = self.queues + error_queues

        for queue in all_queues:
            count = self.r.llen(queue)
            if not self.verbose and count == 0:
                continue
            if self.verbose:
                ids = self.r.lrange(queue, 0, count)
                report.append((queue, str(count), "\n".join(ids)))
            else:
                report.append((queue, str(count)))

        if self.csv_format:
            self.csv_out(report)
            return self.report_file
        else:
            return report

    def generate_specific(self, model, task):
        if model and model not in ['ethesis', 'dataset']:
            raise ValueError("Model has to be one of 'ethesis' or 'dataset'")
        if task and task not in ['deposit', 'poll']:
            raise ValueError("Model has to be one of 'deposit', 'poll' or 'ticket create'")
        job_queue = None
        if model == 'dataset':
            if task == 'deposit':
                job_queue = app.config.get('DATASET_SUBMIT_QUEUE')
            elif task == 'poll':
                job_queue = app.config.get('DATASET_POLL_QUEUE')
        elif model == 'ethesis':
            if task == 'deposit':
                job_queue = app.config.get('ETHESIS_SUBMIT_QUEUE')
            elif task == 'poll':
                job_queue = app.config.get('ETHESIS_POLL_QUEUE')
        if not job_queue:
            raise ValueError("There is no queue defined for this model and task")
        error_queue = "%s_error" % job_queue

        all_queues = [job_queue, error_queue]

        if self.verbose:
            report = [('Queue name', 'Length', 'Ids')]

        for queue in all_queues:
            count = self.r.llen(queue)
            if self.verbose:
                ids = self.r.lrange(queue, 0, count)
                report.append((queue, str(count), "\n".join(ids)))
            else:
                report.append((queue, str(count)))

        if self.csv_format:
            self.csv_out(report)
            return self.report_file
        else:
            return report

    def csv_out(self, report):
        if not os.path.exists(self.report_dir):
            os.makedirs(self.report_dir)
        with open(self.report_file, 'wb') as out:
            csv_out = csv.writer(out)
            for row in report:
                csv_out.writerow(row)
        return

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument("-v", "--verbose", action="store_true", help="report on all queues including queues of length zero; For queues of non-zero length, also include the job ids")
    parser.add_argument("-c", "--csv", action="store_true", help="Save report to disk in csv format; this or --raw is required")
    parser.add_argument("-r", "--raw", action="store_true", help="Display raw output to stdout; this or --csv is required")
    parser.add_argument("-m", "--model", help="ethesis or dataset")
    parser.add_argument("-t", "--task", help="task to display")

    args = parser.parse_args()

    if args.csv is None and args.raw is None:
        parser.print_help()
        exit(0)

    verbose = False
    if args.verbose:
        verbose = True

    make_csv = False
    if args.csv:
        make_csv = True

    r = TaskStatus(verbose=verbose, csv_format=make_csv)

    if args.model is not None and args.task is not None:
        print "Producing report for {x}, {y}".format(x=args.model, y=args.task)
        print r.generate_specific(args.model, args.task)
    else:
        print "Producing report across all models/tasks"
        print r.generate_all()