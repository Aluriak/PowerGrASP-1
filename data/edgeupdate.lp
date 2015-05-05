%*
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
Choose a clique or biclique of maximal edgecover (power node/edge)
and update the set of remaining cliques and bicliques
in order to exclude all edges covered by the chosen power edge
initial version:  09/12/2014   J. Nicolas

Input:
        - concept(cc,k,T,X):- X belongs to set T of cc at step k.
        - clique(cc,k,X):- X belongs to clique cc at step k.
        - edgecover(cc,k,N):- concept cc at step k has a score of N.
Output:
        - powernode(cc,k,N):- powernode cc at step k has a score of N.
        - bcovered(cc,k,X,Y):- edge X to Y is covered by powernode cc at step k.
        - covered(X,Y):- edge X to Y was covered.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
*%

#program edgeupdate(cc,k).

% Uses program parameters
concomp(cc).
step(k).
%any_step(0..k). % unused


% oedgeb are (oriented) edges of the concepts that links two nodes of different sets.
% oedgeb are also the edges covered by the better concept.
oedgeb(cc,k,X,Y):- concept(cc,k,T,X) ; concept(cc,k,3-T,Y), X<Y; T=1..2 ; step(k) ; concomp(cc).
%#show oedgeb/4.
% oedgec are (oriented) edges of the clique that links two nodes.
oedgec(cc,k,X,Y):- clique(cc,k,X) ; clique(cc,k,Y) ; X<Y ; step(k) ; concomp(cc).

% Concept with maximal edgecover and smallest id at step k
powernode(cc,k,N):- edgecover(cc,k,N); concomp(cc).
#show  powernode/3.

% (Oriented) Edges of the best concept at step k
bestedge(cc,k,X,Y):- powernode(cc,k,N) ; oedgeb(cc,k,X,Y).
bestedge(cc,k,X,Y):- powernode(cc,k,N) ; oedgec(cc,k,X,Y).
%bestedge(cc,X,Y):- powernode(cc,N); oedgec(cc,X,Y).
bcovered(cc,k,X,Y):- bestedge(cc,k,X,Y).
 covered(     X,Y):- bestedge(cc,k,X,Y).
:- bcovered(A1,A2,X,Y) ; X>Y.

#show bcovered/4.
#show  covered/2.
