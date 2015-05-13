PYTHON=python2
CYTOSCAPE=~/bin/cytoscape-2.8.3/cytoscape.sh

TARGET=asprgc/__main__.py
#INTERACTIVE=--interactive=True
ITERATIONS=--iterations=10
OUTPUT=--output-format="bbl"

ARGS=$(OUTPUT) $(ITERATIONS) $(INTERACTIVE)
COMMAND=$(PYTHON) $(TARGET) $(ARGS)

diam:
	$(COMMAND) --graph-data="tests/diamond.lp"
ddiam:
	$(COMMAND) --graph-data="tests/double_biclique.lp"
three:
	$(COMMAND) --graph-data="tests/threenode.lp"
prot:
	$(COMMAND) --graph-data="tests/proteome_yeast_1.lp"
clique:
	$(COMMAND) --graph-data="tests/cliques.lp"
single:
	$(COMMAND) --graph-data="tests/singlenode.lp"

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
