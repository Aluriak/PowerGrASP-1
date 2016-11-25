"""
Test on graph compression, using statistical results.

"""
import unittest
import tempfile
import inspect
from functools import partial

import powergrasp
from powergrasp import config
from powergrasp import recipes
from powergrasp import commons
from powergrasp import observers
from powergrasp.statistics import (INIT_EDGE, FINL_EDGE, GENR_PWED, GENR_PWND,
                                   CONV_RATE, EDGE_RDCT, COMP_RTIO, DataExtractor)


STATS_FIELDS = (INIT_EDGE, FINL_EDGE, GENR_PWED, GENR_PWND,
                CONV_RATE, EDGE_RDCT, COMP_RTIO)
STATS_ROUND = partial(round, ndigits=2)


def compression_results(init_edge, finl_edge, genr_pwed, genr_pwnd,
                        conv_rate, edge_rdct, comp_rtio):
    """Return a dict {statistic key: value} where statistics keys are the seven
    constants imported from powergrasp.statistics module, and where the value
    are those given as parameters.
    """
    _, _, _, args = inspect.getargvalues(inspect.currentframe())
    return {
        globals()[name.upper()]: value
        for name, value in args.items()
    }


# Expected results of tested cases
RESULT_DDIAM = compression_results(
    31, 3, 4, 7, 3.4285714285714284, 77.41935483870968, 4.428571428571429,
)
RESULT_CC = compression_results(
    13, 1, 2, 3, 3.3333333333333335, 76.92307692307693, 4.333333333333333,
)
RESULT_CCOLI = compression_results(
    24, 1, 6, 7, 2.4285714285714284, 70.83333333333334, 3.4285714285714284
)
RESULT_EMPTY = compression_results(
    0, 0, 0, 0, 1.0, 100, 1.0,
)


class TestStatisticalCompression(unittest.TestCase):
    """This class yields many subtests about compression results.

    The test case and associated results are defined in setUp() method.
    Tests are robust to ambiguous compression, as long as paths all leads
    to same results.

    These tests operate only on statistical data, thus can't detect problems
    of compression that don't touch the analysed data.

    Tested parameters are:
        Number of model, connected component, biclique,
            clique, poweredge, powernode and initial/remaining edge.
        Conversion rate, edge reduction and compression ratio.


    """

    def setUp(self):
        self.test_cases = {
            'double_biclique.lp' : RESULT_DDIAM,
            'concomp.lp'         : RESULT_CC,
            'empty.lp'           : RESULT_EMPTY,
            'ecoli_2896-53.gml'  : RESULT_CCOLI,
        }

    def filtered_extracted_stats(self, stats):
        return {
            field: stats.get(field, None) for field in STATS_FIELDS
        }

    def assert_equality(self, input_filename, expected_stats):
        """call assertEqual to compare given bubble and bubble generated by
        compressing given graph."""
        statistics = DataExtractor(network_name=input_filename)
        tmp = tempfile.NamedTemporaryFile('w')

        with self.subTest(filename=input_filename):
            cfg = config.Configuration(
                infile=input_filename,
                outfile=tmp.name,
                outformat='bbl',
                loglevel='CRITICAL',
                additional_observers=[statistics],
            )
            recipes.powergraph(cfg=cfg)
            found_stats = self.filtered_extracted_stats(statistics)
            results = ((field, found_stats[field], expected_stats[field])
                       for field in STATS_FIELDS)
            for field, found, expected in results:
                if isinstance(expected, float):
                    expected = STATS_ROUND(expected)
                if isinstance(found, float):
                    found = STATS_ROUND(found)
                with self.subTest(filename=input_filename, field=field):
                    self.assertAlmostEqual(
                        found,
                        expected,
                    )

        tmp.close()

    def test_cases(self):
        for filename, expected in self.test_cases.items():
            self.assert_equality(
                commons.test_case(filename),
                expected
            )


