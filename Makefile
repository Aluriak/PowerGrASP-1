PYTHON2_CMD=python2
PYTHON3_CMD=python3
PYTHON2=$(PYTHON2_CMD) powergrasp/__main__.py
PYTHON3=$(PYTHON3_CMD) -m powergrasp
PYTHON=$(PYTHON3)
#PYTHON=$(PYTHON2)
CYTOSCAPE=~/bin/cytoscape-2.8.3/cytoscape.sh
TARGET=powergrasp/__main__.py
TESTS=powergrasp/tests/
DATA=powergrasp/data/

STATFILE=--stats-file=$(DATA)statistics.csv
#PLOTFILE=--plot-file=$(DATA)statistics.png
#PLOT=--plot-stats
OUTPUT=--output-format="bbl"
FOUT=--output-file="$(DATA)output"
LOGLEVEL=--loglevel=debug
LOGLEVEL=--loglevel=info
LOGLEVEL=--loglevel=warning
#LOGLEVEL=--loglevel=critical
#INTERACTIVE=--interactive
#LBOUND=--lbound-cutoff=-1
CCCOUNT=--count-cc
MODELCOUNT=--count-model
PROFILING=--profiling
#THREAD=--thread=4
#PRE=--show-pre

ALL_OUTPUTS=$(OUTPUT) $(PLOTFILE) $(STATFILE) $(PLOT) $(AGGRESSIVE) $(LOGLEVEL) $(FOUT) $(PROFILING)
ARGS=$(MODELCOUNT) $(CCCOUNT) $(INTERACTIVE) $(LBOUND) $(NOTHREADING) $(THREAD) $(PRE)
COMMAND=$(PYTHON) $(ARGS) $(ALL_OUTPUTS)


# BENCHMARKS
BENCHMARK_INPUT=--inputs=$(TESTS)proteome_yeast_1.lp,$(TESTS)proteome_yeast_2.lp,$(TESTS)structural_binding.lp
#BENCHMARK_INPUT=--inputs=$(TESTS)proteome_yeast_1.lp,$(TESTS)proteome_yeast_2.lp
BENCHMARK_OUTPUT=$(DATA)benchmarks.csv
BENCHMARK_RUN=--runs=4

abn:
	$(COMMAND) --graph-data="$(TESTS)abnormal.lp"
bbind:
	$(COMMAND) --graph-data="$(TESTS)structural_binding_no_bridge.lp"
bintree:
	$(COMMAND) --graph-data="$(TESTS)bintree.lp"
bip:
	$(COMMAND) --graph-data="$(TESTS)bipartite.lp"
blo:
	$(COMMAND) --graph-data="$(TESTS)testblocks.lp"
cdiam:
	$(COMMAND) --graph-data="$(TESTS)double_biclique_and_clique.lp"
clique:
	$(COMMAND) --graph-data="$(TESTS)cliques.lp"
cclique:
	$(COMMAND) --graph-data="$(TESTS)big_clique.lp"
cc:
	$(COMMAND) --graph-data="$(TESTS)concomp.lp"
coli:
	$(COMMAND) --graph-data="$(TESTS)ecoli_2896-23.gml"
ccoli:
	$(COMMAND) --graph-data="$(TESTS)ecoli_2896-53.gml"
cccoli:
	$(COMMAND) --graph-data="$(TESTS)ecoli_2391-42.gml"
chloro:
	$(COMMAND) --graph-data="$(TESTS)CHLOROPHYLL-SYN.sbml"
diam:
	$(COMMAND) --graph-data="$(TESTS)diamond.lp"
ddiam:
	$(COMMAND) --graph-data="$(TESTS)double_biclique.lp"
inc:
	$(COMMAND) --graph-data="$(TESTS)inclusions.lp"
pfc:
	$(COMMAND) --graph-data="$(TESTS)perfectfit.lp"
phos:
	$(COMMAND) --graph-data="$(TESTS)phosphatase.lp"
prol:
	$(COMMAND) --graph-data="$(TESTS)proteome_yeast_1_letters.lp"
prot:
	$(COMMAND) --graph-data="$(TESTS)proteome_yeast_1.lp"
prot2:
	$(COMMAND) --graph-data="$(TESTS)proteome_yeast_2.lp"
sbind:
	$(COMMAND) --graph-data="$(TESTS)structural_binding.lp"
single:
	$(COMMAND) --graph-data="$(TESTS)singlenode.lp"
star:
	$(COMMAND) --graph-data="$(TESTS)star.lp"
three:
	$(COMMAND) --graph-data="$(TESTS)threenode.lp"
tree:
	$(COMMAND) --graph-data="$(TESTS)tree.lp"
triv:
	$(COMMAND) --graph-data="$(TESTS)trivial.lp"
tiso:
	$(COMMAND) --graph-data="$(TESTS)tiso_1.0.sbml"
uml:
	$(COMMAND) --graph-data="$(TESTS)uml.lp"
uvg:
	$(COMMAND) --graph-data="$(TESTS)umlsvg.lp"
gml:
	$(COMMAND) --graph-data="$(TESTS)gml_test.gml"
troll:
	$(COMMAND) --graph-data="$(TESTS)notsupportedformat.troll"


# this is a way to treat multiple files
pack: FOUT=--output-file="$(DATA)tmp"
pack:
	- rm -r mkdir $(DATA)tmp/*
	mkdir -p $(DATA)tmp
	$(COMMAND) --graph-data="$(TESTS)pv/2391_12.gml"
	$(COMMAND) --graph-data="$(TESTS)pv/2391_83.gml"
	$(COMMAND) --graph-data="$(TESTS)pv/502_56.gml"
	$(COMMAND) --graph-data="$(TESTS)pv/502_67.gml"
	$(COMMAND) --graph-data="$(TESTS)pv/502_76.gml"
	$(COMMAND) --graph-data="$(TESTS)pv/502_83.gml"
	rm $(DATA)tmp/*[^\.bbl]
	tar acf $(DATA)tmp.tar.gz $(DATA)tmp/

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
	$(PYTHON) --stats-file=$(DATA)statistics.csv --plot-stats

test_register:
	python setup.py register -r https://testpypi.python.org/pypi
test_install:
	python setup.py sdist upload -r https://testpypi.python.org/pypi
	pip install -U -i https://testpypi.python.org/pypi powergrasp

upload:
	python setup.py sdist upload

install:
	yes y | pip uninstall powergrasp
	pip install powergrasp

