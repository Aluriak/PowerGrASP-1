PYTHON=python2


py:
	$(PYTHON) asprgc/__main__.py --graph-data="data/diamond.lp"

clear:
	rm */*.pyc
