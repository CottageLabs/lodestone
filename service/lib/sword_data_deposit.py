import json
import os
from service import deposit
from octopus.core import app
from service import models
from service.lib.data_confirmations import DataConfirmations
from service.lib.helpers import create_zip_file
from service.lib.data_mets import DataMets


class DataNotFound(Exception):
    pass


class SwordDataDeposit:
    def __init__(self, job_id):
        self.job_id = job_id
        self.data_dao = models.Dataset.pull(self.job_id)
        if not self.data_dao:
            raise DataNotFound("Could not find dataset with id %s" % job_id)
        self.username = app.config.get('SWORD_USERNAME')
        self.password = app.config.get('SWORD_PASSWORD')
        self.collection_iri = app.config.get('SWORD_DATASET_COLLECTION_IRI')
        if not os.path.exists(app.config.get('SWORD_DEPOSIT_DIR')):
            os.makedirs(app.config.get('SWORD_DEPOSIT_DIR'))
        self.zip_file = os.path.join(app.config.get('SWORD_DEPOSIT_DIR'), '%s.zip' % self.job_id)
        return

    def deposit_dataset(self):
        # MIMETYPE = "application/zip"
        # PACKAGING = "http://purl.org/net/sword/package/METSDSpaceSIP"
        on_behalf_of = None
        try:
            edit_iri = deposit.deposit(self.zip_file, self.username, self.password, self.collection_iri, on_behalf_of)
        except:
            self.data_dao.status_code = "error"
            self.data_dao.save()
            raise

        if edit_iri:
            self.data_dao.edit_iri = edit_iri
            self.data_dao.status_code = 'review'
            self.data_dao.save()
            # Delete sword package on disk
            os.remove(self.zip_file)
            return True
        else:
            self.data_dao.status_code = "error"
            self.data_dao.save()
            return False

    def poll_deposit(self):
        if not self.data_dao.edit_iri:
            return 'Error'

        receipt, statement = deposit.poll(self.data_dao.edit_iri, self.username, self.password)
        if statement is None:
            self.data_dao.tombstone()
            self.data_dao.save()
            return True

        save = False

        # look to see if we've got a doi
        # first look in dcterms:identifier
        identifiers = receipt.metadata.get("dcterms_identifier")
        doi = None
        if identifiers is not None and len(identifiers) > 0:
            doi = identifiers[0]
        # if not there, look in dcterms:isVersionOf
        if doi is None:
            identifiers = receipt.metadata.get("dcterms_isVersionOf")
            if identifiers is not None and len(identifiers) > 0:
                doi = identifiers[0]
        # if we found it, and we didn't already have it, store it
        if doi is not None and self.data_dao.doi is None:
            self.data_dao.doi = doi
            save = True

        for term, text in statement.states:
            status = term.split('/')[-1]
            if status and self.data_dao.status_code != status:
                # State has changed
                self.data_dao.status_code = status
                if text:
                    self.data_dao.status_message = text
                else:
                    self.data_dao.status_message = ""

                if 'archived' in status:
                    self.data_dao.remote_repository_url = receipt.alternate
                    self.update_files(statement.resources)
                    # item is saved by update_files, to ensure record and disk consistency
                    return True
                elif "inprogress" in status:
                    self.data_dao.tombstone()
                    self.data_dao.save()
                    return True
                else:
                    self.data_dao.save()
                    return False
        if save:
            self.data_dao.save()

        return False

    def prepare_deposit(self):
        if not self.data_dao:
            return False
        t = DataConfirmations(self.data_dao)
        t.save_file()
        dataset = json.loads(self.data_dao.json())
        if 'files' in dataset:
            dataset['files'] = self.data_dao.files
        dataset['dir'] = self.data_dao.dir
        mets = DataMets(dataset)
        mets.save_xml()
        create_zip_file(self.data_dao.dir, self.zip_file)
        return

    def update_files(self, resources):
        dspace_files = {}
        for rsrc in resources:
            fp = rsrc.cont_iri
            fn = fp.strip('/ ').split('/')[-1]
            dspace_files[fn] = fp

        new_files = []
        modified = False
        for f in self.data_dao.files:
            if f['file_name'] == self.data_dao.id + '_confirmations.txt':
                modified = True
                if f['file_path'] and os.path.isfile(f['file_path']):
                    os.remove(f['file_path'])
            elif f['file_name'] in dspace_files:
                modified = True
                f['file_url'] = dspace_files[f['file_name']]
                if f['file_path']:
                    if os.path.isfile(f['file_path']):
                        os.remove(f['file_path'])
                    f['file_path'] = None
                new_files.append(f)
            else:
                new_files.append(f)
        if modified:
            self.data_dao._set_list("files", new_files)
            self.data_dao.save()
            self.data_dao.burn_dir()
        return