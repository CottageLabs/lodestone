import json
import uuid
import os
from redis import Redis

from service import models
from service.lib.helpers import get_sha1
from octopus.core import app
from octopus.lib import mail


class CrudHelper:
    def __init__(self, model, job_id=None):
        self.model = model
        self.job_id = job_id
        if self.job_id == 'new':
            self.job_id = unicode(uuid.uuid4())
        if model == 'ethesis':
            self.dao = models.Ethesis()
            self.multi_valued_fields = app.config.get('ETHESIS_MULTIVALUED_FIELDS')
            self.submit_queue = app.config.get('ETHESIS_SUBMIT_QUEUE')
        elif model == 'dataset':
            self.dao = models.Dataset()
            self.multi_valued_fields = app.config.get('DATASET_MULTIVALUED_FIELDS')
            self.submit_queue = app.config.get('DATASET_SUBMIT_QUEUE')
        self.dao_record = self.dao.pull(job_id)
        self.redis_host = app.config.get('REDIS_HOST')

    def get_records(self):
        dao_records = map(lambda x: json.loads(x.json()), self.dao.list_all())
        return dao_records

    def get_user_records(self, username):
        dao_records = map(lambda x: json.loads(x.json()), self.dao.list_by_user(username))
        return dao_records

    def get_record(self):
        if self.dao_record:
            record = json.loads(self.dao_record.json())
            if 'files' in record:
                record['files'] = self.dao_record.files
            record['dir'] = self.dao_record.dir
            return record
        return None

    def create_record(self, data, type="metadata"):
        data['id'] = self.job_id

        if type == 'metadata':
            data.pop('files', None)

        for key in self.multi_valued_fields:
            # save these as list objects
            if key in data:
                if not isinstance(data[key], list):
                    data[key] = [data[key]]

        files = []
        if self.dao_record:
            files = self.dao_record.files
            data['created_date'] = self.dao_record.started_raw
        try:
            if self.model == 'ethesis':
                self.dao_record = models.Ethesis(data)
            else:
                self.dao_record = models.Dataset(data)
        except Exception, e:
            print e
            # TODO: Log exception
            # TODO: ES may not be available. In that case reponse should be a 500 and not 400
            return False

        if files:
            for file_data in files:
                self.dao_record.files = file_data

        try:
            self.dao_record.save(blocking=True, max_wait=2.0) # so that the record is available for search immediately after this returns
        except Exception, e:
            print e
            # TODO: Log exception
            # TODO: ES may not be available. In that case reponse should be a 500 and not 400
            return False

        return True

    def delete_record(self):
        base_paths = []
        for val in self.dao.files:
            if os.path.isfile(val['file_path']):
                os.remove(val['file_path'])
            base_paths.append(os.path.dirname(val['file_path']))
        base_paths = list(set(base_paths))
        for base_path in base_paths:
            try:
                os.removedirs(base_path)
            except OSError:
                pass
        self.dao.delete()
        return

    def add_file(self, file_master, file_data):
        if not self.dao_record:
            self.dao.populate({'id': self.job_id})
            self.dao.save()
            self.dao_record = self.dao.pull(self.job_id)
        master_path = os.path.join(self.dao_record.dir, file_master.filename)
        if not os.path.exists(self.dao_record.dir):
            os.makedirs(self.dao_record.dir)
        file_master.save(master_path)
        if self.model == 'ethesis':
            file_url = '/ethesis/%s/files/%s' % (self.job_id, file_master.filename)
        else:
            file_url = '/data/%s/files/%s' % (self.job_id, file_master.filename)
        file_data.update({
            'file_name': file_master.filename,
            'file_path': master_path,
            'file_url': file_url,
            'file_mime_type': file_master.content_type,
            'file_fixity': {'type': 'SHA1', 'value': get_sha1(master_path)},
            'file_size': os.stat(master_path).st_size,
            # 'file_embargoed_until': 'yyyy-mm-dd'
        })
        self.dao_record.files = file_data
        if not self.dao_record.status_code:
            self.dao_record.status_code = 'draft'
        self.dao_record.save()
        return

    def submit_record(self):
        if self.dao_record.status_code != "submit":
            return

        r = Redis(host=app.config.get('REDIS_HOST'))
        r.lpush(self.submit_queue, self.job_id)

