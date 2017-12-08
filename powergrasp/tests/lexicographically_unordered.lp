% This example show nodes that are not lexicographically ordered (numbers),
% so that the compression is lost because of edges non-recognition.
% This case is handled by a warning since 553b630a511d69


% DO NOT SHOW THE PROBLEM
% (i can't reproduce it…)

edge((10;20),(11;21)).
edge((1;20),(21;2)).
