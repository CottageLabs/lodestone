from copy import deepcopy
from octopus.lib import paths

class DatasetFixtureFactory(object):
    @classmethod
    def dataset(cls):
        return deepcopy(DATASET)

    @classmethod
    def pdf_path(cls):
        return paths.rel2abs(__file__, "..", "resources", "package", "pdf1.pdf")

DATASET = {
    "funders": [
        {
            "project_id": "WEL1",
            "name": "Wellcome"
        }
    ],
    "files": [
        {
            "file_name": "pdf1.pdf",
            "file_url": "/data/ad8e6ab2-dc18-4b4f-aa14-5f7c2f148788/files/pdf1.pdf",
            "file_format": [
                "Format"
            ],
            "file_size": 11083,
            "file_fixity": {
                "type": "SHA1",
                "value": "b6258643fddb6ae3578be2c6852ba92fd93a87e1"
            },
            "file_mime_type": "application/pdf",
            "file_path": "tmp/data/datasets/ad/8e/6ab2-dc18-4b4f-aa14-5f7c2f148788/pdf1.pdf",
            "software": [
                "Software"
            ]
        }
    ],
    "doi" : "10.I/made.this",
    "last_updated": "2016-12-07T15:57:46Z",
    "iscitedby": "http://journal",
    "twitter": "@twitter",
    "terms_and_conditions": True,
    "user_auth": {
        "name": "user1",
        "session_id": "user-session-id-in-some-long-string",
        "email": "user1@example.com"
    },
    "publicationtitle": "My Publication",
    "keywords": [
        "one",
        "two",
        "three"
    ],
    "publicise": True,
    "given_names": "Richard",
    "has_publication": True,
    "confirm_sharing_rights": True,
    "title": "Research data supporting 'My Publication'",
    "id": "49993ade-4ecc-47cb-914b-a0b9ffa494a5",
    "peerreviewaccess": True,
    "accessrights": "Restriction",
    "journal_name": "Journal",
    "department": "Department",
    "resources": [
        {
            "url": "http://webpage",
            "type": "webpage"
        },
        {
            "url": "http://sourcecode",
            "type": "sourcecode"
        },
        {
            "url": "http://otherpublication",
            "type": "otherpublication"
        },
        {
            "url": "http://conferenceoutput",
            "type": "conferenceoutput"
        },
        {
            "url": "http://otherdataset",
            "type": "otherdataset"
        },
        {
            "url": "http://report",
            "type": "report"
        },
        {
            "url": "http://blog",
            "type": "blog"
        },
        {
            "url": "http://other",
            "type": "other"
        }
    ],
    "status": {
        "code": "submit"
    },
    "additionalinfo": "Additional",
    "description": "Description",
    "crsid": "crs12",
    "publication_published": False,
    "confidential_information": True,
    "authors": [
        {
            "orcid": "0000-0000-0000-0000",
            "family_name": "Jones",
            "supervisor": True,
            "given_names": "Richard"
        },
        {
            "orcid": "1111-1111-1111-1111",
            "family_name": "Ranganathan",
            "given_names": "Anusha"
        }
    ],
    "publication_date": "2016-12-01",
    "external_funding": True,
    "placeholder": True,
    "embargo": True,
    "family_name": "Jones",
    "license": {
        "text": "GPLv3",
        "uri": "https://www.gnu.org/licenses/gpl-3.0.en.html"
    },
    "externalemail": "test@example.com",
    "created_date": "2016-12-07T15:57:43Z",
    "currently_employed": True,
    "software_information" : "Software Information"
}