%*
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
Rewritting of powercomp4.lp by Lucas Bourneuf,
without special treatment of bipartite case.

Extract the connected components of the graph
Input:
  	- edge(X,Y): there exists an edge between X and Y in the graph.
Output:
        - connectedpath(X,Y): there exists a path from X to Y, X<Y.
        - cc(CC): CC is the minimal element of a connected component.
        - ccedge(CC,X,Y): there exists an edge between X and Y in CC.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
*%
#program extract.

%In nodes and Out nodes
%node(1,X):- edge(X,_). % anonymous variable generates bugs…
%node(2,Y):- edge(_,Y).
node(1,X):- edge(X,T).
node(2,Y):- edge(T,Y).

%All nodes 
node(X):- node(1..2,X).

%Symetric graph
inter(X,Y):- edge(X,Y). %xxx: used later
inter(X,Y):- edge(Y,X).

%Oriented graph
% an oriented edge go from smaller to bigger :
% oedge(3, 5) is true, oedge(5, 3) is false.
onode(1..2,X):- node(X).
oedge(X,Y)   :- edge(X,Y); X<Y.
oedge(X,Y)   :- edge(Y,X); X<Y. % edge(5,3) become oedge(3,5)

%Connected paths starting with minimal element X
% connected(Minimum element, 
%           Element connected to the minimum
%          )
connectedpath(X,Y):- oedge(X,Y).
connectedpath(X,Z):- connectedpath(X,Y); oedge(Y,Z); X<Z.
%xxx: should X<Z be set as a constraint ?
%:- connectedpath(X,Y) ; X>=Y.

connected(Y):- connectedpath(T,Y).

%Connected component of minimum element X
membercc(X,Y):- connectedpath(X,Y); not connected(X).
membercc(X,X):- connectedpath(X,T); not connected(X).
cc(CC):- membercc(CC,T).

nb(nodes,               N):- N=#count{node(X):node(X)}.
nb(connectedcomponents, N):- N=#count{  cc(X):node(X), not connected(X)}.

%edges of the connected components
ccedge(CC,X,Y):- membercc(CC,Y);  edge(X,Y).

%:- nb(X,Y) ; countable(X) ; amount(Y) ; Y=0. 
%{nb(X,Y): nb(X,Y)}.

#show cc/1.
#show ccedge/3.
#show membercc/2.
#show nb/2.
#show node/1.
#show inter/2.
#show connectedpath/2.
