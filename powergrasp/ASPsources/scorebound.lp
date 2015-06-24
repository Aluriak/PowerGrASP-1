%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Computation of the maximal lower bound.
%
% initial version:  23/06/2015   J. Nicolas
%
% Input:
%       - ccedge(cc,X,Y): there exists an edge between X and Y in the graph cc.
%       - covered(X,Y): edge(X,Y) is covered by a concept.
% Output:
%       - maxlowerbound(S): maximal lower bound admissible in non-covered graph.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#program scorebound(cc).

% get oriented edges of the connected component that are not covered
oedge(X,Y):- ccedge(cc,X,Y) ; X<Y ; not covered(X,Y).
oedge(X,Y):- ccedge(cc,Y,X) ; X<Y ; not covered(X,Y).

% compute the output degree of each node
%   (output degree == number of links to higher nodes)
degree(X,D):- oedge(X,_) ; D=#count{r(Y):oedge(X,Y)}.
%degree(X,0):- not oedge(X,_) ; oedge(_,X).

% maxmize the node score
%#maximize{S@1,S:degree(X,S)}.
maxlowerbound(S):- S=#max{D:degree(X,D)}.

#show degree/2.
#show maxlowerbound/1.
%#show ccedge/3.
