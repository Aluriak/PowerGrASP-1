"""Observers related to debugging"""


import logging
from collections import defaultdict

from .observer import CompressionObserver, Signals, SIGNAL_FOUND
from powergrasp import commons


LOGGER = commons.logger()


class SignalProfiler(CompressionObserver):
    """On the compression end, logs stats about all received signals"""

    TEMPLATE       = "Signal {} receive {} times, with type(s) {}."
    TEMPLATE_EMPTY = "None of the following signals was received: {}."


    def __init__(self, loglevel:str='INFO'):
        self.counts = {signal: [] for signal in Signals}  # signal: [payload type]
        self.loglevel = commons.log_level_code(loglevel)

    def _update(self, signals):
        for signal, payload in signals.items():
            self.counts[signal].append(type(payload))
        if Signals.CompressionFinalized in signals:
            self.logs_signals()

    def logs_signals(self):
        """Logs stats about received signals"""
        not_received = set()
        for signal, payload_types in self.counts.items():
            if len(payload_types):
                LOGGER.log(self.loglevel, SignalProfiler.TEMPLATE.format(
                    str(signal), len(payload_types), ', '.join(str(_) for _ in set(payload_types))
                ))
            else:
                not_received.add(signal)
        LOGGER.log(self.loglevel, SignalProfiler.TEMPLATE_EMPTY.format(', '.join(str(sig) for sig in not_received)))
