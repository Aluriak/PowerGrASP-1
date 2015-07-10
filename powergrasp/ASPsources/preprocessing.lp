%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Perform pre-processing of the data at each steps.
%  outputs atoms will be the input of next ASP programs.
%
% initial version:  08/07/2014   L. Bourneuf
%
% Input:
%       - ccedge(cc,X,Y): there exists an edge between X and Y in the
%                         subgraph corresponding to connected component cc
%       - membercc(cc,Y): Y is a member of cc, but not its root.
%       - covered(X,Y): edge(X,Y) is already covered.
%       - lowbound: exits iff the maxlowerbound must be computed
% Output:
%       - oedge(X,Y): there exits a usable edge between X and Y with X<Y
%       - membercc(Y): Y is a member of cc, and is used by oedge
%       - maxlowerbound(S): the maximal score lower bound is S
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#program preprocessing(cc).

% get oriented edges of the connected component that are not covered
oedge(X,Y):- ccedge(cc,X,Y) ; X<Y ; not covered(X,Y).
oedge(X,Y):- ccedge(cc,Y,X) ; X<Y ; not covered(X,Y).

% node describes really used nodes
membercc(X):- membercc(cc,X) ; oedge(X,_).
membercc(X):- membercc(cc,X) ; oedge(_,X).

% compute the output degree of each node
%   (output degree == number of links to higher nodes that are in the same block)
degree(X,D,b(K,B)):- lowerbound ; oedge(X,_) ; block(K,B,Anonymous) ;
                     D=#count{r(Y): oedge(X,Y), block(K,B,Y)}.

% maximize the node score
maxlowerbound(S):- S=#max{D:degree(_,D,b(_,_))} ; lowerbound.

% outputs preprocessed data
#show.
#show oedge/2.
#show maxlowerbound/1.
#show membercc/1.
