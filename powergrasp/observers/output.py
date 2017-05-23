"""
Definition of various output-related compression observers.

"""

import os
import sys
import csv
import tempfile
import statistics
from functools import partial
from collections import defaultdict

from .observer  import CompressionObserver, Signals, Priorities
from powergrasp import commons
from powergrasp import converter
from powergrasp import utils


LOGGER = commons.logger()


class ClusterWriter(CompressionObserver):
    """Write clusters in a DSV format"""

    def __init__(self, outfile_template:str):
        self.outfile_template = str(outfile_template)
        self.outfile = None  # file descriptor
        assert '{}' in self.outfile_template, "outfile must be a template"

    def write(self, powernodes:iter, poweredge:iter):
        """Write given information into CSV format"""
        writer = csv.writer(self.outfile, delimiter='\t')
        parts = defaultdict(set)
        for _, _, part, node in powernodes:
            parts[int(part)].add(node)
        poweredge = tuple(poweredge)
        assert len(poweredge) == 1
        if len(parts) == 1:  # star case or clique case
            if len(poweredge[0]) == 4:  # star case
                _, _, star_part, star = poweredge[0]
                parts[3-int(star_part)] = [star]
            else:  # clique case
                _, _, part1, _, part2 = poweredge[0]
                assert part1 == part2, "clique poweredge link two different set"
                parts[3-int(part1)] = ['(clique)']

        writer.writerow([
            ';'.join(parts[1]),
            ';'.join(parts[2]),
        ])


    def on_connected_component_started(self, payload):
        _, cc_name, atoms, _ = payload
        if self.outfile:
            raise ValueError("CC start signal sent before CC end signal")
        filename = self.outfile_template.format(cc_name.strip("").replace(' ', ''))
        self.outfile = open(filename, 'w')

    def on_model_found(self, motif):
        # give new powernodes, clique and poweredges to converter
        self.write(
            (a.args for a in motif.model.get('powernode')),
            (a.args for a in motif.model.get('poweredge')),
        )


    def on_connected_component_stopped(self, remain_edges:'AtomsModel'):
        if not self.outfile:
            raise ValueError("CC end signal sent before CC start signal")
        self.outfile.close()
        self.outfile = None


class InteractiveCompression(CompressionObserver):
    """Make the compression interactive: ask for an input from user
    at the end of each step"""

    def on_step_stopped(self):
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

    def on_connected_component_started(self, payload):
        _, cc_name, atoms, _ = payload
        graphdict = utils.asp2graph(atoms)
        filename = self.basename.format(cc_name)
        utils.draw_lattice(graphdict, filename)
        LOGGER.info('Line diagram of CC ' + str(cc_name)
                    + ' saved in ' + filename)


class OutputWriter(CompressionObserver):
    """Manage the output bubble file, and assure its conversion
    into expected output format

    """

    def __init__(self, outfile:str=None, outformat:str=None, oriented:bool=False):
        self.format = OutputWriter.format_deduced_from(outfile, outformat)
        self.output = str(outfile or '')
        self.oriented = bool(oriented)
        self.write_to_stdout = not bool(self.output)


    def on_model_found(self, motif):
        SIGNAL_MODEL_ATOMS = {'powernode', 'clique', 'poweredge'}
        # give new powernodes, clique and poweredges to converter
        model_atoms = motif.model.get_str(SIGNAL_MODEL_ATOMS)
        self.write(str(model_atoms))

    def on_connected_component_started(self, payload):
        cc_num, cc_name, cc_atoms, cc_density = payload
        self.comment("CONNECTED COMPONENT {}: {} (density={})".format(int(cc_num), cc_name, round(cc_density, 3)))

    def on_connected_component_stopped(self, remain_edges:'AtomsModel'):
        self.write(str(remain_edges))
        self.finalize_cc()

    def on_compression_started(self):
        self.init_writer()

    def on_compression_stopped(self):
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
            converter.bbl_to_output(self.fd.name, self.output,
                                    self.format, self.oriented)

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
    def format_deduced_from(output_file:str, output_format:str=None):
        """Return the most likely expected output format by looking at given args"""
        # look at the output_file extension if output_format is unusable
        if not output_format or output_format not in converter.OUTPUT_FORMATS:
            try:
                # infer from file extension
                output_format = os.path.splitext(output_file)[1].lstrip('.')
            except (IndexError, AttributeError):
                LOGGER.warning("Given outfile ({}) will be written in"
                               " bubble format because of unknow"
                               " extension.".format(output_file))
                output_format = converter.DEFAULT_OUTPUT_FORMAT  # use BBL
        return output_format


class PerCCOutputWriter(CompressionObserver):
    """Manage the output bubble file, and assure its conversion
    into expected output format.

    Works per CC.

    """

    def __init__(self, outfile_template:str, outformat:str='bbl',
                 oriented:bool=False):
        self.outfile_template = str(outfile_template)
        self.writer_cons = partial(OutputWriter, outformat=outformat, oriented=oriented)
        assert '{}' in self.outfile_template

    def on_model_found(self, motif):
        self.writer.on_model_found(motif)

    def on_connected_component_started(self, payload):
        _, cc_name, atoms, _ = payload
        self.writer = self.writer_cons(
            self.outfile_template.format(cc_name.replace(' ', '')),
        )
        self.writer.init_writer()
        self.writer.on_connected_component_started(payload)

    def on_connected_component_stopped(self, remain_edges:'AtomsModel'):
        self.writer.on_connected_component_stopped(remain_edges)
        self.writer.finalized()

    def comment(self, _): pass

    # def on_compression_started(self):
        # pass  # nothing to do

    # def on_compression_stopped(self):
        # pass  # nothing to do



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


    def on_compression_stopped(self):
        if self.time_counter is None:
            return
        time = self.time_counter.compression_time
        self.save_time(time)
        self.show(time)


    def save_time(self, new_time):
        if self.save_result:
            with open(self.filename, 'a') as fd:
                fd.write(str(new_time) + '\n')
        else:
            pass


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
