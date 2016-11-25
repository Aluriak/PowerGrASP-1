"""
Test on graph compression.

"""
import unittest
import tempfile

from powergrasp import commons
from powergrasp import recipes
from powergrasp import config


class TestUnambiguousCompression(unittest.TestCase):
    """This class yields many subtests about unambiguous compression results.

    The test case and associated results are defined in setUp() method.
    Bubble outputs are comparated, excluding comments and empty lines.

    The unambiguous compression is important : bubble comparison is sensitive
    to powernodes numbers and related.
    However, it resists to multiple connected components.

    """

    def setUp(self):
        self.test_cases = {
            'double_biclique_unambiguous.lp' : RESULT_DDIAMUN,
            'bipartite.lp'                   : RESULT_BIP,
            'testblocks.lp'                  : RESULT_BLO,
            'perfectfit.lp'                  : RESULT_PFC,
            'clique.lp'                      : RESULT_CLIQUE,
            'star.lp'                        : RESULT_STAR,
            'concomp.lp'                     : RESULT_CC,
            'ecoli_2896-53.gml'              : RESULT_ECOLI,
            'test.graphml'                   : RESULT_GRAPHML,
            'one_edge.lp'                    : RESULT_ONEDGE,
            'test.gml'                       : RESULT_TESTGML,
            'empty.lp'                       : '',
        }


    def unified_bubble(self, bubble_lines):
        """Return the set of comparable lines found in given bubble lines"""
        # filter out comments and blank lines
        return set(line.strip() for line in bubble_lines
                   if not line.startswith('#') and len(line.strip()) > 0)

    def unified_bubble_from_file(self, bubble_file):
        """Return the set of comparable lines found in given bubble file"""
        with open(bubble_file) as fd:
            return self.unified_bubble(fd)

    def assert_equality(self, input_filename, expected_bubble):
        """call assertEqual to compare given bubble and bubble generated by
        compressing given graph."""
        tmp = tempfile.NamedTemporaryFile('w', delete=False)
        tmp.close()
        with self.subTest(filename=input_filename):
            cfg = config.Configuration(
                infile=input_filename,
                outfile=tmp.name,
                outformat='bbl',
                loglevel='CRITICAL',
            )
            recipes.powergraph(cfg=cfg)
            expected = self.unified_bubble(expected_bubble)
            found = self.unified_bubble_from_file(tmp.name)
            self.assertEqual(expected, found)


    def test_cases(self):
        for filename, expected in self.test_cases.items():
            self.assert_equality(
                commons.test_case(filename),
                expected.split('\n')
            )


# Expected results of tested cases
RESULT_DDIAMUN = """
NODE\t"d2"
NODE\t"h"
NODE\t"n"
NODE\t"q"
NODE\t"e"
NODE\t"c"
NODE\t"d"
NODE\t"i"
NODE\t"m2"
NODE\t"g"
NODE\t"p"
NODE\t"f1"
NODE\t"b2"
NODE\t"a"
NODE\t"f2"
NODE\t"j"
NODE\t"b1"
NODE\t"m"
NODE\t"o"
NODE\t"l"
IN\t"f2"\tPWRN-"a"-2-1
IN\t"j"\tPWRN-"a"-2-1
IN\t"g"\tPWRN-"a"-2-1
IN\t"f1"\tPWRN-"a"-2-1
IN\tPWRN-"a"-3-1\tPWRN-"a"-2-1
IN\t"m"\tPWRN-"a"-5-1
IN\t"m2"\tPWRN-"a"-5-1
IN\tPWRN-"a"-4-1\tPWRN-"a"-3-2
IN\t"d2"\tPWRN-"a"-1-1
IN\t"d"\tPWRN-"a"-1-1
IN\t"a"\tPWRN-"a"-1-1
IN\t"q"\tPWRN-"a"-1-2
IN\t"e"\tPWRN-"a"-1-2
IN\t"c"\tPWRN-"a"-1-2
IN\t"b2"\tPWRN-"a"-1-2
IN\t"b1"\tPWRN-"a"-1-2
IN\t"o"\tPWRN-"a"-1-2
IN\t"p"\tPWRN-"a"-3-1
IN\t"l"\tPWRN-"a"-3-1
IN\t"h"\tPWRN-"a"-2-2
IN\t"i"\tPWRN-"a"-2-2
IN\tPWRN-"a"-5-1\tPWRN-"a"-4-1
IN\t"n"\tPWRN-"a"-4-1
EDGE\tPWRN-"a"-5-1\t"n"\t1.0
EDGE\tPWRN-"a"-2-1\tPWRN-"a"-2-2\t1.0
EDGE\t"f1"\t"g"\t1.0
EDGE\tPWRN-"a"-1-1\tPWRN-"a"-1-2\t1.0
EDGE\tPWRN-"a"-3-1\tPWRN-"a"-3-2\t1.0
EDGE\tPWRN-"a"-4-1\t"q"\t1.0
EDGE\t"b1"\t"c"\t1.0
"""


