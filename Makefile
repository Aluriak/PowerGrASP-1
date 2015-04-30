PYTHON=python2

diam:
	$(PYTHON) asprgc/__main__.py --graph-data="data/diamond.lp" --iterations=10
ddia:
	$(PYTHON) asprgc/__main__.py --graph-data="data/diamond2.lp" --iterations=10
mix:
	$(PYTHON) asprgc/__main__.py --graph-data="data/diamix.lp" --iterations=10
prot:
	$(PYTHON) asprgc/__main__.py --graph-data="data/proteome_yeast_1.lp" --iterations=10

clear:
	rm */*.pyc
