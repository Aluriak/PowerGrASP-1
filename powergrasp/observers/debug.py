"""Observers related to debugging"""


import logging
from collections import defaultdict

from .observer import CompressionObserver, Signals
from powergrasp import commons


LOGGER = commons.logger()


class SignalProfiler(CompressionObserver):
    """On the compression end, logs stats about all received signals"""

    TEMPLATE       = "Signal {} received {} times, with type(s) {}."
    TEMPLATE_EMPTY = "None of the following signals was received: {}."
    TEMPLATE_ALL_DISPATCH = "All signals was dispatched at least once."


    def __init__(self, loglevel:str='INFO'):
        self.counts = {signal: [] for signal in Signals}  # signal: [payload type]
        self.loglevel = commons.log_level_code(loglevel)

    def on_signals(self, signals):
        for signal, payload in signals.items():
            self.counts[signal].append(type(payload))
        if Signals.CompressionFinalized in signals:
            self.logs_signals()

    def logs_signals(self):
        """Logs stats about received signals"""
        not_received = set()
        for signal, payload_types in self.counts.items():
            assert signal in Signals, "Received signal {} is not part of Signals".format(signal)
            if len(payload_types):
                LOGGER.log(self.loglevel, SignalProfiler.TEMPLATE.format(
                    signal.name, len(payload_types), ', '.join(_.__name__ for _ in set(payload_types))
                ))
            else:
                not_received.add(signal)
        if not_received:
            LOGGER.log(self.loglevel, SignalProfiler.TEMPLATE_EMPTY.format(
                ', '.join(sig.name for sig in not_received)))
        else:
            LOGGER.log(self.loglevel, SignalProfiler.TEMPLATE_ALL_DISPATCH)
