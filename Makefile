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
#INTERACTIVE=--interactive
#LBOUND=--lbound-cutoff=-1
MODELCOUNT=--count-model
#NOTHREADING=--no-threading
PROFILING=--profiling

ALL_OUTPUTS=$(OUTPUT) $(PLOTFILE) $(STATFILE) $(PLOT) $(AGGRESSIVE) $(LOGLEVEL) $(FOUT) $(PROFILING)
ARGS=$(MODELCOUNT) $(INTERACTIVE) $(LBOUND) $(NOTHREADING)
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
cclique:
	$(COMMAND) --graph-data="tests/big_clique.lp"
single:
	$(COMMAND) --graph-data="tests/singlenode.lp"
star:
	$(COMMAND) --graph-data="tests/star.lp"
bip:
	$(COMMAND) --graph-data="tests/bipartite.lp"
cc:
	$(COMMAND) --graph-data="tests/concomp.lp"
chloro:
	$(COMMAND) --graph-data="tests/CHLOROPHYLL-SYN.sbml"
uml:
	$(COMMAND) --graph-data="tests/uml.lp"
uvg:
	$(COMMAND) --graph-data="tests/umlsvg.lp"
gml:
	$(COMMAND) --graph-data="tests/gml_test.gml"
coli:
	$(COMMAND) --graph-data="tests/ecoli_2896-23.gml"
ccoli:
	$(COMMAND) --graph-data="tests/ecoli_2896-53.gml"
cccoli:
	$(COMMAND) --graph-data="tests/ecoli_2391-42.gml"
troll:
	$(COMMAND) --graph-data="tests/notsupportedformat.troll"


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

