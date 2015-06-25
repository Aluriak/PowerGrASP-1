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

%#show degree/3.
%#show block/3.
#show maxlowerbound/1.
