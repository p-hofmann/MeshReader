import os
import unittest
from meshlib.objreader import ObjReader


class ReadTest(unittest.TestCase):
    input = os.path.join(".", "input", "Scaffold.obj")

    def setUp(self):
        self.obj = ObjReader()

    def tearDown(self):
        del self.obj

    def test_read(self):
        self.obj.read(self.input)
        facets = list(self.obj.get_facets())
        self.assertGreaterEqual(len(facets), 2)
        self.assertTrue(self.obj.has_triangular_facets())
