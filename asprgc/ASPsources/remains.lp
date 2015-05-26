%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Find all edges that are not covered,
%  and produce them as remaining edges.
%
% initial version:  10/05/2014   L. Bourneuf
%
% Input:
%       - covered(X,Y):- edge X to Y was covered.
%       - ccedge(_,X,Y): there exists an edge between X and Y in the graph.
% Output:
%       - remain(X,Y):- edge X to Y can't be covered.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#program remains.

oedge(X,Y):- ccedge(_,X,Y) ; X<Y.
oedge(X,Y):- ccedge(_,Y,X) ; X<Y.
edge(X,Y):- oedge(X,Y) ; not covered(X,Y).

#show edge/2.
%#show ccedge/3.
%#show oedge/2.
%#show covered/2.

