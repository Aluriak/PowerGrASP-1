%*
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
Choose a clique or biclique of maximal edgecover (power node/edge)
and update the set of remaining cliques and bicliques
in order to exclude all edges covered by the chosen power edge
initial version:  09/12/2014   J. Nicolas

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
*%

#program edgeupdate(cc,k).

% Uses program parameters
concomp(cc).
step(k).
any_step(0..k).


% NB: concept(CC,Step,NumModel,NumSet,Element)
%id(cc,k,b(I)):- concept(cc,k,I,Anonymous,Anonymous2).
%id(cc,k,c(I)):- clique(cc,k,I,Anonymous).
%id(cc,k):- id(cc,k,Anonymous).
%:- step(k); not id(cc,k);  step(k); concomp(cc).
%#show update(cc,k,next_k).
%#show id/2.
%#show id/3.
%#show concept/5.

% oedgb are (oriented) edges of the concepts that links two nodes of different sets
oedgeb(cc,k,X,Y):- concept(cc,k,T,X),concept(cc,k,3-T,Y), X<Y; T=1..2 ; step(k).
#show oedgeb/4.

%oedgc are oriented edges of the clique, oedgec2 is the symmetric relation
%oedgec(cc,X,Y):- clique(cc,X); clique(cc,Y); X<Y.
%oedgec2(cc,X,Y):- oedgec(cc,X,Y).
%oedgec2(cc,X,Y):- oedgec(cc,Y,X).
%#show oedgec/3.
%#show oedgec2/3.


% Concept with maximal edgecover and smallest id at step k
powernode(cc,k,N):- edgecover(cc,k,N); concomp(cc).
#show  powernode/3.

% (Oriented) Edges of the best concept at step k
bestedge(cc,k,X,Y):- powernode(cc,k,N); oedgeb(cc,k,X,Y).
%bestedge(cc,X,Y):- powernode(cc,N); oedgec(cc,X,Y).
bcovered(cc,k,X,Y):- bestedge(cc,k,X,Y).
 covered(     X,Y):- bestedge(cc,k,X,Y).
:- bcovered(A1,A2,X,Y) ; X>Y.

#show bcovered/4.
#show  covered/2.
