from service.dao import DatasetDAO
from octopus.lib import dataobj
from dateutil.parser import parse
import shutil
import os
from octopus.core import app

class Dataset(dataobj.DataObj, DatasetDAO):

    @property
    def dataset_id(self):
        return self._get_single("id", self._utf8_unicode())

    @property
    def dir(self):
        job_id = self.dataset_id
        file_dir = os.path.join(app.config.get('DATASET_UPLOAD_DIR'), job_id[:2], job_id[2:4], job_id[4:])
        return file_dir

    def burn_dir(self):
        dir = self.dir
        if os.path.exists(dir):
            shutil.rmtree(dir)

        job_id = self.dataset_id

        parent1 = os.path.join(app.config.get('DATASET_UPLOAD_DIR'), job_id[:2], job_id[2:4])
        if os.path.exists(parent1) and len(os.listdir(parent1)) == 0:
            shutil.rmtree(parent1)

        parent2 = os.path.join(app.config.get('DATASET_UPLOAD_DIR'), job_id[:2])
        if os.path.exists(parent2) and len(os.listdir(parent2)) == 0:
            shutil.rmtree(parent2)

    @property
    def started_display(self):
        dt = self._get_single("created_date", self._utf8_unicode())
        return parse(dt).strftime('%d-%m-%Y %H:%M')

    @property
    def started_raw(self):
        dt = self._get_single("created_date", self._utf8_unicode())
        return dt

    @property
    def status_code(self):
        return self._get_single("status.code", self._utf8_unicode())

    @status_code.setter
    def status_code(self, val):
        # self._set_single("status.code", val, self._utf8_unicode(), allowed_values=self.STATUS_CODES)
        self._set_single("status.code", val, self._utf8_unicode())

    @property
    def status_message(self):
        return self._get_single("status.message", self._utf8_unicode())

    @status_message.setter
    def status_message(self, val):
        self._set_single("status.message", val, self._utf8_unicode())

    @property
    def edit_iri(self):
        return self._get_single("edit_iri", self._utf8_unicode())

    @edit_iri.setter
    def edit_iri(self, val):
        self._set_single("edit_iri", val, self._utf8_unicode())

    @property
    def doi(self):
        return self._get_single("doi", self._utf8_unicode())

    @doi.setter
    def doi(self, val):
        self._set_single("doi", val, self._utf8_unicode())

    @property
    def ticket_id(self):
        return self._get_single("ticket_id", self._utf8_unicode())

    @ticket_id.setter
    def ticket_id(self, val):
        self._set_single("ticket_id", val, self._utf8_unicode())

    @property
    def files(self):
        return self._get_list("files")

    @files.setter
    def files(self, val):
        self._add_to_list("files", val, ignore_none=True,  unique=False)

    def is_placeholder(self):
        return self._get_single("placeholder")

    def delete_file(self, file_name):
        files_list = self.files
        file_path = None
        new_list = []
        for f in files_list:
            if f['file_name'] != file_name:
                new_list.append(f)
            else:
                file_path = f['file_path']

        if file_path is not None:
            if os.path.isfile(file_path):
                os.remove(file_path)
            if len(new_list) == 0:
                self.burn_dir()

        self._set_list("files", new_list)

    def remove_files(self):
        self._set_list("files", [])
        self.burn_dir()

    def tombstone(self):
        # remove all the files
        self.remove_files()
        self.status_code = "tombstone"

    @property
    def crsid(self):
        return self._get_single("crsid", coerce=self._utf8_unicode())

    @property
    def external_email(self):
        return self._get_single("externalemail", coerce=self._utf8_unicode())

    @property
    def user_email(self):
        return self._get_single("user_auth.email", coerce=self._utf8_unicode())

    @property
    def given_names(self):
        return self._get_single("given_names", coerce=self._utf8_unicode())

    @property
    def title(self):
        return self._get_single("title", coerce=self._utf8_unicode())

    @property
    def remote_repository_url(self):
        return self._get_single("remote_repository_url", coerce=self._utf8_unicode())

    @remote_repository_url.setter
    def remote_repository_url(self, val):
        self._set_single("remote_repository_url", val, coerce=self._utf8_unicode())

    @property
    def doi(self):
        return self._get_single("doi", coerce=self._utf8_unicode())

    @doi.setter
    def doi(self, val):
        self._set_single("doi", val, coerce=self._utf8_unicode())

    @property
    def webhook_callback(self):
        return self._get_single("webhook_callback", self._utf8_unicode())

    @webhook_callback.setter
    def webhook_callback(self, val):
        self._set_single("webhook_callback", val, self._utf8_unicode(), ignore_none=True)
