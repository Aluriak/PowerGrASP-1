"""Definition of the Graph class.

Belongs to the main client API.
See recipes submodule in order to get usage examples.

"""


from powergrasp import config
from powergrasp import solving
from powergrasp.observers import Signals
from powergrasp.connected_component import ConnectedComponent


class Graph:
    """Main object of the client API, offering high level function to compress
    and express algorithms.

    Graph Works closely with ConnectedComponent class.
    See recipes submodule in order to get usage examples.

    """

    def __init__(self, cfg:config.Configuration, observers:iter=None):
        """

        cfg -- Configuration instance ready to go
        observers -- iterable of observers to signal during treatments

        """
        self.observers = observers or []
        self.infile = cfg.infile
        self.config = cfg
        self._ccs = []  # will hold ConnectedComponent instances
        assert cfg is not None


    def __iter__(self):
        """Yield iterable on connected components of the graph"""
        if self._ccs:
            yield from self._ccs
        else:
            yield from self.compute_cc()


    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.finalize()


    def finalize(self):
        """Notify all observers in order to finish the compression"""
        # collect final information through connected components
        total_remain_edges_counter = 0
        total_edges_counter = 0
        for cc in self.ccs:
            total_remain_edges_counter += cc.remaining_edges_count
            total_edges_counter += cc.initial_edges_count

        # notify
        self.observers.signal(
            final_edge_count_generated=total_edges_counter,
            final_remain_edge_count_generated=total_remain_edges_counter)
        self.observers.signal(Signals.CompressionStopped)
        self.observers.signal(Signals.CompressionFinalized)


    def build_connected_component(self, **kwargs):
        """Return a ConnectedComponent object created with given args.

        This method is here to be overwritten by subclasses,
        allowing client to define its own connected components.

        """
        return ConnectedComponent(**kwargs)


    def compute_cc(self):
        """Yield the connected components data found in data graph.

        The instance will conserve a reference to
         the new ConnectedComponent instances.

        """
        self.observers.signal(Signals.ExtractionStarted)

        assert self.config.biclique_config.__class__.__name__ != 'function'
        for model in solving.all_models_from('', aspfiles=[self.config.graph_file],
                                             aspconfig=self.config.extract_config):
            atom_counts = model.counts
            cc_atom = model.get_only('cc').args
            assert len(cc_atom) == 1, "Extraction yield a cc/{} atom".format(len(cc_atom))
            cc_id = str(cc_atom[0])
            atoms = ('{}({}).'.format(name, ','.join(args))
                     for name, args  in model.atoms)
            print(self.ccs)
            cc_object = self.build_connected_component(
                cc_id=cc_id,
                node_number=int(atom_counts['membercc']),
                edge_number=int(atom_counts['oedge']),
                atoms=''.join(atoms),
                observers=self.observers,
                config=config
            )
            self._ccs.append(cc_object)
            print(self.ccs)
            yield cc_object
        self.observers.signal(Signals.ExtractionStopped)


    @property
    def ccs(self):
        return self._ccs
