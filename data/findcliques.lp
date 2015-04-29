%*
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
Find maximal cliques 
in the incidence matrix of a simple non oriented graph 
  initial version:  09/12/2014   J. Nicolas 

Input:
        - node(X): X is a graph node;
        - edge(X,Y):  there exists an edge between X and Y in the graph (all edges are symmetric).
        - inter(X,Y): there exists an edge between X and Y in the graph (all edges are symmetric).
        - oedge(X,Y): there exists an edge between X and Y in the graph and edge is oriented X<Y.
        - membercc(cc,X): X belongs to cc
Output:
        - newedgecoverc(cc,N): score (edge covering) by the clique cc
        - newclique(cc,X): X belongs to clique cc
        - clique3(X): cc is a clique of 3 elements
*%

#program findcliques(cc).


clique3(cc):- oedge(cc,X,Y); oedge(cc,Y,Z); oedge(cc,X,Z).

%Choice of a  clique of at least 3 elements
3{newclique(cc,X): membercc(cc,X)}:- clique3(cc).
 
%consistency of the clique
:- newclique(cc,X); newclique(cc,Y); X<Y; not oedge(cc,X,Y).

%maximality of the clique
:-  membercc(cc,X); not newclique(cc,X); inter(X,Y):newclique(cc,Y); clique3(cc).

newedgecoverc(cc,(N*(N-1))/2):- N={newclique(cc,X):membercc(cc,X)}; clique3(cc).

#show clique3/1.
#show newclique/2.
#show newedgecoverc/2.
%#show oedge/3.
%#show membercc/2.
%#show node/1.


