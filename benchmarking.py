"""
Perform some benchmarks on various parameters.

"""
from timeit import timeit
from functools import partial

from powergrasp import solving


def extract_config(graph_lp):
    """Yield time necessary for perform an extraction with different
    clasp configurations"""

    results = {}
    try:
        for aspconfig in solving.gen_extract_configs():
            def func():
                tuple(solving.all_models_from('', aspfiles=[graph_lp],
                                              aspconfig=aspconfig))
            result = timeit(func, number=3)
            yield aspconfig.clasp_options + ': ' + str(result)
            results[aspconfig.clasp_options] = result
    except KeyboardInterrupt:
        pass
    minimal = min(results, key=lambda k: results[k])
    yield '\nMinimal score:' + str(results[minimal]) + '\n\t' + minimal


if __name__ == "__main__":
    GRAPH = './powergrasp/tests/structural_binding.lp'
    GRAPH = './powergrasp/tests/big_biclique.lp'
    [print(line) for line in extract_config(GRAPH)]
