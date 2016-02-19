%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Perform pre-processing of the data at each steps.
%  outputs atoms will be the input of next ASP programs.
%
% initial version:  08/07/2014   L. Bourneuf
%
% Constants:
%       - cc: treated connected component. (cc/1 gives existing cc)
%
% Input:
%       - ccedge(cc,X,Y): there exists an edge between X and Y in the
%                         subgraph corresponding to connected component cc
%       - membercc(cc,Y): Y is a member of cc, but not its root.
%       - covered(X,Y): edge(X,Y) is already covered.
%       - lowbound: exits iff the maxlowerbound must be computed
%       - include_block(k,B,p(cc,k,T)): block B contains set T of newconcept.
%       - block(k,B,X): block B contains X.
%       - include_powernode(cc,K1,T1,K2,T2): powernode K1,T1 contains K2,T2.
%       - equiv(X,Y): any time X is compressed, Y should be too. neighbor(X) == neighbor(Y)
% Output:
%       - oedge(X,Y): there exits a usable edge between X and Y with X<Y
%       - membercc(Y): Y is a member of cc, and is used by oedge
%       - maxlowerbound(S): the maximal score lower bound is S
%       - degree(X,D): node X have a degree of D (=there is D nodes linked to X)
%       - equiv(X,Y): any time X is compressed, Y should be too. neighbor(X) == neighbor(Y)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


% get oriented edges of the connected component that are not covered
oedge(X,Y):- ccedge(cc,X,Y) ; X<Y ; not covered(X,Y).
oedge(X,Y):- ccedge(cc,Y,X) ; X<Y ; not covered(X,Y).

% Symetric and non-oriented edges
inter(X,Y):- oedge(X,Y).
inter(Y,X):- oedge(X,Y).

% node describes really used nodes
membercc(X):- membercc(cc,X) ; oedge(X,_).
membercc(X):- membercc(cc,X) ; oedge(_,X).


% outputs preprocessed data
#show.
#show oedge/2.
#show membercc/1.
#show inter/2.
#show equiv(X,Y): equiv(X,Y), membercc(X).
