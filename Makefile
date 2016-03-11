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

TIMERS=--timers
STATFILE=--stats-file=$(DATA)statistics.csv
#PLOTFILE=--plot-file=$(DATA)statistics.png
#PLOT=--plot-stats
OUTPUT=--output-format="bbl"
FOUT=--output-file="$(DATA)output.bbl"
LOGLEVEL=--loglevel=debug
LOGLEVEL=--loglevel=info
#LOGLEVEL=--loglevel=warning
#LOGLEVEL=--loglevel=critical
#INTERACTIVE=--interactive
CCCOUNT=--count-cc
MODELCOUNT=--count-model
#PROFILING=--profiling
#THREAD=--thread=0
#PRE=--show-pre
#LATTICE=--draw_lattice=$(DATA)


# PDF OUPUT PIPELINE
powerlattice:
	java -jar oog/Oog.jar -inputdir=$(DATA) -inputfiles=output.bbl -img -f=png -outputdir=$(DATA) &> /dev/null
	convert $(DATA)output.bbl.png $(DATA)output.bbl.pdf
	cd $(DATA) && ls | grep lattice_.*\.pdf | xargs -i pdfunite output.bbl.pdf {} powerlattice.pdf
	evince $(DATA)powerlattice.pdf


ALL_OUTPUTS=$(OUTPUT) $(PLOTFILE) $(STATFILE) $(TIMERS) $(PLOT) $(AGGRESSIVE) $(LOGLEVEL) $(FOUT) $(PROFILING) $(LATTICE)
ARGS=$(MODELCOUNT) $(CCCOUNT) $(INTERACTIVE) $(LBOUND) $(NOTHREADING) $(THREAD) $(PRE)
COMMAND=$(PYTHON) $(ARGS) $(ALL_OUTPUTS)


# BENCHMARKS
BENCHMARK_INPUT=--inputs=$(TESTS)proteome_yeast_1.lp,$(TESTS)proteome_yeast_2.lp,$(TESTS)structural_binding.lp
#BENCHMARK_INPUT=--inputs=$(TESTS)proteome_yeast_1.lp,$(TESTS)proteome_yeast_2.lp
BENCHMARK_OUTPUT=$(DATA)benchmarks.csv
BENCHMARK_RUN=--runs=4

basical:
	$(PYTHON3) --graph-data="$(TESTS)abnormal.lp"


abn:
	$(COMMAND) --graph-data="$(TESTS)abnormal.lp"
bbind:
	$(COMMAND) --graph-data="$(TESTS)structural_binding_no_bridge.lp"
big_biclique:
	$(COMMAND) --graph-data="$(TESTS)big_biclique.lp"
big_biclique_merged:
	$(COMMAND) --graph-data="$(TESTS)big_biclique_merged.lp"
big_clique:
	$(COMMAND) --graph-data="$(TESTS)big_clique.lp"
bintree:
	$(COMMAND) --graph-data="$(TESTS)bintree.lp"
bip:
	$(COMMAND) --graph-data="$(TESTS)bipartite.lp"
blo:
	$(COMMAND) --graph-data="$(TESTS)testblocks.lp"
cdiam:
	$(COMMAND) --graph-data="$(TESTS)double_biclique_and_clique.lp"
chr:
	$(COMMAND) --graph-data="$(TESTS)rrel_chr1_chr38.lp"
clique:
	$(COMMAND) --graph-data="$(TESTS)cliques.lp"
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
ddiamun:
	$(COMMAND) --graph-data="$(TESTS)double_biclique_unambiguous.lp"
empty:
	$(COMMAND) --graph-data="$(TESTS)empty.lp"
inc:
	$(COMMAND) --graph-data="$(TESTS)inclusions.lp"
onedge:
	$(COMMAND) --graph-data="$(TESTS)one_edge.lp"
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
redef:
	$(COMMAND) --graph-data="$(TESTS)redefedge.lp"
reduclique:
	$(COMMAND) --graph-data="$(TESTS)clique_reduction.lp"
sbind:
	$(COMMAND) --graph-data="$(TESTS)structural_binding.lp"
single:
	$(COMMAND) --graph-data="$(TESTS)singlenode.lp"
star:
	$(COMMAND) --graph-data="$(TESTS)star.lp"
testgml:
	$(COMMAND) --graph-data="$(TESTS)test.gml"
testlp:
	$(COMMAND) --graph-data="$(TESTS)test.lp"
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
troll_format:
	$(COMMAND) --graph-data="$(TESTS)notsupportedformat.troll"
troll_file:
	$(COMMAND) --graph-data="$(TESTS)thisfiledoesnt.exists"


plot:
	$(PYTHON) --plot-stats $(STATFILE)


t: test
test:
	python3 -m unittest discover -v
pest:
	py.test-3.4 powergrasp --doctest-module --failed-first --exitfirst


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
	rm asp_py_lextab.py asp_py_parsetab.py

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

pg:
	python3 -m cProfile -o out profiling.py
	gprof2dot -f pstats out | dot -Tpng -o $(DATA)profiling_graph.png
	- rm out
	feh $(DATA)profiling_graph.png
