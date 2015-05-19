%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Update the set of edges contained by the concept of current step,
%  in order to exclude all edges covered by the chosen powernode
%
% initial version:  09/12/2014   J. Nicolas
% revised version:  06/05/2014   L. Bourneuf
%
% Input:
%       - covered(X,Y):- edge X to Y was covered.
%       - ccedge(_,X,Y): there exists an edge between X and Y in the graph.
% Output:
%       - remain(X,Y):- edge X to Y can't be covered.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#program remains.

covered(X,Y):- covered(Y,X).
edge(X,Y):- ccedge(C,X,Y) ; not covered(X,Y).

#show edge/2.

