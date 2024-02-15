import unittest
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import ap_dict

class TestApDict(unittest.TestCase):
    def setUp(self):
        pass

    def test_decode(self):
        self.assertEqual(ap_dict.decode("HND"), "東京（羽田）")

if __name__ == "__main__":
    unittest.main()