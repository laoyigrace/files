from pymongo import MongoClient
from pymongo import DESCENDING


# Create your models here.
DbConfig = {
    "host": "mongodb.cpt.com",# 200.200.177.11
    "user": "root",
    "password": "root",
    "port": 27017
}


class DbBase(object):
    def __init__(self, host=None, port=27017, user=None, password=None):
        if host is None:
            host = DbConfig["host"]

        self.client = MongoClient(host, int(port))


class BuildsResult(DbBase):
    def __init__(self, db_name="jenkins", collection_name="builds"):
        super(BuildsResult, self).__init__()
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def find(self, query=None, skip=0, limit=10):
        if query is not None:
            builds = self.collection.find(query).sort("build_num", DESCENDING).skip(skip).limit(limit)
        else:
            builds = self.collection.find().sort("build_num").skip(skip).limit(limit)

        return builds

    def count(self, query=None):
        if query is not None:
            count = self.collection.find(query).count()
        else:
            count = self.collection.find().count()

        return count

    def latest_pkg_nums(self, result="PASS"):
        build = self.collection.find(
            {"job_name": "physical_smoke_tempest_run", "result": "PASSED"}).\
            sort("package_version", DESCENDING).limit(1)
        return build[0]

    def jobs(self):
        jobs = self.collection.distinct(key="job_name")
        return jobs

class Email(DbBase):
    def __init__(self, db_name="jenkins", collection_name="email"):
        super(Email, self).__init__()
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def sub_email(self, id):
        count = self.collection.find({'id': id}).count()
        if count > 0:
            return
        self.collection.insert_one({'id': id})

    def unsub_email(self, id):
        count = self.collection.find({'id': id}).count()
        if count < 1:
            return
        self.collection.remove({'id': id})

    def find(self, query=None):
        if query is not None:
            emails = self.collection.find(query)
        else:
            emails = self.collection.find()

        return emails