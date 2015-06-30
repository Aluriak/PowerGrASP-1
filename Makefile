PYTHON=python2 powergrasp/__main__.py
PYTHON3=python3 -m powergrasp
CYTOSCAPE=~/bin/cytoscape-2.8.3/cytoscape.sh
TARGET=powergrasp/__main__.py

STATFILE=--stats-file=data/statistics.csv
#PLOTFILE=--plot-file=data/statistics.png
#PLOT=--plot-stats
OUTPUT=--output-format="bbl"
#FOUT=--output-file="data/output_alt"
LOGLEVEL=--loglevel=debug
LOGLEVEL=--loglevel=info
#LOGLEVEL=--loglevel=critical
#AGGRESSIVE=--aggressive
#INTERACTIVE=--interactive
#LBOUND=--lbound-cutoff=-1
MODELCOUNT=--count-model
#NOTHREADING=--no-threading

ALL_OUTPUTS=$(OUTPUT) $(PLOTFILE) $(STATFILE) $(PLOT) $(AGGRESSIVE) $(LOGLEVEL) $(FOUT)
ARGS=$(MODELCOUNT) $(INTERACTIVE) $(LBOUND) $(HEURISTIC) $(NOTHREADING)
COMMAND=$(PYTHON) $(ARGS) $(ALL_OUTPUTS)



diam:
	$(COMMAND) --graph-data="tests/diamond.lp"
ddiam:
	$(COMMAND) --graph-data="tests/double_biclique.lp"
cdiam:
	$(COMMAND) --graph-data="tests/double_biclique_and_clique.lp"
three:
	$(COMMAND) --graph-data="tests/threenode.lp"
pfc:
	$(COMMAND) --graph-data="tests/perfectfit.lp"
blo:
	$(COMMAND) --graph-data="tests/testblocks.lp"
prot2:
	$(COMMAND) --graph-data="tests/proteome_yeast_2.lp"
prot:
	$(COMMAND) --graph-data="tests/proteome_yeast_1.lp"
prol:
	$(COMMAND) --graph-data="tests/proteome_yeast_1_letters.lp"
phos:
	$(COMMAND) --graph-data="tests/phosphatase.lp"
sbind:
	$(COMMAND) --graph-data="tests/structural_binding.lp"
bbind:
	$(COMMAND) --graph-data="tests/structural_binding_no_bridge.lp"
triv:
	$(COMMAND) --graph-data="tests/trivial.lp"
clique:
	$(COMMAND) --graph-data="tests/cliques.lp"
single:
	$(COMMAND) --graph-data="tests/singlenode.lp"
star:
	$(COMMAND) --graph-data="tests/star.lp"
bip:
	$(COMMAND) --graph-data="tests/bipartite.lp"
cc:
	$(COMMAND) --graph-data="tests/concomp.lp"

clear:
	rm */*.pyc
help:
	$(PYTHON) --help

tar:
	cd .. && tar acf tarball.tar.gz asprgc/
zip:
	cd .. && zip -r tarball.zip asprgc/
tarasp:
	tar acvf ASPsources.tar.gz asprgc/ASPsources/

cytoscape:
	$(CYTOSCAPE)
show:
	$(PYTHON) --stats-file=data/statistics.csv --plot-stats

