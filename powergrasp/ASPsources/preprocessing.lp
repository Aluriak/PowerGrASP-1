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
%       - include_block(k,B,p(cc,k,T)): block B contains set T of newconcept.
%       - block(k,B,X): block B contains X.
%       - include_powernode(cc,K1,T1,K2,T2): powernode K1,T1 contains K2,T2.
%       - equiv(X,Y): any time X is compressed, Y should be too. neighbor(X) == neighbor(Y)
%       - weight(X,W): node X hides W-1 nodes.
% Output:
%       - block(k,B,X): block B contains X.
%       - inter(X,Y): there exits an edge between X and Y
%       - membercc(Y): Y is a member of cc, and is connected to at least one other node
%       - equiv(X,Y): any time X is compressed, Y should be too. neighbor(X) == neighbor(Y)
%       - weight(X,W): node X hides W-1 nodes.
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


% Outputs preprocessed data.
#show.
#show inter/2.
#show membercc/1.
#show equiv(X,Y): equiv(X,Y), membercc(X).
%#show weight(X,W): weight(X,W), membercc(X).
