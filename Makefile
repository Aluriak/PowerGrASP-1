PYTHON=python2
CYTOSCAPE=~/bin/cytoscape-2.8.3/cytoscape.sh

TARGET=powergrasp/__main__.py
#INTERACTIVE=--interactive=True
ITERATIONS=--iterations=10
OUTPUT=--output-format="bbl"

ARGS=$(OUTPUT) $(ITERATIONS) $(INTERACTIVE)
COMMAND=$(PYTHON) $(TARGET) $(ARGS)

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
triv:
	$(COMMAND) --graph-data="tests/trivial.lp"
clique:
	$(COMMAND) --graph-data="tests/cliques.lp"
single:
	$(COMMAND) --graph-data="tests/singlenode.lp"
bip:
	$(COMMAND) --graph-data="tests/bipartite.lp"

clear:
	rm */*.pyc

tar:
	cd .. && tar acf tarball.tar.gz asprgc/
zip:
	cd .. && zip -r tarball.zip asprgc/
tarasp:
	tar acvf ASPsources.tar.gz asprgc/ASPsources/

cytoscape:
	$(CYTOSCAPE)
show:
	$(CYTOSCAPE) -N data/output.nnf
