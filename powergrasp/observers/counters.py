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

    def _update(self, signals):
        if Signals.CCCountGenerated in signals:
            self._nb_ccs = int(signals[Signals.CCCountGenerated])
        if Signals.ConnectedComponentStopped in signals:
            count = signals[Signals.ConnectedComponentStopped].counts.get('oedge', 0)
            if count > 0:
                LOGGER.info(self.cc_name + ': ' + str(count)
                            + ' remaining edge(s)')
            else:
                LOGGER.info(self.cc_name + ': ' + 'No remaining edge')
        if Signals.ConnectedComponentStarted in signals:
            self.cc_num, self.cc_name, _ = signals[Signals.ConnectedComponentStarted]
            LOGGER.info('#### CC ' + self.cc_name + ' ' + str(self.cc_num+1)
                        + '/' + str(self._nb_ccs))


class ObjectCounter(CompressionObserver):
    """Counter of objects, based on received signals ending with '_found'"""

    PREFIX = '_counter_'

    def __init__(self):
        self.props = []

    def _update(self, signals):
        if Signals.ModelFound in signals:
            # incrementation of the internal counter associated with given motif
            motif = signals[Signals.ModelFound].motif
            prop = ObjectCounter.property_named_from(motif)
            setattr(self, prop, getattr(self, prop, 0) + 1)

        if Signals.CompressionFinalized in signals:
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
