%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Extraction of graph data from edge information.
%
% initial version:  09/12/2014   J. Nicolas
% revised version:  29/04/2014   L. Bourneuf
%
% Extract the connected components of the graph
% Input:
%       - edge(X,Y): there exists an edge between X and Y in the graph.
% Output:
%       - cc(CC): CC is the minimal element of a connected component.
%       - membercc(X,Y): there exists a path from X to Y, X<Y.
%       - ccedge(CC,X,Y): there exists an edge between X and Y in CC.
%       - block(0,CC,X): X is in the block cc a step 0
%       - equiv(X,Y): any time X is compressed, Y should be too. neighbor(X) == neighbor(Y)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


% Symetric graph
inter(X,Y):- edge(X,Y).
inter(X,Y):- edge(Y,X).

% Equivalent nodes: nodes having edges to the same others nodes
%  (same place in the concept lattice). Only the smaller is kept,
%  all the others will be automatically generated when necessary.
%differ(X,Y):- inter(X,Z); not inter(Y,Z) ; inter(Y,_).
%equiv(X,Y):-  inter(X,_) ; inter(Y,_) ; X<Y ;  not differ(X,Y) ;  not differ(Y,X) ; not equiv(_,X).

%% Hidden nodes are nodes with an equivalent. Only the smaller one is kept, thus not hidden.
%hidden(Y):- equiv(_,Y).

%% weight of a node is the number of node hidden by it, including itself
%weight(X,W+1):- W={equiv(X,_)} ; equiv(X,_) ; not hidden(X).
%weight(X,1):- not equiv(X,_) ; not hidden(X) ; membercc(_,X).

% Oriented graph
% an oriented edge go from smaller to bigger :
% oedge(3, 5) is true, oedge(5, 3) is false.
oedge(X,Y):- edge(X,Y) ; X<Y ; not hidden(X) ; not hidden(Y).
oedge(X,Y):- edge(Y,X) ; X<Y ; not hidden(X) ; not hidden(Y).

% Connected paths starting with minimal element X
% connected(Minimum element,Element connected to the minimum)
connectedpath(X,Y):- oedge(X,Y).
connectedpath(X,Z):- connectedpath(X,Y) ; inter(Y,Z) ; X<Z.

connected(Y):- connectedpath(_,Y).

% Connected component of minimum element X
membercc(X,Y):- connectedpath(X,Y) ; not connected(X) ; not hidden(Y).
membercc(X,X):- connectedpath(X,_) ; not connected(X).
cc(CC):- membercc(CC,T).

%edges of the connected components
ccedge(CC,X,Y):- membercc(CC,Y) ;  edge(X,Y) ; not hidden(X) ; not hidden(Y).

% initial ccstate of blocks : each node is in its cc
block(0,CC,X):- membercc(CC,X).

% total count of edges in the graph (including those hidden)
nb_edge(N):- N=#count{1,X,Y:edge(X,Y)}.

% outputs
#show cc/1.
#show membercc/2.
%#show inter/2.
#show block/3.
#show ccedge/3.
#show nb_edge/1.
%#show weight/2.
%#show equiv(X,Y): equiv(X,Y), not hidden(X).
