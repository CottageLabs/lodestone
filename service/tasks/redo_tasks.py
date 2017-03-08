from octopus.core import app
from redis import Redis


class RedoTasks:
    """
    from service.tasks.redo_tasks import RedoTasks
    r = RedoTasks(model, task)
        # Model has to be one of 'ethesis' or 'dataset'
        # Task has to be one of 'deposit', 'poll' or 'ticket create'

    r.all() # to redo all jobs in given model and task

    r.job(id) # to redo a specific job in a given model and task
    """
    def __init__(self, model, task):
        if model not in ['ethesis', 'dataset']:
            raise ValueError("Model has to be one of 'ethesis' or 'dataset'")
        if task not in ['deposit', 'poll']:
            raise ValueError("Task has to be one of 'deposit' or 'poll'")
        self.r = Redis()
        self.model = model
        self.task = task
        self.queue = None
        self.error_queue = None
        if model == 'dataset':
            if task == 'deposit':
                self.queue = app.config.get('DATASET_SUBMIT_QUEUE')
            elif task == 'poll':
                self.queue = app.config.get('DATASET_POLL_QUEUE')
        elif model == 'ethesis':
            if task == 'deposit':
                self.queue = app.config.get('ETHESIS_SUBMIT_QUEUE')
            elif task == 'poll':
                self.queue = app.config.get('ETHESIS_POLL_QUEUE')
        if not self.queue:
            raise ValueError("There is no queue defined for this model and task")
        self.error_queue = "%s_error" % self.queue

    def all(self):
        while self.r.llen(self.error_queue) > 0:
            self.r.rpoplpush(self.error_queue, self.queue)

    def job(self, job_id):
        if self.r.lrem(self.error_queue, job_id) > 0:
            self.r.lpush(self.queue, job_id)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument("-m", "--model", help="ethesis or dataset")
    parser.add_argument("-t", "--task", help="task to restart")
    parser.add_argument("-j", "--job", help="optional job id from error queue; you must have this or --all")
    parser.add_argument("-a", "--all", action="store_true", help="restart the task for all existing errors; you must have this or --job")

    args = parser.parse_args()
    if args.model is None or args.task is None:
        parser.print_help()
        exit(0)

    if args.job is None and args.all is None:
        parser.print_help()
        exit(0)

    r = RedoTasks(args.model, args.task)
    if args.job is not None:
        print "Acting on job {x} in {y} error queue".format(x=args.job, y=args.model)
        r.job(args.job)
    else:
        print "Acting on all jobs in {x} error queue".format(x=args.model)
        r.all()