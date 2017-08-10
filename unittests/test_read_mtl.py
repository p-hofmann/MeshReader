import os
import unittest
from meshlib.mtlreader import MtlReader


class ReadTest(unittest.TestCase):
    input_mtl = os.path.join(".", "input", "Beast Mothership", "Beast Mothership.mtl")
    input_obj = {
        "file": os.path.join(".", "input", "vaygr-mobile-refinery", "source", "2e7e6b3efd3440bcb1bc81388483087a.obj"),
        "dir":  os.path.join(".", "input", "vaygr-mobile-refinery", "textures")
        }

    def setUp(self):
        self.obj = MtlReader()

    def tearDown(self):
        del self.obj

    def test_read(self):
        self.obj.read(self.input_mtl)
        # self.obj.to_stdout()
        self.assertTrue(self.obj.validate_textures())

    def test_reconstruct(self):
        success_failure = self.obj.read(self.input_obj["file"], self.input_obj["dir"])
        # self.obj.to_stdout()
        # print(success_failure)
        self.assertListEqual(success_failure, [9, 1])
