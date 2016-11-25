"""Definition of THE configuration object, specifying all particular values
for a compression.


"""


import sys
import tempfile

from powergrasp import cli
from powergrasp import solving
from powergrasp import commons
from powergrasp import converter


LOGGER = commons.logger()


# configuration fields mapped with default value or None
FIELDS = dict(commons.DEFAULT_PROGRAM_OPTIONS)
FIELDS.update({
    'biclique_config': solving.DEFAULT_CONFIG_BICLIQUE(),
    'clique_config': solving.DEFAULT_CONFIG_CLIQUE(),
    'extract_config': solving.DEFAULT_CONFIG_EXTRACTION(),
    # 'do_profiling': False,

    # infered data
    'network_name': 'unknow',
    'graph_file': None,
})


def meta_config(name, bases, attrs):
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
        for field in FIELDS:
            value = kwargs.get(field)
            setattr(self, '__' + field,
                    FIELDS.get(field) if value is None else value)
        self.populate()
        self.validate()


    def populate(self):
        """Compute fields based on existing ones. Modify some existing fields."""
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


    def validate(self):
        """Logs any inconsistancies in the configuration"""

        if self.infile is None:
            with tempfile.NamedTemporaryFile('w', delete=False) as tmp:
                LOGGER.info("No input data found. Standard input will be read"
                            " and saved in {}.".format(tmp.name))
                print(tmp, type(tmp))
                [tmp.write(line + '\n') for line in sys.stdin]
                self.__infile = tmp.name

        if self.outfile is None:
            LOGGER.info('No output file to write. Standard output will be used.')

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
        params = cli.parse(parameters=parameters, args=args)
        cfg = Configuration(**params)
        cfg.cli_params = params  # TODO: document it, or delete it
        return cfg
