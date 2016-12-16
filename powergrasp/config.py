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
    'oriented'      : False,  # True for oriented output graph
    'plot_stats'    : False,
    'plot_file'     : False,
    'profiling'     : False,  # profiling of input data
    'thread'        : 1,  # how many thread to use
    'draw_lattice'  : None,
    'save_time'     : False,
    'motifs'        : (motif.Clique.for_powergraph(), motif.Biclique.for_powergraph()),  # iterable of motifs to use to compress
    'extract_config': solving.ASPConfig.extraction(),
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

    def __init__(self, default=FIELDS, **kwargs):
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        # payload is the aggregation of default values,
        #  given default (dict or Configuration object) and given kwargs,
        #  in decreasing order of priority.
        payload = dict(ChainMap(kwargs, dict(default), BASE_FIELDS))
        self._validate_init_args(payload)
        for field, value in payload.items():
            setattr(self, '__' + field, value)
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
                "extraction",
                self.__extract_config.files,
                self.__extract_config.clasp_options + thread_option,
                self.__extract_config.gringo_options
            )
            self.__clique_config = solving.ASPConfig(
                "clique",
                self.__clique_config.files,
                self.__clique_config.clasp_options + thread_option,
                self.__clique_config.gringo_options
            )
            self.__biclique_config = solving.ASPConfig(
                "biclique",
                self.__biclique_config.files,
                self.__biclique_config.clasp_options + thread_option,
                self.__biclique_config.gringo_options
            )

        # get data from parameters
        # read http://stackoverflow.com/a/40495529/3077939 to see
        # why the setattr form is used.
        setattr(self, '__network_name', commons.network_name(self.infile))
        setattr(self, '__graph_file', (None if not self.infile
                                       else converter.to_asp_file(self.infile)))

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

        # verifications about directed graphs
        have_oriented_extraction = self.extract_config.files == [commons.ASP_SRC_OREXTRACT]
        have_oriented_motif = any(isinstance(m, motif.OrientedBiclique)
                                  for m in self.motifs)
        have_non_oriented_motif = any(not isinstance(m, motif.OrientedBiclique)
                                      for m in self.motifs)
        if have_oriented_motif and have_non_oriented_motif:
            LOGGER.warning("Graph declared both oriented and non oriented"
                           " motifs. This is very probably an error.")
        if self.oriented and not have_oriented_motif:
            LOGGER.warning("Graph is said oriented but declared non-oriented"
                           " motifs. This is very probably an error.")
        if have_oriented_motif and not self.oriented:
            LOGGER.warning("Graph declared non-oriented motifs but it is"
                           " said oriented. This is very probably an error.")
        if have_oriented_extraction and not have_oriented_motif:
            LOGGER.warning("Graph declared oriented motifs but extraction"
                           " is not oriented. This is very probably an error.")
        if not have_oriented_extraction and have_oriented_motif:
            LOGGER.warning("Graph declared non-oriented motifs but extraction"
                           " is oriented. This is very probably an error.")


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


    @staticmethod
    def fields_for_high_priority_first(**kwargs) -> dict:
        """Return a minimal dict of fields and values allowing
        to treat graphs with a prioritization of some nodes.

        kwargs -- supplementary fields to provide. Will override default data.

        """
        MOTIFS = [motif.Biclique(include_max_node_degrees=True,
                                 additional_files=[commons.ASP_SRC_PRIORITY])]
        fields = {
            'motifs': tuple(MOTIFS),
        }
        for field in fields:
            if field in kwargs:
                LOGGER.warning("The recipe Configuration.fields_for_prioritized"
                               "_degree is designed to define the field {}, but"
                               " given parameter overrides it with value {}."
                               " This unexpected value will be used, but"
                               " chances are this is an error."
                               "".format(field, kwargs[field]))
        fields.update(kwargs)
        return fields


    @staticmethod
    def fields_for_oriented_graph(**kwargs) -> dict:
        """Return a minimal dict of fields and values allowing
        to treat oriented graphs.

        kwargs -- supplementary fields to provide. Will override default data.

        """
        fields = {
            'oriented': True,
            'motifs': (motif.OrientedBiclique.for_powergraph(),),
            'extract_config': solving.ASPConfig.oriented_extraction(),
        }
        for field in fields:
            if field in kwargs:
                LOGGER.warning("The recipe Configuration.for_oriented_graph is"
                               " designed to define the field {}, but given"
                               " parameter overrides it with value {}."
                               " This unexpected value will be used, but"
                               " chances are this is an error."
                               "".format(field, kwargs[field]))
        fields.update(kwargs)
        return fields
