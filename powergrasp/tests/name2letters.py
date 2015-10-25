# -*- coding: utf-8 -*-

from __future__ import print_function
import sys
import re
from collections import defaultdict

with open(sys.argv[1], "r") as fid, open(sys.argv[2], "w") as fod:
    ids = (chr(_) for _ in range(ord('a'), ord('z')+1))
    names = defaultdict(lambda: next(ids))  # protein name:id
    reg = re.compile('''edge\("([^"]*)","([^"]*)"\).''')
    for line in fid:
        match = reg.match(line)
        if match:
            proteinA, proteinB = match.groups()
            assert(proteinA.__class__ is str)
            fod.write('''edge({0},{1}).\n'''.format(
                names[proteinA], names[proteinB]
            ))



