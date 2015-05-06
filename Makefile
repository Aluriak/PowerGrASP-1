PYTHON=python2

diam:
	$(PYTHON) asprgc/__main__.py --graph-data="tests/diamond.lp" --iterations=10
ddiam:
	$(PYTHON) asprgc/__main__.py --graph-data="tests/double_biclique.lp" --iterations=10
three:
	$(PYTHON) asprgc/__main__.py --graph-data="tests/threenode.lp" --iterations=10
prot:
	$(PYTHON) asprgc/__main__.py --graph-data="tests/proteome_yeast_1.lp" --iterations=10
clique:
	$(PYTHON) asprgc/__main__.py --graph-data="tests/cliques.lp" --iterations=10
single:
	$(PYTHON) asprgc/__main__.py --graph-data="tests/singlenode.lp" --iterations=10

clear:
	rm */*.pyc


tar:
	cd .. && tar acf tarball.tar.gz asprgc/
zip:
	cd .. && zip -r tarball.zip asprgc/ 
