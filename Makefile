PYTHON2_CMD=python2
PYTHON3_CMD=python3
PYTHON2=$(PYTHON2_CMD) powergrasp/__main__.py
PYTHON3=$(PYTHON3_CMD) -m powergrasp
PYTHON=$(PYTHON3)
#PYTHON=$(PYTHON2)
CYTOSCAPE=~/bin/cytoscape-2.8.3/cytoscape.sh
TARGET=powergrasp/__main__.py

STATFILE=--stats-file=data/statistics.csv
#PLOTFILE=--plot-file=data/statistics.png
#PLOT=--plot-stats
OUTPUT=--output-format="bbl"
FOUT=--output-file="data/output"
LOGLEVEL=--loglevel=debug
LOGLEVEL=--loglevel=info
LOGLEVEL=--loglevel=warning
#LOGLEVEL=--loglevel=critical
#INTERACTIVE=--interactive
#LBOUND=--lbound-cutoff=-1
CCCOUNT=--count-cc
MODELCOUNT=--count-model
#NOTHREADING=--no-threading
PROFILING=--profiling
#THREAD=--thread=4
#PRE=--show-pre

ALL_OUTPUTS=$(OUTPUT) $(PLOTFILE) $(STATFILE) $(PLOT) $(AGGRESSIVE) $(LOGLEVEL) $(FOUT) $(PROFILING)
ARGS=$(MODELCOUNT) $(CCCOUNT) $(INTERACTIVE) $(LBOUND) $(NOTHREADING) $(THREAD) $(PRE)
COMMAND=$(PYTHON) $(ARGS) $(ALL_OUTPUTS)


# BENCHMARKS
BENCHMARK_INPUT=--inputs=tests/proteome_yeast_1.lp,tests/proteome_yeast_2.lp,tests/structural_binding.lp
#BENCHMARK_INPUT=--inputs=tests/proteome_yeast_1.lp,tests/proteome_yeast_2.lp
BENCHMARK_OUTPUT=data/benchmarks.csv
BENCHMARK_RUN=--runs=4

abn:
	$(COMMAND) --graph-data="tests/abnormal.lp"
bbind:
	$(COMMAND) --graph-data="tests/structural_binding_no_bridge.lp"
bintree:
	$(COMMAND) --graph-data="tests/bintree.lp"
bip:
	$(COMMAND) --graph-data="tests/bipartite.lp"
blo:
	$(COMMAND) --graph-data="tests/testblocks.lp"
cdiam:
	$(COMMAND) --graph-data="tests/double_biclique_and_clique.lp"
clique:
	$(COMMAND) --graph-data="tests/cliques.lp"
cclique:
	$(COMMAND) --graph-data="tests/big_clique.lp"
cc:
	$(COMMAND) --graph-data="tests/concomp.lp"
coli:
	$(COMMAND) --graph-data="tests/ecoli_2896-23.gml"
ccoli:
	$(COMMAND) --graph-data="tests/ecoli_2896-53.gml"
cccoli:
	$(COMMAND) --graph-data="tests/ecoli_2391-42.gml"
chloro:
	$(COMMAND) --graph-data="tests/CHLOROPHYLL-SYN.sbml"
diam:
	$(COMMAND) --graph-data="tests/diamond.lp"
ddiam:
	$(COMMAND) --graph-data="tests/double_biclique.lp"
inc:
	$(COMMAND) --graph-data="tests/inclusions.lp"
pfc:
	$(COMMAND) --graph-data="tests/perfectfit.lp"
phos:
	$(COMMAND) --graph-data="tests/phosphatase.lp"
prol:
	$(COMMAND) --graph-data="tests/proteome_yeast_1_letters.lp"
prot:
	$(COMMAND) --graph-data="tests/proteome_yeast_1.lp"
prot2:
	$(COMMAND) --graph-data="tests/proteome_yeast_2.lp"
sbind:
	$(COMMAND) --graph-data="tests/structural_binding.lp"
single:
	$(COMMAND) --graph-data="tests/singlenode.lp"
star:
	$(COMMAND) --graph-data="tests/star.lp"
three:
	$(COMMAND) --graph-data="tests/threenode.lp"
tree:
	$(COMMAND) --graph-data="tests/tree.lp"
triv:
	$(COMMAND) --graph-data="tests/trivial.lp"
tiso:
	$(COMMAND) --graph-data="tests/tiso_1.0.sbml"
uml:
	$(COMMAND) --graph-data="tests/uml.lp"
uvg:
	$(COMMAND) --graph-data="tests/umlsvg.lp"
gml:
	$(COMMAND) --graph-data="tests/gml_test.gml"
troll:
	$(COMMAND) --graph-data="tests/notsupportedformat.troll"


# this is a way to treat multiple files
pack: FOUT=--output-file="data/tmp"
pack:
	- rm -r mkdir data/tmp/*
	mkdir -p data/tmp
	$(COMMAND) --graph-data="tests/pv/2391_12.gml"
	$(COMMAND) --graph-data="tests/pv/2391_83.gml"
	$(COMMAND) --graph-data="tests/pv/502_56.gml"
	$(COMMAND) --graph-data="tests/pv/502_67.gml"
	$(COMMAND) --graph-data="tests/pv/502_76.gml"
	$(COMMAND) --graph-data="tests/pv/502_83.gml"
	rm data/tmp/*[^\.bbl]
	tar acf data/tmp.tar.gz data/tmp/

benchmarks:
	$(PYTHON2_CMD) powergrasp/benchmarks.py $(BENCHMARK_INPUT) --output-file=$(BENCHMARK_OUTPUT) $(BENCHMARK_RUN)
	cat $(BENCHMARK_OUTPUT)

clr: clear
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

