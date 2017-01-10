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
STATFILE=$(DATA)statistics.csv
PLOTFILE=$(DATA)statistics.png

TIMERS=--timers
STATFILE_OPT=--stats-file=$(STATFILE)
# PLOTFILE_OPT=--plot-file=$(PLOTFILE)
# PLOT=--plot-stats
# OUTPUT=--outformat="bbl"
# FOUT=--outfile="todel/output_{}.bbl"
FOUT=--outfile="$(DATA)output.bbl"
# FOUT=--outfile="$(DATA)output.dot"
# FOUT=--outfile="$(DATA)output.gexf"
LOGLEVEL=--loglevel=debug
LOGLEVEL=--loglevel=info
#LOGLEVEL=--loglevel=warning
#LOGLEVEL=--loglevel=critical
#INTERACTIVE=--interactive
CCCOUNT=--count-cc
MODELCOUNT=--count-model
# PROFILING=--profiling
SIGNAL_PROFILER=--signal-profile
# THREAD=--thread=0
# PRE=--show-pre
# LATTICE=--draw_lattice=$(DATA)

COMPRESSION_METHOD=powergraph
# COMPRESSION_METHOD=OEM
# COMPRESSION_METHOD=oriented
# COMPRESSION_METHOD=HPF
# COMPRESSION_METHOD=FHPF
# COMPRESSION_METHOD=K2HPF

# PDF OUPUT PIPELINE
powerlattice:
	java -jar oog/Oog.jar -inputdir=$(DATA) -inputfiles=output.bbl -img -f=png -outputdir=$(DATA) &> /dev/null
	convert $(DATA)output.bbl.png $(DATA)output.bbl.pdf
	cd $(DATA) && ls | grep lattice_.*\.pdf | xargs -i pdfunite output.bbl.pdf {} powerlattice.pdf
	evince $(DATA)powerlattice.pdf


ALL_OUTPUTS=$(OUTPUT) $(PLOTFILE_OPT) $(STATFILE_OPT) $(TIMERS) $(PLOT) $(AGGRESSIVE) $(LOGLEVEL) $(FOUT) $(PROFILING) $(LATTICE)
ARGS=$(MODELCOUNT) $(CCCOUNT) $(INTERACTIVE) $(LBOUND) $(NOTHREADING) $(THREAD) $(PRE) $(SIGNAL_PROFILER)
COMMAND=$(PYTHON) $(COMPRESSION_METHOD) $(ARGS) $(ALL_OUTPUTS)


# BENCHMARKS
BENCHMARK_INPUT=--inputs=$(TESTS)proteome_yeast_1.lp,$(TESTS)proteome_yeast_2.lp,$(TESTS)structural_binding.lp
#BENCHMARK_INPUT=--inputs=$(TESTS)proteome_yeast_1.lp,$(TESTS)proteome_yeast_2.lp
BENCHMARK_OUTPUT=$(DATA)benchmarks.csv
BENCHMARK_RUN=--runs=4

basical:
	$(PYTHON3) powergraph "$(TESTS)abnormal.lp"


aci:
	$(COMMAND) "$(TESTS)AcinetoPB.graphml"
abn:
	$(COMMAND) "$(TESTS)abnormal.lp"
atro:
	$(COMMAND) "$(TESTS)atropaPB.graphml"
bbind:
	$(COMMAND) "$(TESTS)structural_binding_no_bridge.lp"
big_biclique:
	$(COMMAND) "$(TESTS)big_biclique.lp"
big_biclique_merged:
	$(COMMAND) "$(TESTS)big_biclique_merged.lp"
big_clique:
	$(COMMAND) "$(TESTS)big_clique.lp"
bintree:
	$(COMMAND) "$(TESTS)bintree.lp"
biog12:
	$(COMMAND) "$(TESTS)biogenouest12.lp"
biog12NA:
	$(COMMAND) "$(TESTS)biogenouest12NA.lp"
biog2:
	$(COMMAND) "$(TESTS)biogenouest2.lp"
bip:
	$(COMMAND) "$(TESTS)bipartite.lp"
blo:
	$(COMMAND) "$(TESTS)testblocks.lp"
bollo:
	$(COMMAND) "$(TESTS)bollobas.lp"
cdiam:
	$(COMMAND) "$(TESTS)double_biclique_and_clique.lp"
chr:
	$(COMMAND) "$(TESTS)rrel_chr1_chr38.lp"
clique:
	$(COMMAND) "$(TESTS)clique.lp"
cliques:
	$(COMMAND) "$(TESTS)cliques.lp"
cc:
	$(COMMAND) "$(TESTS)concomp.lp"
coli:
	$(COMMAND) "$(TESTS)ecoli_2896-23.gml"
ccoli:
	$(COMMAND) "$(TESTS)ecoli_2896-53.gml"
cccoli:
	$(COMMAND) "$(TESTS)ecoli_2391-42.gml"
cordi:
	$(COMMAND) "$(TESTS)CordiPB.graphml"
chloro:
	$(COMMAND) "$(TESTS)CHLOROPHYLL-SYN.sbml"
disjoint:
	$(COMMAND) "$(TESTS)disjoint.lp"
diacli:
	$(COMMAND) "$(TESTS)diacli.lp"
diam:
	$(COMMAND) "$(TESTS)diamond.lp"
ddiam:
	$(COMMAND) "$(TESTS)double_biclique.lp"
