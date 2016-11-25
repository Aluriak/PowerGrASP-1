"""Implementation of the regular Power Graph compression."""


import powergrasp as pg


def powergraph(infile:str, outfile:str=None, observers=None, cfg=None):
    """Implementation of the greedy Power Graph compression.

    Save compressed graph in given file, and return it.
    If observers is not given, pg.observers.all() call will be used.

    """
    if observers is None:
        if cfg is None:
            cfg, observers = pg.observers.most()
        else:
            observers = observers.built_from(cfg)
    elif cfg is None:
        cfg = pg.config.Configuration(infile=infile, outfile=outfile)
    return powergraph_template(cfg, observers=observers)


def profiling(inputfile:str, per_cc=False) -> '?':
    """Return the profiling of the input graph"""

    graph = pg.Graph.from_file(inputfile)
    if per_cc:
        for cc in graph:
            pass
    else:
        pass


def bipartite_powergraph(inputfile:str, outputfile:str=None,
                         observers=None):
    raise NotImplementedError
    return powergraph_template(inputfile, outputfile,
                               observers=observers or pg.observers.most(),
                               motifs=[motif.BICLIQUE])


def powergraph_template(cfg, observers:pg.observers.ObserverBatch=None):
    """Implementation of a greedy Power Graph compression.

    Save compressed graph in given file, and return it.
    If observers is not given, pg.observers.built_from will be used.

    """
    observers = observers or pg.observers.built_from(cfg)
    with pg.Graph(cfg, observers=observers) as graph:
        motifs = [pg.motif.CLIQUE, pg.motif.BICLIQUE]
        for cc in graph:
            while cc.has_motif:
                best_motif = None
                for motif in motifs:
                    best_motif = cc.search_motif(motif, alt=best_motif)
                cc.compress(best_motif)
        return graph
