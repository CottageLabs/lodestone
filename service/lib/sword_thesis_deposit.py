import json
import os
from service import deposit
from octopus.core import app
from service import models
from service.lib.thesis_confirmations import ThesisConfirmations
from service.lib.helpers import create_zip_file
from service.lib.ethesis_mets import EthesisMets


class ThesisNotFound(Exception):
    pass


class SwordThesisDeposit:
    def __init__(self, job_id):
        self.job_id = job_id
        self.thesis_dao = models.Ethesis.pull(self.job_id)
        if not self.thesis_dao:
            raise ThesisNotFound("Could not find thesis with id %s" % job_id)
        self.username = app.config.get('SWORD_USERNAME')
        self.password = app.config.get('SWORD_PASSWORD')
        self.collection_iri = app.config.get('SWORD_ETHESIS_COLLECTION_IRI')
        if not os.path.exists(app.config.get('SWORD_DEPOSIT_DIR')):
            os.makedirs(app.config.get('SWORD_DEPOSIT_DIR'))
        self.zip_file = os.path.join(app.config.get('SWORD_DEPOSIT_DIR'), '%s.zip' % self.job_id)
        return

    def deposit_thesis(self):
        # MIMETYPE = "application/zip"
        # PACKAGING = "http://purl.org/net/sword/package/METSDSpaceSIP"
        on_behalf_of = None
        try:
            edit_iri = deposit.deposit(self.zip_file, self.username, self.password, self.collection_iri, on_behalf_of)
        except:
            self.thesis_dao.status_code = "error"
            self.thesis_dao.save()
            raise

        if edit_iri:
            self.thesis_dao.edit_iri = edit_iri
            self.thesis_dao.status_code = 'review'
            self.thesis_dao.save()
            # Delete sword package on disk
            os.remove(self.zip_file)
            return True
        else:
            self.thesis_dao.status_code = "error"
            self.thesis_dao.save()
            return False

    def poll_deposit(self):
        if not self.thesis_dao.edit_iri:
            return 'Error'

        receipt, statement = deposit.poll(self.thesis_dao.edit_iri, self.username, self.password)
        if statement is None:
            self.thesis_dao.tombstone()
            self.thesis_dao.save()
            return True

        for term, text in statement.states:
            status = term.split('/')[-1]
            if status and self.thesis_dao.status_code != status:
                # State has changed
                self.thesis_dao.status_code = status
                if text:
                    self.thesis_dao.status_message = text
                else:
                    self.thesis_dao.status_message = ""

                if 'archived' in status:
                    self.thesis_dao.remote_repository_url = receipt.alternate
                    self.update_files(statement.resources)
                    # item is saved by update_files, to ensure record and disk consistency
                    # self.thesis_dao.save()
                    return True
                elif "inprogress" in status:
                    self.thesis_dao.tombstone()
                    self.thesis_dao.save()
                    return True
                else:
                    self.thesis_dao.save()
                    return False
        return False

    def prepare_deposit(self):
        if not self.thesis_dao:
            return False
        t = ThesisConfirmations(self.thesis_dao)
        t.save_file()
        thesis = json.loads(self.thesis_dao.json())
        if 'files' in thesis:
            thesis['files'] = self.thesis_dao.files
        thesis['dir'] = self.thesis_dao.dir
        mets = EthesisMets(thesis)
        mets.save_xml()
        create_zip_file(self.thesis_dao.dir, self.zip_file)
        return

    def update_files(self, resources):
        dspace_files = {}
        for rsrc in resources:
            fp = rsrc.cont_iri
            fn = fp.strip('/ ').split('/')[-1]
            dspace_files[fn] = fp

        new_files = []
        modified = False
        for f in self.thesis_dao.files:
            if f['file_name'] == self.thesis_dao.id + '_confirmations.txt':
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
            self.thesis_dao._set_list("files", new_files)
            self.thesis_dao.save()
            self.thesis_dao.burn_dir()
        return