RESULT_BLO = """
NODE\t"f"
NODE\t"d"
NODE\t"k"
NODE\t"i"
NODE\t"a"
NODE\t"h"
NODE\t"e"
NODE\t"g"
NODE\t"c"
NODE\t"b"
NODE\t"j"
IN\t"e"\tPWRN-"a"-2-1
IN\tPWRN-"a"-3-1\tPWRN-"a"-2-1
IN\t"a"\tPWRN-"a"-3-1
IN\t"c"\tPWRN-"a"-3-1
IN\t"b"\tPWRN-"a"-3-1
IN\t"d"\tPWRN-"a"-3-1
IN\t"g"\tPWRN-"a"-4-1
IN\t"f"\tPWRN-"a"-4-1
IN\t"h"\tPWRN-"a"-4-1
IN\t"i"\tPWRN-"a"-1-1
IN\t"j"\tPWRN-"a"-1-1
IN\tPWRN-"a"-4-1\tPWRN-"a"-1-1
IN\t"k"\tPWRN-"a"-1-1
EDGE\tPWRN-"a"-2-1\tPWRN-"a"-2-1\t1.0
EDGE\tPWRN-"a"-3-1\t"f"\t1.0
EDGE\tPWRN-"a"-4-1\t"l"\t1.0
EDGE\tPWRN-"a"-1-1\tPWRN-"a"-1-1\t1.0
"""

RESULT_BIP = """
NODE\t"b"
NODE\t"d"
NODE\t"a"
NODE\t"f"
NODE\t"e"
NODE\t"c"
IN\t"e"\tPWRN-"a"-2-1
IN\t"c"\tPWRN-"a"-2-1
IN\t"d"\tPWRN-"a"-2-1
IN\tPWRN-"a"-2-1\tPWRN-"a"-1-2
IN\t"a"\tPWRN-"a"-1-1
IN\t"f"\tPWRN-"a"-1-1
IN\t"b"\tPWRN-"a"-1-1
EDGE\tPWRN-"a"-2-1\tPWRN-"a"-2-1\t1.0
EDGE\tPWRN-"a"-1-1\tPWRN-"a"-1-2\t1.0
"""

RESULT_CLIQUE = """
NODE\t"c"
NODE\t"b"
NODE\t"a"
NODE\t"d"
IN\t"c"\tPWRN-"a"-1-1
IN\t"b"\tPWRN-"a"-1-1
IN\t"a"\tPWRN-"a"-1-1
IN\t"d"\tPWRN-"a"-1-1
EDGE\tPWRN-"a"-1-1\tPWRN-"a"-1-1\t1.0
"""

RESULT_STAR = """
NODE\t"c"
NODE\t"d"
NODE\t"b"
NODE\t"e"
IN\t"c"\tPWRN-"a"-1-2
IN\t"d"\tPWRN-"a"-1-2
IN\t"b"\tPWRN-"a"-1-2
IN\t"e"\tPWRN-"a"-1-2
EDGE\tPWRN-"a"-1-2\t"a"\t1.0
"""

RESULT_CC = """
EDGE\t"23"\t"42"\t1.0
NODE\t"2"
NODE\t"5"
NODE\t"3"
NODE\t"4"
NODE\t"6"
NODE\t"1"
IN\t"1"\tPWRN-"1"-1-1
IN\t"6"\tPWRN-"1"-1-1
IN\t"4"\tPWRN-"1"-1-2
IN\t"2"\tPWRN-"1"-1-2
IN\t"5"\tPWRN-"1"-1-2
IN\t"3"\tPWRN-"1"-1-2
EDGE\tPWRN-"1"-1-1\tPWRN-"1"-1-2\t1.0
NODE\t"b"
NODE\t"c"
NODE\t"d"
NODE\t"e"
IN\t"b"\tPWRN-"a"-1-2
IN\t"c"\tPWRN-"a"-1-2
IN\t"d"\tPWRN-"a"-1-2
IN\t"e"\tPWRN-"a"-1-2
EDGE\tPWRN-"a"-1-2\t"a"\t1.0
"""

