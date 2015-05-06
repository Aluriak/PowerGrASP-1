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


% Are covered all edges of concept that link two nodes of different set.
bcovered(cc,k,X,Y):- concept(cc,k,T,X) ; concept(cc,k,3-T,Y), X<=Y; T=1..2 ; step(k) ; concomp(cc).
:- bcovered(A1,A2,X,Y) ; X>Y.

% Concept with maximal edgecover and smallest id at step k
#show powernode(cc,k,T,X): concept(cc,k,T,X).

% New edges covered by powernode
covered(     X,Y):- bcovered(cc,k,X,Y).

#show bcovered/4.
#show  covered/2.
