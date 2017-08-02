import unittest
import os
from meshlib.stlreader import StlReader


class ReadTest(unittest.TestCase):

    def setUp(self):
        self.obj = StlReader()

    def tearDown(self):
        del self.obj

    def test_read_askii(self):
        input_file_path = os.path.join(".", "input", "cube.stl")
        self.obj.read(input_file_path)
        facets = list(self.obj.get_facets())
        self.assertEqual(len(list(self.obj.get_names())), 4)
        self.assertEqual(len(facets), 12)
        self.assertTrue(self.obj.has_triangular_facets())
