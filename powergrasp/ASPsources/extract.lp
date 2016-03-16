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

% Node access.
node(X):- inter(X,_).

% Oriented graph
% an oriented edge go from smaller to bigger :
% oedge(3, 5) is true, oedge(5, 3) is false.
oedge(X,Y):- inter(X,Y) ; X<Y ; not hidden(X) ; not hidden(Y).

% Equivalent nodes: nodes having edges to the same others nodes
%  (same place in the concept lattice). Only the smaller is kept,
%  all the others will be automatically generated when necessary.
differ(X,Y):- inter(X,Z); not inter(Y,Z) ; inter(Y,_).
equiv(X,Y):-  inter(X,_) ; inter(Y,_) ; X<Y ;  not differ(X,Y) ;  not differ(Y,X) ; not equiv(_,X).

% Hidden nodes are nodes with an equivalent. Only the smaller one is kept, thus not hidden.
hidden(Y):- equiv(_,Y).

% Weight of a node is the number of node hidden by it, excluding itself.
% Weight atom is only generated for atoms that hides hidden nodes.
weight(X,W):- W={equiv(X,_)} ; equiv(X,_) ; not hidden(X).

% Connected paths starting with minimal element X
% connected(Minimum element,Element connected to the minimum)
connectedpath(X,Y):- oedge(X,Y).
connectedpath(X,Z):- connectedpath(X,Y) ; inter(Y,Z) ; X<Z.

% Connected components are identified by their smaller element.
% Choose them, on by one.
1{ cc(X): node(X) , not connectedpath(_,X), connectedpath(X,_) }1.


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%% CONNECTED COMPONENTS YIELDING %%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Are members of the cc all nodes linked to the smaller element, this last included.
membercc(X):- cc(CC) ; node(X) ; connectedpath(CC,X).
membercc(CC):- cc(CC).

% initial ccstate of blocks : each node is in its cc
block(0,CC,X):- membercc(X) ; cc(CC).

% node in cc, including hidden ones.
cc_node(X):- membercc(X).
cc_node(Y):- membercc(X) ; equiv(X,Y).

% Count of edges.
nb_edge(N/2):- N={inter(X,_): cc_node(X)}.

% outputs
#show cc/1.
#show membercc/1.
#show block/3.
#show oedge(X,Y): oedge(X,Y), membercc(X).
#show weight(X,W): weight(X,W), membercc(X).
#show equiv(X,Y): equiv(X,Y), not hidden(X), membercc(X).
#show nb_edge/1.
#show nb_cc(N): N={node(X): node(X), not connectedpath(_,X), connectedpath(X,_)}.