RESULT_PFC = """
NODE\t"j"
NODE\t"l"
NODE\t"b"
NODE\t"g"
NODE\t"h"
NODE\t"a"
NODE\t"d"
NODE\t"c"
NODE\t"e"
NODE\t"f"
NODE\t"i"
IN\tPWRN-"a"-2-1\tPWRN-"a"-1-2
IN\t"h"\tPWRN-"a"-1-2
IN\t"i"\tPWRN-"a"-1-2
IN\t"b"\tPWRN-"a"-1-1
IN\tPWRN-"a"-3-1\tPWRN-"a"-1-1
IN\t"a"\tPWRN-"a"-1-1
IN\t"j"\tPWRN-"a"-3-2
IN\t"l"\tPWRN-"a"-3-2
IN\t"d"\tPWRN-"a"-3-1
IN\t"c"\tPWRN-"a"-3-1
IN\t"e"\tPWRN-"a"-2-1
IN\t"g"\tPWRN-"a"-2-1
IN\t"f"\tPWRN-"a"-2-1
IN\tPWRN-"a"-3-2\tPWRN-"a"-2-2
EDGE\tPWRN-"a"-3-1\tPWRN-"a"-3-2\t1.0
EDGE\tPWRN-"a"-2-1\tPWRN-"a"-2-2\t1.0
EDGE\tPWRN-"a"-1-1\tPWRN-"a"-1-2\t1.0
"""

RESULT_ECOLI = """
NODE\t"R_VALabc"
NODE\t"R_DHAD1"
NODE\t"R_VALt2r"
IN\t"R_VALabc"\tPWRN-"R_DHAD1"-1-1
IN\t"R_DHAD1"\tPWRN-"R_DHAD1"-1-1
IN\t"R_VALt2r"\tPWRN-"R_DHAD1"-1-1
EDGE\tPWRN-"R_DHAD1"-1-1\tPWRN-"R_DHAD1"-1-1\t1.0
NODE\t"RXN-14213"
NODE\t"RXN-14200"
NODE\t"R_DTMPK"
IN\t"RXN-14213"\tPWRN-"RXN-14200"-1-1
IN\t"RXN-14200"\tPWRN-"RXN-14200"-1-1
IN\t"R_DTMPK"\tPWRN-"RXN-14200"-1-1
EDGE\tPWRN-"RXN-14200"-1-1\tPWRN-"RXN-14200"-1-1\t1.0
NODE\t"R_EX_26dap_M_LPAREN_e_RPAREN_"
NODE\t"RXN-14246"
NODE\t"R_DAPE"
IN\t"R_EX_26dap_M_LPAREN_e_RPAREN_"\tPWRN-"RXN-14246"-1-1
IN\t"RXN-14246"\tPWRN-"RXN-14246"-1-1
IN\t"R_DAPE"\tPWRN-"RXN-14246"-1-1
EDGE\tPWRN-"RXN-14246"-1-1\tPWRN-"RXN-14246"-1-1\t1.0
EDGE\t"NADH-KINASE-RXN"\t"R_NADK"\t1.0
NODE\t"R_G1PACT"
NODE\t"GLUCOSAMINEPNACETYLTRANS-RXN"
NODE\t"R_PGAMT"
NODE\t"PHOSACETYLGLUCOSAMINEMUT-RXN"
NODE\t"R_AMANAPE"
NODE\t"R_EX_acgam_LPAREN_e_RPAREN_"
IN\tPWRN-"GLUCOSAMINEPNACETYLTRANS-RXN"-2-1\tPWRN-"GLUCOSAMINEPNACETYLTRANS-RXN"-1-1
IN\t"PHOSACETYLGLUCOSAMINEMUT-RXN"\tPWRN-"GLUCOSAMINEPNACETYLTRANS-RXN"-1-1
IN\t"GLUCOSAMINEPNACETYLTRANS-RXN"\tPWRN-"GLUCOSAMINEPNACETYLTRANS-RXN"-2-1
IN\t"R_AMANAPE"\tPWRN-"GLUCOSAMINEPNACETYLTRANS-RXN"-2-1
IN\t"R_EX_acgam_LPAREN_e_RPAREN_"\tPWRN-"GLUCOSAMINEPNACETYLTRANS-RXN"-2-1
IN\t"R_G1PACT"\tPWRN-"GLUCOSAMINEPNACETYLTRANS-RXN"-1-2
IN\t"R_PGAMT"\tPWRN-"GLUCOSAMINEPNACETYLTRANS-RXN"-1-2
EDGE\tPWRN-"GLUCOSAMINEPNACETYLTRANS-RXN"-1-1\tPWRN-"GLUCOSAMINEPNACETYLTRANS-RXN"-1-2\t1.0
EDGE\tPWRN-"GLUCOSAMINEPNACETYLTRANS-RXN"-2-1\tPWRN-"GLUCOSAMINEPNACETYLTRANS-RXN"-2-1\t1.0
NODE\t"R_GLGC"
NODE\t"RXN-10770"
NODE\t"GLYMALTOPHOSPHORYL-RXN"
IN\t"R_GLGC"\tPWRN-"GLYMALTOPHOSPHORYL-RXN"-1-1
IN\t"RXN-10770"\tPWRN-"GLYMALTOPHOSPHORYL-RXN"-1-1
IN\t"GLYMALTOPHOSPHORYL-RXN"\tPWRN-"GLYMALTOPHOSPHORYL-RXN"-1-1
EDGE\tPWRN-"GLYMALTOPHOSPHORYL-RXN"-1-1\tPWRN-"GLYMALTOPHOSPHORYL-RXN"-1-1\t1.0
"""