ddiamun:
	$(COMMAND) "$(TESTS)double_biclique_unambiguous.lp"
edgetest:
	$(COMMAND) "$(TESTS)edges_test.lp"
empty:
	$(COMMAND) "$(TESTS)empty.lp"
glasses:
	$(COMMAND) "$(TESTS)glasses.lp"
inc:
	$(COMMAND) "$(TESTS)inclusions.lp"
lattice:
	$(COMMAND) "$(TESTS)lattice.lp"
matrixdb:
	$(COMMAND) "$(TESTS)matrixdb_network.lp"
partition:
	$(COMMAND) "$(TESTS)partition.lp"
onedge:
	$(COMMAND) "$(TESTS)one_edge.lp"
or_double_edge:
	$(COMMAND) "$(TESTS)oriented_double_edge.lp"
or_lattice:
	$(COMMAND) "$(TESTS)oriented_lattice.lp"
or_overlap:
	$(COMMAND) "$(TESTS)oriented_overlap.lp"
or_simple:
	$(COMMAND) "$(TESTS)oriented_simple.lp"
pfc:
	$(COMMAND) "$(TESTS)perfectfit.lp"
phos:
	$(COMMAND) "$(TESTS)phosphatase.lp"
priodeg:
	$(COMMAND) "$(TESTS)prio_deg.lp"
priodeg_str:
	$(COMMAND) "$(TESTS)prio_deg_str.lp"
prol:
	$(COMMAND) "$(TESTS)proteome_yeast_1_letters.lp"
prot:
	$(COMMAND) "$(TESTS)proteome_yeast_1.lp"
prot2:
	$(COMMAND) "$(TESTS)proteome_yeast_2.lp"
redef:
	$(COMMAND) "$(TESTS)redefedge.lp"
reduclique:
	$(COMMAND) "$(TESTS)clique_reduction.lp"
rna_mi_m:
	$(COMMAND) "$(TESTS)miRNA_mRNA.lp"
rna_pi_lnc:
	$(COMMAND) "$(TESTS)piRNA_lncRNA.lp"
rna_pi_msg:
	$(COMMAND) "$(TESTS)piRNA_mRNA.lp"
sbind:
	$(COMMAND) "$(TESTS)structural_binding.lp"
sbind_maincc:
	$(COMMAND) "$(TESTS)structural_binding_maincc.lp"
simple:
	$(COMMAND) "$(TESTS)simple.lp"
single:
	$(COMMAND) "$(TESTS)singlenode.lp"
ssn:
	$(COMMAND) "$(TESTS)ssn.lp"
star:
	$(COMMAND) "$(TESTS)star.lp"
testgml:
	$(COMMAND) "$(TESTS)test.gml"
testgraphml:
	$(COMMAND) "$(TESTS)test.graphml"
testlp:
	$(COMMAND) "$(TESTS)test.lp"
three:
	$(COMMAND) "$(TESTS)threenode.lp"
tree:
	$(COMMAND) "$(TESTS)tree.lp"
triv:
	$(COMMAND) "$(TESTS)trivial.lp"
tiso:
	$(COMMAND) "$(TESTS)tiso_1.0.sbml"
uml:
	$(COMMAND) "$(TESTS)uml.lp"
unclique:
	$(COMMAND) "$(TESTS)unclique.lp"
uvg:
	$(COMMAND) "$(TESTS)umlsvg.lp"
gml:
	$(COMMAND) "$(TESTS)gml_test.gml"
troll_format:
	$(COMMAND) "$(TESTS)notsupportedformat.troll"
troll_file:
	$(COMMAND) "$(TESTS)thisfiledoesnt.exists"


plot:
	$(PYTHON) --plot-stats --stats-file=$(STATFILE)


unittest:
	python3 -m unittest discover -v
t: pytest
pytest:
	pytest powergrasp --doctest-module --failed-first
te: pytest_exit
pytest_exit:
	pytest powergrasp --doctest-module --failed-first --exitfirst
pylint:
	pylint powergrasp > doc/pylint_report.txt


# this is a way to treat multiple files
pack: FOUT=--output-file="$(DATA)tmp"
pack:
	- rm -r mkdir $(DATA)tmp/*
	mkdir -p $(DATA)tmp
	$(COMMAND) "$(TESTS)pv/2391_12.gml"
	$(COMMAND) "$(TESTS)pv/2391_83.gml"
	$(COMMAND) "$(TESTS)pv/502_56.gml"
	$(COMMAND) "$(TESTS)pv/502_67.gml"
	$(COMMAND) "$(TESTS)pv/502_76.gml"
	$(COMMAND) "$(TESTS)pv/502_83.gml"
	rm $(DATA)tmp/*[^\.bbl]
	tar acf $(DATA)tmp.tar.gz $(DATA)tmp/

benchmarks:
	$(PYTHON2_CMD) powergrasp/benchmarks.py $(BENCHMARK_INPUT) --output-file=$(BENCHMARK_OUTPUT) $(BENCHMARK_RUN)
	cat $(BENCHMARK_OUTPUT)

clr: clear
clear:
	- rm */*.pyc
	- rm __pycache__/ */__pycache__/ -r
	- rm powergrasp.egg-info/ -r
	- rm asp_py_lextab.py asp_py_parsetab.py
	- rm powergrasp/logs/*.logs*
	- rm unittest.logs

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
