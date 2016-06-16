%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Extraction of graph data from edge information.
%
% initial version:  09/12/2014   J. Nicolas
% revised version:  29/04/2014   L. Bourneuf
%
% Extract the connected components of the graph
% Input:
%       - edge(X,Y): there exists an edge between X and Y in the graph.
% Output (one model per connected component):
%       - cc(CC): CC is the minimal element of the connected component.
%       - membercc(X): node X belongs to connected component.
%       - oedge(X,Y): there exists an oriented edge between X and Y.
%       - block(0,CC,X): X is in the block cc a step 0
%       - equiv(X,Y): X hides the node Y.
%       - weight(X,W): X hides W other nodes.
%       - nb_edge(N): there is N edges in the connected component.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%% CONNECTED COMPONENTS SEARCH %%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Symetric graph
inter(X,Y):- edge(X,Y) ; X!=Y.
inter(X,Y):- inter(Y,X).

% Equivalent nodes: nodes having edges to the same others nodes
%  (same place in the concept lattice). Only the smaller is kept,
%  all the others will be automatically generated when necessary.
differ(X,Y):- inter(X,Z) ; not inter(Y,Z) ; inter(Y,_).
all_equiv(X,Y):-  inter(X,_) ; inter(Y,_) ; X<Y ; not differ(X,Y) ; not differ(Y,X).
equiv(X,Y):- all_equiv(X,Y) ; not hidden(X).

% Hidden nodes are nodes with an equivalent. Only the smaller one is kept, thus not hidden.
hidden(Y):- equiv(_,Y).

% Weight of a node is the number of node hidden by it, excluding itself.
% Weight atom is only generated for atoms that hides hidden nodes.
weight(X,W):- W={equiv(X,_)} ; equiv(X,_) ; not hidden(X).

% Connected paths starting with minimal element X
% connected(Minimum element,Element connected to the minimum)
connectedpath(X,Y):- inter(X,Y) ; X<Y.
connectedpath(X,Z):- connectedpath(X,Y) ; inter(Y,Z) ; X<Z.

% In a connected component, the root is the smaller element.
cc_root(X):- not connectedpath(_,X) ; connectedpath(X,_).

% Edges, oriented and related to their connected component.
ccedge(CC,X,Y):- inter(X,Y) ; X<Y ; cc_root(CC) ; connectedpath(CC,X).
ccedge(CC,CC,Y):- inter(CC,Y) ; cc_root(CC).

% Connected components are identified by their smaller element.
% Choose them, on by one.
1{ cc(X): cc_root(X) }1.


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%% CONNECTED COMPONENTS YIELDING %%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Are members of the cc all nodes linked to the smaller element, this last included.
membercc(X):- cc(CC) ; connectedpath(CC,X).
membercc(CC):- cc(CC).

% Oriented graph between non hidden nodes.
% an oriented edge go from smaller to bigger :
% oedge(3, 5) is possible, but oedge(5, 3) is not.
oedge(X,Y):- ccedge(CC,X,Y) ; cc(CC).

% initial ccstate of blocks : each node is in its cc
block(0,CC,X):- membercc(X) ; cc(CC).

% Count of edges in the connected component.
nb_edge(N):- N={ccedge(CC,X,Y)} ; cc(CC).

% Count of node in the graph.
ccnode(CC,X):- cc(CC) ; connectedpath(CC,X).
ccnode(CC,CC):- cc(CC).
nb_node(N):- N={ccnode(CC,X)} ; cc(CC).
#show nb_node/1.

% outputs
#show cc/1.
#show membercc(X): membercc(X), not hidden(X).
#show block(A,B,X): block(A,B,X), not hidden(X).
#show oedge(X,Y): oedge(X,Y), membercc(X), not hidden(X), not hidden(Y).
#show weight(X,W): weight(X,W), membercc(X).
#show equiv(X,Y): equiv(X,Y), membercc(X).
#show nb_edge/1.
#show nb_cc(N): N={node(X): node(X), not connectedpath(_,X), connectedpath(X,_)}.