RESULT_TESTGML = """
NODE\t"g"
NODE\t"b"
NODE\t"m"
NODE\t"s"
NODE\t"d"
NODE\t"v"
NODE\t"w"
NODE\t"f"
NODE\t"c"
IN\t"d"\tPWRN-"b"-1-1
IN\t"w"\tPWRN-"b"-1-1
IN\t"c"\tPWRN-"b"-1-1
IN\t"s"\tPWRN-"b"-1-1
IN\t"b"\tPWRN-"b"-1-1
IN\t"f"\tPWRN-"b"-2-2
IN\tPWRN-"b"-3-2\tPWRN-"b"-2-2
IN\t"g"\tPWRN-"b"-2-2
IN\t"m"\tPWRN-"b"-3-2
IN\t"v"\tPWRN-"b"-3-2
EDGE\tPWRN-"b"-3-2\t"l"\t1.0
EDGE\t"l"\t"p"\t1.0
EDGE\tPWRN-"b"-1-1\tPWRN-"b"-1-1\t1.0
EDGE\t"m"\t"v"\t1.0
EDGE\t"c"\t"f"\t1.0
EDGE\tPWRN-"b"-2-2\t"b"\t1.0
"""

RESULT_GRAPHML = """
NODE\t"2"
NODE\t"3"
NODE\t"1"
NODE\t"4"
IN\t"1"\tPWRN-"1"-1-1
IN\t"4"\tPWRN-"1"-1-1
IN\t"3"\tPWRN-"1"-1-2
IN\t"2"\tPWRN-"1"-1-2
EDGE\tPWRN-"1"-1-1\tPWRN-"1"-1-2\t1.0
"""

RESULT_ONEDGE = """
EDGE\t"a"\t"b"\t1.0
"""

RESULT_TESTGML = """
NODE\t"c"
NODE\t"w"
NODE\t"f"
NODE\t"v"
NODE\t"s"
NODE\t"b"
NODE\t"d"
NODE\t"g"
NODE\t"m"
IN\t"c"\tPWRN-"b"-1-1
IN\t"b"\tPWRN-"b"-1-1
IN\t"w"\tPWRN-"b"-1-1
IN\t"d"\tPWRN-"b"-1-1
IN\t"s"\tPWRN-"b"-1-1
IN\t"g"\tPWRN-"b"-2-2
IN\t"f"\tPWRN-"b"-2-2
IN\tPWRN-"b"-3-2\tPWRN-"b"-2-2
IN\t"v"\tPWRN-"b"-3-2
IN\t"m"\tPWRN-"b"-3-2
EDGE\tPWRN-"b"-2-2\t"b"\t1.0
EDGE\t"c"\t"f"\t1.0
EDGE\tPWRN-"b"-1-1\tPWRN-"b"-1-1\t1.0
EDGE\t"m"\t"v"\t1.0
EDGE\t"l"\t"p"\t1.0
EDGE\tPWRN-"b"-3-2\t"l"\t1.0
"""
