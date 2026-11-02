"""In-memory canonical slot regression; never rewrites a manifest or user card."""
import copy
import unittest
from generate_managed_recipe_overhaul import sequenced


class CanonicalSequenceFluidTest(unittest.TestCase):
    def test_fluid_and_fluid_tag_use_native_step_item_key(self):
        for fluid in ({'kind': 'FLUID', 'id': 'minecraft:water', 'amount': 250},
                      {'kind': 'FLUID_TAG', 'id': 'c:water', 'amount': 500}):
            with self.subTest(fluid=fluid):
                spec = {'id': 'industrial_colonies:test/fluid', 'type': 'sequenced_assembly',
                        'phase': 'Electrical Manufacturing', 'comment': 'Canonical filling regression',
                        'input': 'tfmg:silicon_ingot', 'transitional': 'tfmg:silicon_ingot',
                        'output': '2x tfmg:n_semiconductor', 'loops': 2,
                        'steps': [{'op': 'deploying', 'ingredient': 'tfmg:copper_wire',
                                   'machine': 'createcasing:copper_deployer'},
                                  {'op': 'filling', 'fluid': fluid, 'machine': 'create:spout'}]}
                before = copy.deepcopy(spec)
                card = sequenced(spec, 'test-uid')
                self.assertEqual(spec, before)
                self.assertNotIn('seqFluid1', card['slots'])
                self.assertEqual(card['slots']['seqItem1']['amount'], fluid['amount'])
                self.assertEqual(card['slots']['seqItem1']['kind'], fluid['kind'])
                self.assertEqual(card['slots']['seqItem0']['id'], 'tfmg:copper_wire')
                self.assertEqual(card['slots']['__machine_step_1_filling']['id'], 'create:spout')
                self.assertEqual(card['params']['loops'], '2')
                self.assertEqual(card['slots']['output0']['count'], 2)


if __name__ == '__main__':
    unittest.main()
