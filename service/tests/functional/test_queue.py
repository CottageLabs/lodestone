# override the test index stuff
from octopus.core import app
app.config["ELASTIC_SEARCH_TEST_INDEX"] = app.config["ELASTIC_SEARCH_INDEX"]

from octopus.modules.es.testindex import ESTestCase
from service.lib.crud_helper import CrudHelper
from service import models
import os, shutil
from service.tests import fixtures



UN = "richard@cottagelabs.com"
PW = "dspace"
COL_IRI = "http://localhost:8080/swordv2/collection/123456789/2"
MIMETYPE = "application/zip"
PACKAGING = "http://purl.org/net/sword/package/METSDSpaceSIP"
OBO = None

# we should be making our own payload from the fixture
# PAYLOAD = "/home/richard/Code/External/lodestone/python-client-sword2/tests/databank/example.zip"
PAYLOAD = "/home/richard/Code/External/lodestone/service/tests/resources/package.zip"

class TestModels(ESTestCase):
    def setUp(self):
        super(TestModels, self).setUp()
        if os.path.exists("tmp"):
            shutil.rmtree("tmp")

    def tearDown(self):
        # super(TestModels, self).tearDown()
        pass

    def test_01_push_to_dataset_queue(self):
        # this test just pushes a deposit onto the dataset deposit queue
        # get our fixtures
        DATASET = fixtures.DatasetFixtureFactory.dataset()
        DATASET["iscitedby"] = "10.whatever"    # just to check it is identified correctly
        source_file = fixtures.DatasetFixtureFactory.pdf_path()

        # make an instance of the ethesis object
        job_id = DATASET["id"]
        ds = models.Dataset(DATASET)
        ds.save(blocking=True)

        # copy in our test file
        os.makedirs(ds.dir)
        shutil.copy(source_file, ds.dir)

        ch = CrudHelper("dataset", job_id=ds.id)
        ch.submit_record()

    def test_02_push_to_thesis_queue(self):
        # this test just pushes a deposit onto the dataset deposit queue
        # get our fixtures
        THESIS = fixtures.ThesisFixtureFactory.thesis()
        source_file = fixtures.ThesisFixtureFactory.pdf_path()

        # make an instance of the ethesis object
        job_id = THESIS["id"]
        ds = models.Ethesis(THESIS)
        ds.save(blocking=True)

        # copy in our test file
        os.makedirs(ds.dir)
        shutil.copy(source_file, ds.dir)

        ch = CrudHelper("ethesis", job_id=ds.id)
        ch.submit_record()