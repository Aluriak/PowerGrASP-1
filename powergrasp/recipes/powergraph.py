"""Implementation of the regular Power Graph compression."""


import powergrasp as pg
from powergrasp.observers import ObserverBatch


def oriented_powergraph(infile:str=None, outfile:str=None, *, cfg=None,
                        observers:ObserverBatch=None):
    """Implementation of the greedy Power Graph compression,
    with a constraint on generated motifs: only oriented edges oriented in
    the same direction (from set 1 to set 2) are accepted in the motifs.

    If observers is not given, pg.observers.all() call will be used.

    If infile and outfile are given, the config should not.
    If config is given, infile and outfile should not.

    """
    if infile or outfile:
        assert infile and outfile, "both input and output files should be given"
        assert cfg is None, "Config can't be given if files are given"
        cfg = pg.Config(pg.Config.fields_for_oriented_graph(infile=infile, outfile=outfile))
    else:
        assert cfg is not None, "Config should be provided"
        cfg = pg.Config(pg.Config.fields_for_oriented_graph(**dict(cfg)))
    if observers is None:
        observers = pg.observers.built_from(cfg)
    return powergraph_template(cfg, observers=observers)


def high_priority_first(infile:str=None, outfile:str=None, *, cfg=None,
                        observers:ObserverBatch=None):
    """Implementation of the greedy Power Graph compression,
    with heuristic inspired from Dwyer et al.

    If observers is not given, pg.observers.all() call will be used.

    If infile and outfile are given, the config should not.
    If config is given, infile and outfile should not.

    """
    cfg = pg.Config(pg.Config.fields_for_prioritized_degree(
        infile=infile, outfile=outfile, default=cfg))
    if observers is None:
        observers = pg.observers.built_from(cfg)
    return powergraph_template(cfg, observers=observers)


def powergraph(infile:str=None, outfile:str=None, *, cfg=None,
               observers:ObserverBatch=None):
    """Implementation of the greedy Power Graph compression.

    If observers is not given, pg.observers.all() call will be used.

    If infile and outfile are given, the config should not.
    If config is given, infile and outfile should not.

    """
    cfg = pg.Config(infile=infile, outfile=outfile, default=cfg)
    if observers is None:
        observers = pg.observers.built_from(cfg)
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
                               motifs=[motif.Biclique.for_powergraph()])


def powergraph_template(cfg, observers:ObserverBatch=None):
    """Implementation of a greedy Power Graph compression.

    Save compressed graph in given file, and return it.
    If observers is not given, pg.observers.built_from will be used.

    """
    observers = observers or pg.observers.built_from(cfg)
    with pg.Graph(cfg, observers=observers) as graph:
        for cc in graph:
            while cc.has_motif:
                best_motif = None
                for motif in cfg.motifs:
                    best_motif = cc.search_motif(motif, alt=best_motif)
                cc.compress(best_motif)
        return graph
