from gatekeeper.models import GateKeeper
from testing.testcase import TestCase


class GateKeeperTests(TestCase):

    def setUp(self):
        self.clear_cache()

    def test_gatekeeper(self):
        gk = GateKeeper.get('gk_name')
        self.assertEqual(gk, {'percentage': 0, 'description': ''})
        self.assertEqual(GateKeeper.is_switch_on('gk_name'), False)
        self.assertEqual(GateKeeper.in_gk('gk_name', 1), False)

        GateKeeper.set_kv('gk_name', 'percentage', 20)
        self.assertEqual(GateKeeper.is_switch_on('gk_name'), False)
        self.assertEqual(GateKeeper.in_gk('gk_name', 1), True)

        GateKeeper.set_kv('gk_name', 'percentage', 100)
        self.assertEqual(GateKeeper.is_switch_on('gk_name'), True)
        self.assertEqual(GateKeeper.in_gk('gk_name', 1), True)

