import os
from service.lib.helpers import get_sha1


class DataConfirmations:
    def __init__(self, data_dao):
        self.id = data_dao.id
        self.data_dao = data_dao
        self.confirmation_text = ''

        self.sharing_rights = """
I confirm that I have the rights to share these data via the Research Repository.*
"""

        self.confirmation = """
I confirm that I have read and accepted the data deposition terms and conditions
"""
        return

    def save_file(self):
        # remove any old confirmations file
        filename = self.data_dao.id + '_confirmations.txt'
        self.data_dao.delete_file(filename)

        # generate the new one
        self.gather_text()
        file_path = os.path.join(self.data_dao.dir, filename)
        if not os.path.exists(self.data_dao.dir):
            os.makedirs(self.data_dao.dir)
        f = open(file_path, 'w')
        f.write(self.confirmation_text)
        f.close()
        file_data = {
            'file_name': filename,
            'file_description': 'Confirmations agreed by the depositor',
            'file_path': file_path,
            'file_url': '/data/{id}/files/{fn}'.format(id=self.data_dao.id, fn=filename),
            'file_mime_type': 'text/plain',
            'file_fixity': {'type': 'SHA1', 'value': get_sha1(file_path)},
            'file_size': os.stat(file_path).st_size,
            "visible" : False
        }

        # set the property on the object and save
        self.data_dao.files = file_data
        self.data_dao.save()

    def gather_text(self):
        if self.data_dao._get_single('confirm_sharing_rights'):
            self.confirmation_text = self.confirmation_text + self.sharing_rights + '\n\n'
        if self.data_dao._get_single('terms_and_conditions'):
            self.confirmation_text = self.confirmation_text + self.confirmation + '\n\n'
        return
