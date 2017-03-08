from octopus.modules.es.testindex import ESTestCase
from service.lib.sword_thesis_deposit import SwordThesisDeposit, EthesisMets, ThesisConfirmations
from service.lib.sword_data_deposit import SwordDataDeposit, DataMets, DataConfirmations
from service import models
import os, shutil, json
from service.tests import fixtures

class TestModels(ESTestCase):
    def setUp(self):
        super(TestModels, self).setUp()
        if os.path.exists("tmp"):
            shutil.rmtree("tmp")

    def tearDown(self):
        super(TestModels, self).tearDown()

    def test_01_thesis_mets(self):
        THESIS = fixtures.ThesisFixtureFactory.thesis()
        et = models.Ethesis(THESIS)
        et.save(blocking=True)
        t = ThesisConfirmations(et)
        t.save_file()
        thesis = json.loads(et.json())
        if 'files' in thesis:
            thesis['files'] = et.files
        thesis['dir'] = et.dir
        mets = EthesisMets(thesis)
        print mets.xml()

    def test_02_thesis_package(self):
        THESIS = fixtures.ThesisFixtureFactory.thesis()
        job_id = THESIS["id"]
        et = models.Ethesis(THESIS)
        et.save(blocking=True)

        sword_deposit = SwordThesisDeposit(job_id)
        sword_deposit.prepare_deposit()

    def test_03_data_mets(self):
        DATASET = fixtures.DatasetFixtureFactory.dataset()
        ds = models.Dataset(DATASET)
        ds.save(blocking=True)
        t = DataConfirmations(ds)
        t.save_file()
        dataset = json.loads(ds.json())
        dataset["iscitedby"] = "10.whatever"    # just to check it is identified correctly
        if 'files' in dataset:
            dataset['files'] = ds.files
        dataset['dir'] = ds.dir
        mets = DataMets(dataset)
        print mets.xml()

    def test_04_data_package(self):
        DATASET = fixtures.DatasetFixtureFactory.dataset()
        job_id = DATASET["id"]
        ds = models.Dataset(DATASET)
        ds.save(blocking=True)

        sword_deposit = SwordDataDeposit(job_id)
        sword_deposit.prepare_deposit()