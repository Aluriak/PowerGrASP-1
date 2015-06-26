%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Computation of the score bound for quick discarding of
%  uninteresting models.
%
% The maximal lower bound is equals to the maximal number of nodes
%  in the same block that are linked to a node.
%
% initial version:  23/06/2015   L. Bourneuf
%
% Input:
%       - ccedge(cc,X,Y): there exists an edge between X and Y in the graph cc.
%       - covered(X,Y): edge(X,Y) is covered by a concept.
%       - block(K,B,X): element X is in block B at step K.
% Output:
%       - maxlowerbound(S): maximal lower bound admissible in non-covered graph.
%       - upperbound(X,S): concept with minobj X have a maximal coverage of S.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#program scorebound(cc).

% get oriented edges of the connected component that are not covered
oedge(X,Y):- ccedge(cc,X,Y) ; X<Y ; not covered(X,Y).
oedge(X,Y):- ccedge(cc,Y,X) ; X<Y ; not covered(X,Y).

% compute the output degree of each node
%   (output degree == number of links to higher nodes that are in the same block)
degree(X,D,b(K,B)):- oedge(X,_) ; block(K,B,Anonymous) ;
                     D=#count{r(Y): oedge(X,Y), block(K,B,Y)}.

% maximize the node score
maxlowerbound(S):- S=#max{D:degree(_,D,b(_,_))}.

% maximal surface of each node
degree(X,D):- oedge(X,_) ; D=#count{r(Y): oedge(X,Y)}.
min_neighbor_degree(X,S):- S=#min{D:degree(Y,D), oedge(X,Y)} ; oedge(X,_) ; S!=#sup ; S!=#inf.
upperbound(X,N1*N2):- degree(X,N1) ; min_neighbor_degree(X,N2).

%#show degree/3.
%#show block/3.
%#show min_neighbor_degree/2.
#show maxlowerbound/1.
#show upperbound/2.
