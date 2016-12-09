"""
Definitions of model_from(5) that encapsulate
 the ASP grounder and solver calls.

The system of ASPConfig allows to define different
configs for different tasks.

"""
import os
import itertools
from functools   import partial
from collections import deque, Counter

from powergrasp import commons
from powergrasp import atoms
from pyasp import asp


LOGGER = commons.logger()


# shortcuts for solvers options
SOLVER_HEURISTICS = ('Berkmin', 'Vmtf', 'Vsids', 'Unit', 'None', 'Domain')
SOLVER_CONFIGURATIONS = ('frumpy', 'jumpy', 'tweety', 'trendy', 'crafty', 'handy')
SOLVER_STRATEGIES = ('bb,1', 'bb,2', 'bb,3', 'usc,1', 'usc,2', 'usc,3')
SOLVER_FLAGS = ('', '--restart-on-model')

SOLVER_CLI_TEMPLATE = ' --heuristic={} --configuration={} --opt-strategy={} {} -n 0'
ASP_DEFAULT_CLASP_OPTION = ' --heuristic=Vsids --configuration=frumpy '
ASP_FILES_MOTIF_SEARCH = [commons.ASP_SRC_PREPRO, commons.ASP_SRC_POSTPRO]


class ASPConfig:
    """Context for solvers, used by solving module"""
    def __init__(self, files:list, clasp_options:str='', gringo_options:str=''):
        self.files = list(files or [])
        self.clasp_options = clasp_options
        self.gringo_options = gringo_options

    @staticmethod
    def gen_configs(heuristics=SOLVER_HEURISTICS, configs=SOLVER_CONFIGURATIONS,
                    strategies=SOLVER_STRATEGIES, flags=SOLVER_FLAGS) -> iter:
        """Yield all possible solver configurations as 4-uplets
        (heuristic, config, strategies, other flags)

        Example: Berkmin, handy, usc 2, --restart-on-model

        """
        yield from itertools.product(heuristics, configs, strategies, flags)

    @staticmethod
    def gen_extract_configs():
        """Yield all possible ASPConfig objects for extraction"""
        for heur, conf, strat, flag in gen_configs():
            yield ASPConfig([commons.ASP_SRC_EXTRACT],
                            SOLVER_CLI_TEMPLATE.format(heur, conf, strat, flag))


SOLVER_NB_CONFIG = len(tuple(ASPConfig.gen_configs()))

# default configs
CONFIG_DEFAULT = lambda: ASPConfig(None)
DEFAULT_CONFIG_EXTRACTION = lambda: ASPConfig(
    [commons.ASP_SRC_EXTRACT],
    ' --heuristic=Vsids --configuration=frumpy -n 0',
)
DEFAULT_CONFIG_BICLIQUE = lambda: ASPConfig(
    [commons.ASP_SRC_PREPRO, commons.ASP_SRC_POSTPRO, commons.ASP_SRC_FINDBC],
    ASP_DEFAULT_CLASP_OPTION,
)
DEFAULT_CONFIG_CLIQUE = lambda: ASPConfig(
    [commons.ASP_SRC_PREPRO, commons.ASP_SRC_POSTPRO, commons.ASP_SRC_FINDCC],
    ASP_DEFAULT_CLASP_OPTION,
)
DEFAULT_CONFIG_INCLUSION = lambda: ASPConfig(
    [commons.ASP_SRC_INCLUSION],
)


def all_models_from(base_atoms, aspfiles=None, aspargs=None,
                    aspconfig=None, parsed=True):
    """Compute all models from ASP source code in aspfiles, with aspargs
    given as grounding arguments and base_atoms given as input atoms.

    base_atoms -- string, ASP-readable atoms
    aspfiles -- (list of) supplementary filenames, contains the ASP source code
    aspargs -- dict of constant:value that will be set as constants in aspfiles
    aspconfig -- an ASPConfig object giving more files and solvers options
    parsed -- set to True for get already parsed atoms of model, False for str
    yield -- Atoms instance, containing atoms produced by solving

    """
    aspfiles = aspfiles or []
    aspargs = aspargs or {}
    aspconfig = aspconfig or CONFIG_DEFAULT()
    # use list of aspfiles in all cases
    assert aspfiles.__class__ in (tuple, list, str)
    assert isinstance(aspconfig, ASPConfig)
    if isinstance(aspfiles, str):
        aspfiles = [aspfiles]
    elif isinstance(aspfiles, tuple):  # solver take only list, not tuples
        aspfiles = list(aspfiles)
    aspfiles.extend(aspconfig.files or [])
    assert aspfiles.__class__ is list
    assert len(set(aspfiles)) == len(aspfiles), "Given list of aspfiles contains doublons: " + str(aspfiles)

    # define the command line options for gringo and clasp
    constants = ' -c '.join(str(k)+'='+str(v) for k,v in aspargs.items())
    if len(aspargs) > 0:  # must begin by a -c for announce the first constant
        constants = '-c ' + constants
    gringo_options = constants + ' ' + aspconfig.gringo_options
    # print('OPTIONS:', gringo_options)
    # print('OPTIONS:', aspconfig.clasp_options)
    # print('OPTIONS:', aspconfig)

    #  create solver and ground base and program in a single ground call.
    solver = asp.Gringo4Clasp(gringo_options=gringo_options,
                              clasp_options=aspconfig.clasp_options)
    # print('FILES:', aspfiles)
    # print('ATOMS:', str(base_atoms))
    answers = solver.run(aspfiles, additionalProgramText=base_atoms,
                         collapseAtoms=not parsed)
    # if len(answers) > 0:
        # for idx, answer in enumerate(answers):
            # print('ANSWER ' + str(idx) + ':', answer)
        # print('ALL ANSWERS GAVE')
    # else:
        # print('NO MODEL FOUND !')
    yield from (atoms.AtomsModel.from_pyasp_termset(answer) for answer in answers)


def model_from(base_atoms, aspfiles=None, aspargs=None, aspconfig=None,
               parsed=True):
    """Compute the last model from ASP source code in aspfiles, with aspargs
    given as grounding arguments and base_atoms given as input atoms.

    base_atoms -- string, ASP-readable atoms
    aspfiles -- (list of) filename, contains the ASP source code
    aspargs -- dict of constant:value that will be set as constants in aspfiles
    aspconfig -- an ASPConfig object giving more files and solvers options
    parsed -- set to True for get already parsed atoms of model, False for str
    return -- an Atoms instance containing atoms of the last produced model

    """
    answers = all_models_from(base_atoms=base_atoms, aspfiles=aspfiles,
                              aspargs=aspargs, aspconfig=aspconfig,
                              parsed=parsed)
    try:
        return deque(answers, maxlen=1)[0]
    except IndexError:  # no valid model
        return None
