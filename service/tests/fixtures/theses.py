# -*- coding: utf-8 -*-

from copy import deepcopy
from octopus.lib import paths

class ThesisFixtureFactory(object):
    @classmethod
    def thesis(cls):
        return deepcopy(THESIS)

    @classmethod
    def pdf_path(cls):
        return paths.rel2abs(__file__, "..", "resources", "package", "pdf1.pdf")

THESIS = {
    "status": {
        "code": "submit"
    },
    "files": [
        {
            "file_name": "pdf1.pdf",
            "file_url": "/ethesis/ad8e6ab2-dc18-4b4f-aa14-5f7c2f148788/files/pdf1.pdf",
            "file_description": [
                "Description"
            ],
            "file_size": 11083,
            "file_fixity": {
                "type": "SHA1",
                "value": "b6258643fddb6ae3578be2c6852ba92fd93a87e1"
            },
            "file_mime_type": "application/pdf",
            "file_path": "tmp/data/etheses/ad/8e/6ab2-dc18-4b4f-aa14-5f7c2f148788/pdf1.pdf",
            "software": [
                "Software"
            ]
        }
    ],
    "last_updated": "2016-11-16T16:38:10Z",
    "open_access_ip_confirmed": True,
    "degree": "Doctor of Philosophy (PhD)",
    "abstract": "My Abstract",
    "qualification_level": "Doctoral",
    "authenticity_agreement": True,
    "distribution_license": True,
    "user_auth": {
        "name": "user1",
        "session_id": "user-session-id-in-some-long-string",
        "email": "user1@example.com"
    },
    "supervisors": [
        {
            "orcid": "1111-1111-1111-1111",
            "family_name": "Ranganathan",
            "given_names": "Anusha"
        }
    ],
    "date_awarded": "2016-11-01",
    "faculty": "Physics",
    "keywords": [
        "one",
        "two",
        "three"
    ],
    "id": "ad8e6ab2-dc18-4b4f-aa14-5f7c2f148788",
    "degree_title": "Physics",
    "license": {
        "text": "CC BY-ND (Attribution-NoDerivs)",
        "uri" : "https://creativecommons.org/licenses/by-nc-nd/3.0/"
    },
    "funding": "Funding",
    "open_access_confidentiality_confirmed": True,
    "language": [
        "en",
        "es"
    ],
    "title": u"On Physics with spéciâl chars",
    "college": "Kings",
    "awarding_institution": "University of XXXXXX",
    "comments": "Description/comments",
    "access": {
        "restrict_reason": "Just because",
        "type": "restrict_one"
    },
    "authors": [
        {
            "orcid": "0000-0000-0000-0000",
            "family_name": "Jones",
            "email_id": "richard@example.com",
            "crsid": "abc12",
            "given_names": "Richard"
        }
    ],
    "created_date": "2016-11-16T16:38:02Z",
    "third_party_copyright_notes": "third party copyright"
}