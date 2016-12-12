"""Definition of THE configuration object, specifying all particular values
for a compression.


"""


import os
import sys
import tempfile
from collections import ChainMap

from powergrasp import cli
from powergrasp import motif
from powergrasp import solving
from powergrasp import commons
from powergrasp import converter


LOGGER = commons.logger()


# Definition of the configuration fields and their default values
BASE_FIELDS = {  # field: default value
    'infile'        : None,
    'outfile'       : None,
    'outformat'     : None,
    'interactive'   : False,
    'count_model'   : False,
    'count_cc'      : False,
    'timers'        : False,
    'loglevel'      : commons.DEFAULT_LOG_LEVEL,
    'logfile'       : commons.DEFAULT_LOG_FILE,
    'stats_file'    : None,
    'plot_stats'    : False,
    'plot_file'     : False,
    'profiling'     : False,  # profiling of input data
    'thread'        : 1,  # how many thread to use
    'draw_lattice'  : None,
    'save_time'     : False,
    'motifs'        : (motif.Clique.for_powergraph(), motif.Biclique.for_powergraph()),  # iterable of motifs to use to compress
    'extract_config': solving.DEFAULT_CONFIG_EXTRACTION(),
    'signal_profile': False,  # print debug information on received signals
    'additional_observers': None,  # iterable of observers to add
}
INFERRED_FIELDS = {
    'network_name': None,  # name used to refer to the input network
    'graph_file': None,
    'asp_configs': None,  # iterable of asp configs (motifs + others)
}
# all available fields and default options
FIELDS = ChainMap({}, INFERRED_FIELDS, BASE_FIELDS)
DEFAULT_OPTIONS = dict(BASE_FIELDS)


def meta_config(name, bases, attrs):
    """Mapping allowing Configuration class to automatically holds properties,
    according to the content of FIELDS.

    """
    attrs = dict(attrs)

    def prop(field):
        def wrapped(self):
            """Access to {} value""".format(field)
            return getattr(self, '__' + field)
        return property(wrapped)

    for field in FIELDS:
        attrs[field] = prop(field)

    return type(name, bases, attrs)


class Configuration(metaclass=meta_config):
    """Read-only object allowing whole program to access global constants.

    The Configuration can be inferred from parameters (CLI for instance).
    See `Configuration.from_cli(2)`.

    Description of some fields:

    infile -- input file given by user
    graph_file -- file containing the graph, ASP formated. Can be infile.
    outfile -- the output file to be written.

    """

    def __init__(self, **kwargs):
        self._validate_init_args(kwargs)
        assert all(kwarg in BASE_FIELDS for kwarg in kwargs)
        for field in BASE_FIELDS:
            value = kwargs.get(field)
            setattr(self, '__' + field,
                    FIELDS.get(field) if value is None else value)
        self.populate()
        self.validate()


    @property
    def fields(self):
        for field in FIELDS:
            yield getattr(self, field)

    def __iter__(self) -> ('field', 'value'):
        for field in FIELDS:
            yield field, getattr(self, field)


    def populate(self):
        """Compute fields based on existing ones. Modify some existing fields
        in order to provide default values.

        """
        # add threading to ASP configs
        thread_option = commons.thread(self.thread)
        if thread_option:
            self.__extract_config = solving.ASPConfig(
                self.__extract_config.files,
                self.__extract_config.clasp_options + thread_option,
                self.__extract_config.gringo_options
            )
            self.__clique_config = solving.ASPConfig(
                self.__clique_config.files,
                self.__clique_config.clasp_options + thread_option,
                self.__clique_config.gringo_options
            )
            self.__biclique_config = solving.ASPConfig(
                self.__biclique_config.files,
                self.__biclique_config.clasp_options + thread_option,
                self.__biclique_config.gringo_options
            )

        # get data from parameters
        # read http://stackoverflow.com/a/40495529/3077939 to see
        # why the setattr form is used.
        setattr(self, '__network_name', commons.network_name(self.infile))
        setattr(self, '__graph_file', converter.to_asp_file(self.infile))

        setattr(self, '__additional_observers',
                list(getattr(self, '__additional_observers') or []))

        setattr(self, '__asp_configs',
                list(self.motifs) + [self.extract_config])

        # logging
        commons.configure_logger(log_filename=self.logfile,
                                 term_loglevel=self.loglevel)


    def validate(self):
        """Logs any inconsistancies in the configuration, and try to fix them."""

        if self.infile is None:
            with tempfile.NamedTemporaryFile('w', delete=False) as tmp:
                LOGGER.info("No input data found. Standard input will be read"
                            " and saved in {}.".format(tmp.name))
                [tmp.write(line + '\n') for line in sys.stdin]
                self.__infile = tmp.name

        if self.outfile is None:
            LOGGER.info('No output file to write. Standard output will be used.')
        elif os.path.isdir(self.outfile):
            LOGGER.info("Given output file is not a file, but a directory ({})."
                        " Output file will be placed in it, with the name"
                        " {}.{}.".format(self.outfile, self.network_name, self.outformat))
            self.outfile = os.path.join(
                self.outfile,
                self.network_name + '.' + self.outformat
            )

        if not isinstance(self.thread, int) or self.thread < 1:
            LOGGER.error('Thread value is not valid (equal to {}). 1 will be used.'.format(self.thread))
            self.__thread = 1


    def _validate_init_args(self, kwargs):
        """Verify data sent to __init__, raise ValueError if any problem"""
        for arg in kwargs:
            if arg not in FIELDS:
                raise ValueError("Configuration receive argument <{}>,"
                                 " which is not in the expected ones:"
                                 " {}".format(arg, ', '.join(FIELDS)))


    def __str__(self):
        return "<Configuration for {} network. Non-False fields: {}>".format(
            self.network_name,
            ', '.join(field for field in FIELDS if getattr(self, field))
        )


    @staticmethod
    def from_cli(parameters={}, args=sys.argv[1:]):
        """Return a new Configuration based on CLI arguments
        and given parameters.

        """
        params = cli.parse(parameters=parameters, args=args,
                           default_options=DEFAULT_OPTIONS)
        cfg = Configuration(**params)
        return cfg
