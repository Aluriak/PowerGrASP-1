"""
Definition of various output-related compression observers.

"""
import sys

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
        self.last_cc = None

    def _update(self, signals):
        if Signals.ConnectedComponentStarted in signals:
            _, self.last_cc = signals[Signals.ConnectedComponentStarted]
        if self.last_cc is not None and Signals.PreprocessingStopped in signals:
            atoms = signals[Signals.PreprocessingStopped]
            graphdict = utils.asp2graph(atoms)
            cc_filename = self.basename.format(self.last_cc)
            utils.line_diagram(graphdict, filename=cc_filename)
            LOGGER.info('Line diagram of CC ' + str(self.last_cc)
                        + ' saved in ' + cc_filename)
            self.last_cc = None  # don't react next iteration of the same connected component


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
