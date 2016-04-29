"""
Definition of various output-related compression observers.

"""
import sys
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
    """Manage the output file, and conversion into expected output format"""

    def __init__(self, output_filename, output_format):
        format = OutputWriter.format_deduced_from(output_filename, output_format)
        self.output = open(output_filename, 'w') if output_filename else sys.stdout
        self.converter = converter.output_converter_for(format)

    def _update(self, signals):
        # print('Output Writer:', signals)
        if Signals.ModelFound in signals:
            # give new powernodes to converter
            atoms = signals[Signals.ModelFound]
            self.converter.convert(atoms)
        if Signals.ConnectedComponentStopped in signals:
            self.output.write(self.converter.finalized())
            self.converter.reset_containers()
            LOGGER.debug('Final data saved in file ' + self.output.name)
        if Signals.CCRemainEdgeGenerated in signals:
            remain_edges = signals[Signals.CCRemainEdgeGenerated]
            self.converter.convert(remain_edges)
        if Signals.CompressionStopped in signals:
            if self.output is not sys.stdout: self.output.close()
        if Signals.CompressionStarted in signals:
            self.output.write(self.converter.header())

    def comment(self, lines):
        """Add given lines to output as comments"""
        self.output.write(self.converter.comment(lines))

    @property
    def priority(self):
        return Priorities.Minimal

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
