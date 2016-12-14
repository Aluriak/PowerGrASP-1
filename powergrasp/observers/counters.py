"""
Definition of various counting related compression observers.

"""
from .observer import CompressionObserver, Signals, SIGNAL_MOTIF
from powergrasp import commons


LOGGER = commons.logger()


class ConnectedComponentsCounter(CompressionObserver):
    """Counter of connected components"""

    def __init__(self):
        self._nb_ccs = '?'  # number of cc, printed after current cc number

    def on_cc_count_generated(self, nb_cc:int):
        self._nb_ccs = int(nb_cc)

    def on_connected_component_stopped(self, atoms:'AtomsModel'):
        count = atoms.counts.get('edge', 0)
        if count > 0:
            LOGGER.info(self.cc_name + ': ' + str(count)
                        + ' remaining edge(s)')
        else:
            LOGGER.info(self.cc_name + ': ' + 'No remaining edge')

    def on_connected_component_started(self, payload):
        num, name, _, _ = payload
        self.cc_num, self.cc_name = int(num), str(name)
        LOGGER.info('#### CC ' + self.cc_name + ' ' + str(self.cc_num+1)
                    + '/' + str(self._nb_ccs))

    @property
    def nb_ccs(self) -> int:
        return int(self._nb_ccs)

    @property
    def current_cc(self) -> (str, int):
        return self.cc_name, self.cc_num


class ObjectCounter(CompressionObserver):
    """Counter of objects, based on received signals ending with '_found'"""

    PREFIX = '_counter_'

    def __init__(self):
        self.props = set()


    def on_model_found(self, result):
        # incrementation of the internal counter associated with given motif
        motif = result.motif
        prop = ObjectCounter.property_named_from(motif)
        self.props.add(prop)
        setattr(self, prop, getattr(self, prop, 0) + 1)

    def on_compression_finalized(self):
        for prop in self.props:
            LOGGER.info(self.__class__.__name__ + ': '
                        + ObjectCounter.prettified(prop)
                        + ': ' + str(getattr(self, prop)))


    @staticmethod
    def property_named_from(signal_payload):
        "Return the property name deduced from the signal name"
        return ObjectCounter.PREFIX + str(signal_payload)

    @staticmethod
    def prettified(property_name):
        "Return the prettified property name deduced from the property name"
        property_name = property_name[len(ObjectCounter.PREFIX):]
        return property_name.replace('_', ' ').title()

    @property
    def count(self):
        return {prop.split('_')[-1]: int(getattr(self, prop))
                for prop in self.props}
