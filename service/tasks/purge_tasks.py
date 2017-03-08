from octopus.core import app
from redis import Redis
from service import models
import shutil, os


class PurgeTasks:
    """
    from service.tasks.redo_tasks import RedoTasks
    r = PurgeTasks(model)
        # Model has to be one of 'ethesis' or 'dataset'

    r.job(id) # to redo a specific job in a given model and task
    """
    def __init__(self, model):
        if model not in ['ethesis', 'dataset']:
            raise ValueError("Model has to be one of 'ethesis' or 'dataset'")
        self.r = Redis()
        self.model = model
        self.queues = []
        self.error_queue = None
        if model == 'dataset':
            self.queues = [
                app.config.get('DATASET_SUBMIT_QUEUE'),
                app.config.get('DATASET_POLL_QUEUE'),
            ]
        elif model == 'ethesis':
            self.queues = [
                app.config.get('ETHESIS_SUBMIT_QUEUE'),
                app.config.get('ETHESIS_POLL_QUEUE')
            ]

        if len(self.queues) == 0:
            raise ValueError("There is no queue defined for this model and task")

        error_queues = []
        for val in self.queues:
            error_queues.append("%s_error" % val)
        self.queues += error_queues

    def job(self, job_id):
        count = 0
        for queue in self.queues:
            count += self.r.lrem(queue, job_id)
        if count > 0:
            self._purge(job_id)

    def _purge(self, job_id):
        obj = None
        if self.model == "ethesis":
            obj = models.Ethesis.pull(job_id)
        elif self.model == "dataset":
            obj = models.Dataset.pull(job_id)
        if obj is None:
            return False

        obj.burn_dir()

        zipfile = os.path.join(app.config.get('SWORD_DEPOSIT_DIR'), '%s.zip' % job_id)
        if os.path.exists(zipfile):
            os.remove(zipfile)
        obj.delete()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument("-m", "--model", help="ethesis or dataset")
    parser.add_argument("-j", "--job", help="job id to purge")

    args = parser.parse_args()
    if args.model is None or args.job is None:
        parser.print_help()
        exit(0)

    r = PurgeTasks(args.model)
    print "Purging job {x}".format(x=args.job)
    r.job(args.job)