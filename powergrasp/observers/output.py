"""
Definition of various output-related compression observers.

"""
import sys
import tempfile
import statistics
from functools import partial

from .observer  import CompressionObserver, Signals, Priorities
from powergrasp import commons
from powergrasp import converter
from powergrasp import utils


LOGGER = commons.logger()


class InteractiveCompression(CompressionObserver):
    """Make the compression interactive: ask for an input from user
    at the end of each step"""
    def _update(self, signals):
        if Signals.StepStopped in signals:
            try:
                input('<hit enter for next model computation>')
            except KeyboardInterrupt:
                exit()

    @property
    def priority(self):
        return Priorities.Minimal


class LatticeDrawer(CompressionObserver):
    """Draw a lattice of all connected component"""

    def __init__(self, directory=commons.PACKAGE_DIR_DATA,
                 prefix='lattice_'):
        self.basename = directory + prefix + '{}'

    def _update(self, signals):
        if Signals.ConnectedComponentStarted in signals:
            _, cc, atoms = signals[Signals.ConnectedComponentStarted]
            graphdict = utils.asp2graph(atoms)
            filename = self.basename.format(cc)
            # print('DEBUG:', filename, atoms, graphdict)
            utils.draw_lattice(graphdict, filename)
            LOGGER.info('Line diagram of CC ' + str(cc)
                        + ' saved in ' + filename)


class OutputWriter(CompressionObserver):
    """Manage the output bubble file, and assure its conversion
    into expected output format

    """

    def __init__(self, outfile:str=None, outformat:str=None):
        self.format = OutputWriter.format_deduced_from(outfile, outformat)
        self.output = str(outfile or '')
        self.write_to_stdout = not bool(self.output)


    def _update(self, signals):
        # print('Output Writer:', signals)
        if Signals.ModelFound in signals:
            SIGNAL_MODEL_ATOMS = {'powernode', 'clique', 'poweredge'}
            motif = signals[Signals.ModelFound]
            # give new powernodes, clique and poweredges to converter
            model_atoms = motif.model.get_str(SIGNAL_MODEL_ATOMS)
            self.write(str(model_atoms))

        if Signals.ConnectedComponentStarted in signals:
            cc_num, cc_name, _ = signals[Signals.ConnectedComponentStarted]
            self.comment('CONNECTED COMPONENT {}: {}'.format(cc_num, cc_name))

        if Signals.ConnectedComponentStopped in signals:
            remain_edges = signals[Signals.ConnectedComponentStopped]
            self.write(str(remain_edges))
            self.finalize_cc()

        if Signals.CompressionStarted in signals:
            self.init_writer()

        if Signals.CompressionStopped in signals:
            self.finalized()


    def init_writer(self):
        """Open the output file, initialize the writer, write the header"""
        if self.write_to_bubble:  # write directly to output file
            self.fd = sys.stdout if self.write_to_stdout else open(self.output, 'w')
        else:  # user wants a conversion to another format
            # write bubble in tempfile, then convert it to outfile
            self.fd = tempfile.NamedTemporaryFile('w', delete=False)

        self.writer = converter.BubbleWriter(self.fd)
        self.writer.write_header()


    def finalize_cc(self):
        self.writer.finalize_cc()
        LOGGER.debug("Connected component data wrote in file " + self.fd.name)


    def finalized(self):
        """Write last informations in output file, then convert
        it to expected output format

        """
        if not self.write_to_stdout:
            self.fd.close()
        # conversion to real output
        if not self.write_to_bubble:
            assert self.fd.name != self.output
            print('CYVSBE:', self.fd.name)
            converter.bbl_to_output(self.fd.name, self.output, self.format)

    def write(self, lines):
        """Add given lines to output"""
        self.writer.write_atoms(lines)

    def comment(self, lines):
        """Add given lines to output as comments"""
        self.writer.write_comment(lines)


    @property
    def priority(self):
        return Priorities.Minimal

    @property
    def write_to_bubble(self):
        """True iff output format is bubble"""
        return self.format == 'bbl'


    @staticmethod
    def format_deduced_from(output_file, output_format):
        """Return the most likely expected output format by looking at given args"""
        # look at the output_file extension if output_format is unusable
        if not output_format or output_format not in converter.OUTPUT_FORMATS:
            try:
                output_format = output_file.split('.')[-1]  # extension of the file
            except (IndexError, AttributeError):
                output_format = converter.DEFAULT_OUTPUT_FORMAT  # use BBL
        # verifications
        if output_format not in converter.OUTPUT_FORMATS:
            output_format = converter.DEFAULT_OUTPUT_FORMAT
        return output_format


class TimeComparator(CompressionObserver):
    """Maintain a list of whole compression time, compare with the
    current compression results."""
    ROUNDING_DIGIT = 3

    def __init__(self, network_name, time_counter=None,
                 rounding_order=ROUNDING_DIGIT, *, save_result=True):
        self.time_counter = time_counter
        self.rounder = partial(round, ndigits=rounding_order)
        self.save_result = save_result
        self.filename = commons.access_packaged_file(
            commons.DIR_DATA + 'compression_time_{}.txt'.format(network_name)
        )
        try:
            with open(self.filename, 'a') as fd:
                pass  # create it if necessary
            with open(self.filename) as fd:
                self.time_mean = statistics.mean(float(line) for line in fd)
        except statistics.StatisticsError:
            self.time_mean = None

    def save_time(self, new_time):
        if self.save_result:
            with open(self.filename, 'a') as fd:
                fd.write(str(new_time) + '\n')
        else:
            pass

    def _update(self, signals):
        if Signals.CompressionStopped in signals:
            if self.time_counter is None:
                return
            time = self.time_counter.compression_time
            self.save_time(time)
            self.show(time)

    def show(self, time):
        if self.time_mean is None:
            mean_diff = float(time)
        else:
            mean_diff = self.rounder(float(time) - float(self.time_mean))
        diff_msg = ('+' if mean_diff > 0 else '')
        LOGGER.info('Time Comparator: ' + str(self.rounder(time))
                    + 's (' + diff_msg + str(mean_diff) + ')')


    @property
    def priority(self):
        """After the statistical observer"""
        return Priorities.Minimal
