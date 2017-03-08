from octopus.modules.es.testindex import ESTestCase
from service.lib.sword_thesis_deposit import SwordThesisDeposit
from service.lib.sword_data_deposit import SwordDataDeposit
from service import models, deposit
import os, shutil
from service.tests import fixtures
import sword2

REQUESTS = 0
def mock_poll(*args, **kwargs):
    global REQUESTS
    REQUESTS += 1
    statement = sword2.Atom_Sword_Statement()
    receipt = sword2.Deposit_Receipt()

    if REQUESTS < 5:
        statement.states = [("http://dspace.org/state/inreview", "In Review")]
    else:
        statement.states = [("http://dspace.org/state/archived", "Archived")]
        receipt.metadata["dcterms_identifier"] = "10.random/doi"

    return receipt, statement

class TestModels(ESTestCase):
    def setUp(self):
        super(TestModels, self).setUp()
        if os.path.exists("tmp"):
            shutil.rmtree("tmp")
        self.old_poll = deposit.poll

    def tearDown(self):
        super(TestModels, self).tearDown()
        deposit.poll = self.old_poll

    def test_01_thesis_poll(self):
        deposit.poll = mock_poll

        THESIS = fixtures.ThesisFixtureFactory.thesis()
        job_id = THESIS["id"]
        THESIS["edit_iri"] = "http://whatever/"
        et = models.Ethesis(THESIS)
        et.save(blocking=True)

        sword_deposit = SwordThesisDeposit(job_id)

        ans = False
        while sword_deposit.thesis_dao.status_code != "archived":
            ans = sword_deposit.poll_deposit()
            print sword_deposit.thesis_dao.status_code

        print sword_deposit.thesis_dao.status_code

    def test_02_data_poll(self):
        deposit.poll = mock_poll

        DATASET = fixtures.DatasetFixtureFactory.dataset()
        job_id = DATASET["id"]
        DATASET["edit_iri"] = "http://whatever/"
        ds = models.Dataset(DATASET)
        ds.save(blocking=True)

        sword_deposit = SwordDataDeposit(job_id)

        ans = False
        while sword_deposit.data_dao.status_code != "archived":
            ans = sword_deposit.poll_deposit()
            print sword_deposit.data_dao.status_code

        print sword_deposit.data_dao.status_code