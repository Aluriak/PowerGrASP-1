"""

For CLI usage, see the help:
    python -m powergrasp --help

output formats:
    BBL         formated in Bubble format, readable by CyOog plugin of Cytoscape

input formats:
    ASP         edge/2 atoms, where edge(X,Y) describes a link between X and Y.
    SBML        SBML file. Species and reactions will be translated as nodes.
    GML         Graph Modeling Language file.

"""


from powergrasp import recipes
from powergrasp import config
from powergrasp import plotting


if __name__ == '__main__':

    cfg = config.Configuration.from_cli()
    recipes.powergraph(cfg=cfg)

    # plotting if statistics csv file given, and showing or saving requested
    if (cfg.plot_stats or cfg.plot_file) and cfg.stats_file:
        plotting.plots(cfg.stats_file, savefile=cfg.plot_file)
