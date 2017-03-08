from octopus.modules.es import dao


class EthesisDAO(dao.ESDAO):
    __type__ = 'ethesis'

    @classmethod
    def list_by_status(cls, status):
        q = StatusQuery(status)
        return cls.object_query(q.query())

    @classmethod
    def list_by_type(cls, job_type):
        q = TypeQuery(job_type)
        return cls.object_query(q.query())

    @classmethod
    def list_by_status_and_type(cls, status, job_type):
        q = StatusAndTypeQuery(status, job_type)
        return cls.object_query(q.query())

    @classmethod
    def list_all(cls):
        q = ListAllQuery()
        return cls.object_query(q.query())

    @classmethod
    def query_by_id(cls, job_id):
        return cls.object_query(terms={"id.exact": job_id})

    @classmethod
    def list_by_user(cls, username):
        q = UserQuery(username)
        return cls.object_query(q.query())


class DatasetDAO(dao.ESDAO):
    __type__ = 'dataset'

    @classmethod
    def list_by_status(cls, status):
        q = StatusQuery(status)
        return cls.object_query(q.query())

    @classmethod
    def list_by_type(cls, job_type):
        q = TypeQuery(job_type)
        return cls.object_query(q.query())

    @classmethod
    def list_by_status_and_type(cls, status, job_type):
        q = StatusAndTypeQuery(status, job_type)
        return cls.object_query(q.query())

    @classmethod
    def list_all(cls):
        q = ListAllQuery()
        return cls.object_query(q.query())

    @classmethod
    def query_by_id(cls, job_id):
        return cls.object_query(terms={"id.exact": job_id})

    @classmethod
    def list_by_user(cls, username):
        q = UserQuery(username)
        return cls.object_query(q.query())


class StatusQuery(object):
    def __init__(self, status, size=10):
        self.status = status
        self.size = size

    def query(self):
        return {
            "query": {
                "term": {"status.code.exact": self.status}
            },
            "sort": [{"created_date": {"order": "desc"}}],
            "size": self.size
        }


class TypeQuery(object):
    def __init__(self, job_type, size=10):
        self.job_type = job_type
        self.size = size

    def query(self):
        return {
            "query": {
                "term": {"job_type.exact": self.job_type}
            },
            "sort": [{"created_date": {"order": "desc"}}],
            "size": self.size
        }


class StatusAndTypeQuery(object):
    def __init__(self, status, job_type, size=10):
        self.status = status
        self.job_type = job_type
        self.size = size

    def query(self):
        return {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"status.code.exact": self.status}},
                        {"term": {"job_type.exact": self.job_type}}
                    ]
                }
            },
            "sort": [{"created_date": {"order": "desc"}}],
            "size": self.size
        }


class ListAllQuery(object):
    def __init__(self, size=10):
        self.size = size

    def query(self):
        return {
            "query": {
                "match_all": {}
            },
            "sort": [{"created_date": {"order": "desc"}}],
            "size": self.size
        }


class UserQuery(object):
    def __init__(self, username, size=10):
        self.username = username
        self.size = size

    def query(self):
        return {
            "query": {
                "term": {"user_auth.name.exact": self.username}
            },
            "sort": [{"created_date": {"order": "desc"}}],
            "size": self.size
        }
