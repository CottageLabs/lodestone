import os
from service.lib.helpers import get_sha1

class ThesisConfirmations:
    def __init__(self, thesis):
        self.id = thesis.id
        self.thesis_dao = thesis
        self.confirmation_text = ''

        self.open_access_ip_confirmed = """
I confirm that the open access version of my thesis does not infringe the intellectual property rights of a
third party OR that all parties with a claim to intellectual property contained in any content in my thesis have
agreed to the deposit of my thesis in the repository and dissemination online.*
"""

        self.open_access_confidentiality_confirmed = """
I confirm that the open access version of my thesis does not contain confidential information or that I have
obtained permission from the authorised party to make the confidential information public.*
"""

        self.authenticity_agreement = """
I certify that this is a direct digital equivalent of the copy of my thesis approved by the University for the
award of the degree. No emendation of content has occurred, and if there are any minor variations in formatting,
they are a result of the conversion to Adobe Acrobat format.
"""

        self.distribution_license = """
This document is a contract between you and the University, which constitutes your permission to
deposit, archive, preserve and make your submission ("Research Outputs") available in the Repository on the terms set out
below. References to the Repository include any successor repository
designated by the University.

1. Licence Grant. In consideration of the University (the "University") preserving Research Outputs
in the University institutional repository (the "Repository"), I hereby grant to the University a
non-exclusive, sublicensable, worldwide, perpetual and royalty-free licence to use and reproduce these Research
Outputs in any medium or format for the purposes of archiving, preservation and migration of Research Outputs in
the Repository and, subject to any agreed publication delay or embargo or restricted access, to communicate and
make available to the public Research Outputs in the Repository under the terms of this Licence and any licence
or other terms that may be specified in the Repository deposit submission process and/or that Research Outputs
may be tagged with or otherwise released under in the Repository.

2. Depositor Warranties. I represent and warrant that:

2.1 I have the full power and authority to enter into this Agreement and am duly authorised by all rights
holder/s Research Outputs to deposit or authorise the deposit of Research Outputs in the Repository and grant
the licence in this Agreement;

2.2 Research Outputs are original work and do not, to the best of my knowledge, infringe the intellectual
property rights, including copyright, of any third party, nor contain any confidential information, personal
and/or restricted data;

2.3 jointly owned or third party copyright material, i.e. others' work, included in Research Outputs, is clearly
identified and acknowledged and sufficient and appropriate permissions have been secured for the material to be
reproduced and made available on the licence terms Research Outputs are released under in the Repository; and

2.4 the grant of rights in this Agreement does not constitute a breach of any other agreement, publishing or
otherwise, including any confidentiality or publication restriction provisions in sponsorship, or United
Kingdom export control law, or collaboration agreements governing my research or work (or that of those who have
authorised me to grant rights given in this Agreement on their behalf) at the University or elsewhere.

3. University Repository Policy. I acknowledge and agree that I have read and understood the University
Repository Terms of Use at www.repository.xxxxxxx.ac.uk and that my deposit of Research Outputs complies with
those terms. I acknowledge that the University Repository Terms of Use may be amended from time to time and
that then current policies will apply to my submission.

4. Governing Law and Jurisdiction. This Agreement and all questions of construction, validity and performance
under this Agreement shall be governed by English law and subject to the exclusive jurisdiction of the English
courts.
"""
        return

    def save_file(self):
        # remove any old confirmations file
        filename = self.thesis_dao.id + '_confirmations.txt'
        self.thesis_dao.delete_file(filename)

        # generate the new one
        self.gather_text()
        file_path = os.path.join(self.thesis_dao.dir, filename)
        if not os.path.exists(self.thesis_dao.dir):
            os.makedirs(self.thesis_dao.dir)
        f = open(file_path, 'w')
        f.write(self.confirmation_text)
        f.close()
        file_data = {
            'file_name': filename,
            'file_description': 'Confirmations agreed by the depositor',
            'file_path': file_path,
            'file_url': '/ethesis/{id}/files/{fn}'.format(id=self.thesis_dao.id, fn=filename),
            'file_mime_type': 'text/plain',
            'file_fixity': {'type': 'SHA1', 'value': get_sha1(file_path)},
            'file_size': os.stat(file_path).st_size,
            "visible" : False
        }

        # set the property on the object and save
        self.thesis_dao.files = file_data
        self.thesis_dao.save()

    def gather_text(self):
        if self.thesis_dao._get_single('open_access_ip_confirmed'):
            self.confirmation_text = self.confirmation_text + self.open_access_ip_confirmed + '\n\n'
        if self.thesis_dao._get_single('open_access_confidentiality_confirmed'):
            self.confirmation_text = self.confirmation_text + self.open_access_confidentiality_confirmed + '\n\n'
        if self.thesis_dao._get_single('authenticity_agreement'):
            self.confirmation_text = self.confirmation_text + self.authenticity_agreement + '\n\n'
        if self.thesis_dao._get_single('distribution_license'):
            self.confirmation_text = self.confirmation_text + self.distribution_license + '\n\n'
        return
