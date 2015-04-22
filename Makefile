PYTHON=python2


py:
	$(PYTHON) asprgc/__main__.py --graph-data="data/diamond.lp" --iterations=10

clear:
	rm */*.pyc
