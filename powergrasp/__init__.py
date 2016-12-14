"""PowerGrASP is a package implementing graph compression methods.

You can found the official repository at http://powergrasp.bourneuf.net

High level API is described in the recipes module,
where compression algorithms are implemented.

See also the config module where the Configuration object, allowing one to
precisely define the compression parameters, is implemented.

The CLI also provide a good starting point, allowing one to play directly
with graphs without having to code anything.

"""

from powergrasp import info
from powergrasp import motif
from powergrasp import recipes
from powergrasp import observers
from powergrasp.graph import Graph
from powergrasp.config import Configuration
Config = Configuration  # simple alias
from powergrasp.plotting import plots
