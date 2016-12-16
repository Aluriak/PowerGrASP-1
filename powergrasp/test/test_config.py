"""Unit tests for Configuration object

"""

import unittest

from powergrasp import config
from powergrasp.config import Configuration as Config


class TestConfig(unittest.TestCase):

    def test_config_basics_lpinput(self):
        cfg = Config(infile='test.lp', outfile='test.dot')
        self.assertEqual(cfg.infile, 'test.lp')
        self.assertEqual(cfg.outfile, 'test.dot')
        self.assertEqual(cfg.network_name, 'test')
        self.assertEqual(cfg.graph_file, 'test.lp')


    def test_config_basics_gmlinput(self):
        with self.assertRaises(FileNotFoundError):
            cfg = Config(infile='test.gml', outfile='test.dot')


    def test_config_cons(self):
        cfg1 = Config(infile='test.lp', outfile='test.gexf')
        cfg2 = Config(infile='well.lp', default=cfg1)
        self.assertEqual(cfg2.infile, 'well.lp')
        self.assertEqual(cfg2.outfile, 'test.gexf')
        self.assertEqual(cfg2.outfile, cfg1.outfile)
        self.assertEqual(cfg2.network_name, 'well')
        self.assertEqual(cfg2.graph_file, 'well.lp')
        self.assertNotEqual(cfg2.network_name, cfg1.network_name)
