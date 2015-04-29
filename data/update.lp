%*
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
Choose a clique or biclique of maximal edgecover (power node/edge)
and update the set of remaining cliques and bicliques
in order to exclude all edges covered by the chosen power edge
  initial version:  09/12/2014   J. Nicolas 

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
*%
 
#program update(cc,k,next_k).

% Uses program parameters
concomp(cc).
step(k).
next_step(next_k).


% NB: concept(CC,Step,NumModel,NumSet,Element)
id(cc,k,b(I)):- concept(cc,k,I,Anonymous,Anonymous2).
id(cc,k,c(I)):- clique(cc,k,I,Anonymous).
id(cc,k):- id(cc,k,Anonymous).
:- step(k); not id(cc,k);  step(k); concomp(cc).
#show update(cc,k,next_k).
#show id/2.
#show id/3.
#show concept/5.

%oedgb are (oriented) edges of the concepts
oedgeb(cc,k,I,X,Y):- concept(cc,k,I,T,X),concept(cc,k,I,3-T,Y), X<Y; T=1..2.
#show oedgeb/5.

%oedgc are oriented edges of the clique, oedgec2 is the symmetric relation
oedgec(cc,k,I,X,Y):- clique(cc,k,I,X); clique(cc,k,I,Y); X<Y.
oedgec2(cc,k,X,Y):- oedgec(cc,k,Anonymous,X,Y).
oedgec2(cc,k,X,Y):- oedgec(cc,k,Anonymous,Y,X).
#show oedgec/5.
#show oedgec2/4.


% Concept with maximal edgecover and smallest id at step k
powernode(cc,k,I):- edgecover(cc,k,I,N); not edgecover(cc,k,J,N):id(cc,k,J),J<I; not edgecover(cc,k,K,M):edgecover(cc,k,K,M),M>N; concomp(cc).
bpowernode(cc,k):- powernode(cc,k,b(I)).
cpowernode(cc,k):- powernode(cc,k,c(I)).
#show  powernode/3.
#show bpowernode/2.
#show cpowernode/2.

% (Oriented) Edges of the best concept at step k 
bestedge(cc,k,X,Y):- powernode(cc,k,b(I)); oedgeb(cc,k,I,X,Y).
bestedge(cc,k,X,Y):- powernode(cc,k,c(I)); oedgec(cc,k,I,X,Y).
#show bestedge/4.

% an edge is covered if in bestedge of cc
coverededge(cc,k,X,Y):- bestedge(cc,k,X,Y).
#show coverededge/4.

%%Concepts and cliques to be updated if they have an edge in common with the best concept
%tobeupdated(cc,k,b(J)):- oedgeb(cc,k,J,X,Y); bestedge(cc,k,X,Y); not powernode(cc,k,b(J)); step(k).
%tobeupdated(cc,k,c(J)):- oedgec(cc,k,J,X,Y); bestedge(cc,k,X,Y); not powernode(cc,k,c(J)); step(k).
%#show tobeupdated/3.

%remain(cc,k,BC):-id(cc,k,BC); not tobeupdated(cc,k,BC); not powernode(cc,k,BC).

%%At most two concepts (one for each axis)  may derive from the difference between a concept and the powernode
%%Moreover, all concepts included in a clique are discarded
%newconcept(cc,next_k,b(I,T),T,X):- tobeupdated(cc,k,b(I)); concept(cc,k,I,T,X); 
        %not bestedge(cc,k,X,Y):concept(cc,k,I,3-T,Y),X<Y; not bestedge(cc,k,Y,X):concept(cc,k,I,3-T,Y),Y<X; 
        %concept(cc,k,I,3-T,B);not oedgec2(cc,k,X,B); T=1..2;  concomp(cc) ; next_step(next_k).
%newconcept(cc,next_k,b(I,T),3-T,Y):- tobeupdated(cc,k,b(I)); concept(cc,k,I,3-T,Y); 
                                  %newconcept(cc,next_k,b(I,T),T,X); not oedgec2(cc,k,X,Y); 
                                  %concomp(cc) ; next_step(next_k).
%%Concepts that remain from one step to the next one
%newconcept(cc,next_k,b(I,1),T,X):- concept(cc,k,I,T,X); remain(cc,k,b(I)); concomp(cc) ; next_step(next_k).
%%#show concept(cc,next_k,b(I,1),T,X):newconcept(cc,next_k,b(I,1),T,X).


%% Biclique (Concept) edge cover
%newedgecover(cc,next_k,b(I,T),N1*N2):- N1={newconcept(cc,next_k,b(I,T),1,X):membercc(cc,X)}; 
                                    %N2={newconcept(cc,next_k,b(I,T),2,X):membercc(cc,X)}; 
                                    %tobeupdated(cc,k,b(I)); N1>0; N2>0; T=1..2; concomp(cc) ; next_step(next_k).
%newedgecover(cc,next_k,b(I,1),N):- remain(cc,k,b(I)); edgecover(cc,k,b(I),N); concomp(cc) ; next_step(next_k).
%%#show newedgecover/4.

%% Split of elements of a clique in two possibly overlapping cliques with respect to a biclique chosen as a powernode 
%% Either the element is not in a powernode and it must be kept or the element is in a same set of the poweredge
%bestnodeb(cc,k,T,X):- powernode(cc,k,b(J)); concept(cc,k,J,T,X).
%notbestnodeb(cc,k,X):- powernode(cc,k,b(J)); node(X); not concept(cc,k,J,1,X); not concept(cc,k,J,2,X).
%%#show bestnodeb/4.
%%#show notbestnodeb/3.

%splitcliqueb(cc,k,I,T,X):- bpowernode(cc,k); tobeupdated(cc,k,c(I)); clique(cc,k,I,X); notbestnodeb(cc,k,X); T=1..2.
%splitcliqueb(cc,k,I,T,X):- bpowernode(cc,k); tobeupdated(cc,k,c(I)); clique(cc,k,I,X); bestnodeb(cc,k,T,X); T=1..2.
%%A clique has to contain at least one edge
%admcliqueb(cc,k,I,T):- bpowernode(cc,k); id(cc,k,c(I)); T=1..2;   2{splitcliqueb(cc,k,I,T,X)}.
%%#show splitcliqueb/5.
%%#show admcliqueb/4.

%% Split of elements of a clique  with respect to a clique chosen as a powernode in a clique and a biclique
%bestnodec(cc,k,X):- powernode(cc,k,c(J)); clique(cc,k,J,X); step(k).
%splitcliquec(cc,k,I,X):- cpowernode(cc,k); tobeupdated(cc,k,c(I)); clique(cc,k,I,X); not bestnodec(cc,k,X).
%%#show bestnodec/3.
%%#show splitcliquec/4.


%%At most one new concept  derives from the difference between a clique and the powernode
%newconcept(cc,next_k,b(c(I),1),1,X):- cpowernode(cc,k); tobeupdated(cc,k,c(I)); clique(cc,k,I,X); not bestnodec(cc,k,X); step(k); concomp(cc) ; next_step(next_k).
%is_newconcept(cc,next_k,b(c(I))):- cpowernode(cc,k); newconcept(cc,next_k,b(c(I),1),1,X) ; next_step(next_k).
%newconcept(cc,next_k,b(c(I),1),2,X):- is_newconcept(cc,next_k,b(c(I))); clique(cc,k,I,X); bestnodec(cc,k,X); step(k); concomp(cc) ; next_step(next_k).
%newedgecover(cc,next_k,b(c(I),1), N1*N2):- N1={newconcept(cc,next_k,b(c(I),1),1,X):node(X)}; 
                                        %N2={newconcept(cc,next_k,b(c(I),1),2,X):node(X)}; 
                                        %is_newconcept(cc,next_k,b(c(I))); concomp(cc) ; next_step(next_k).

%%At most two new cliques (one for each axis)  may derive from the difference between a clique and the powernode
%newclique(cc,next_k,c(I,T),X):-   admcliqueb(cc,k,I,T);  splitcliqueb(cc,k,I,T,X); step(k); concomp(cc) ; next_step(next_k).
%newclique(cc,next_k,c(I,1),X):- splitcliquec(cc,k,I,X); 2{splitcliquec(cc,k,I,A)}; step(k); concomp(cc) ; next_step(next_k).

%%Cliques that remain from one step to the next one
%newclique(cc,next_k,c(I,1),X):- remain(cc,k,c(I)); clique(cc,k,I,X); step(k); concomp(cc) ; next_step(next_k).

%% Clique edge cover
%newedgecover(cc,next_k,c(I,T),(N*(N-1))/2):- N={newclique(cc,next_k,c(I,T),X):node(X)};  
                                          %tobeupdated(cc,k,c(I)); T=1..2; N>1; concomp(cc) ; next_step(next_k).
%newedgecover(cc,next_k,c(I,1),N):- remain(cc,k,c(I)); edgecover(cc,k,c(I),N); concomp(cc) ; next_step(next_k).

%%#show newedgecover/4.
%%#show newclique/4.

%#show concept(cc,k,T,X): concept(cc,k,I,T,X); powernode(cc,k,b(I)); concomp(cc); step(k).
%#show clique(cc,k,X): clique(cc,k,I,X), powernode(cc,k,c(I)); concomp(cc); step(k).
%#show step(k).

%%#show powernode(cc,k,I): powernode(cc,k,I), step(k).
%%#show step/1.
%%#show next_step/1.
%%#show id(cc,k,I):id(cc,k,I); step(k).
%%#show concept(cc,k,I,T,X): concept(cc,k,I,T,X);  step(k). %; k=7..9.
%%#show oedgec2(cc,k,X,Y): oedgec2(cc,k,X,Y);  step(k). %; k=7..9.
%%#show remain(cc,k,X): remain(cc,k,X); step(k). %; k=7..9.
%%#show newconcept(cc,next_k,Y,Z,T): newconcept(cc,next_k,Y,Z,T); step(k); concomp(cc) ; next_step(next_k). %; k=7..9. 
%%#show newclique/4.
%%#show powernode(cc,k,I): powernode(cc,k,c(I)), step(k). %; k=7..9.
%%#show bpowernode/2.
%%#show splitcliqueb(cc,k,I,T,X): splitcliqueb(cc,k,I,T,X),  step(k). %; k=7..9.
%%#show splitcliquec(cc,k,I,X): splitcliquec(cc,k,I,X),  step(k). %; k=7..9.
%%#show bestnodeb(cc,k,I,X): bestnodeb(cc,k,I,X),  step(k). %; k=7..9.
%%#show bestnodec(cc,k,X): bestnodec(cc,k,X),  step(k). %; k=7..9.
%%#show notbestnodeb(cc,k,X): notbestnodeb(cc,k,X),  step(k). %; k=7..9.
%%#show admcliqueb(cc,k,I,X): admcliqueb(cc,k,I,X),  step(k). %; k=7..9.
%%#show clique(cc,k,I,X): clique(cc,k,I,X),  step(k). %; k=7..9.
%%#show tobeupdated/3.
%%#show bestedge(cc,k,X,Y):bestedge(cc,k,X,Y), step(k).
%%#show edgecover/4.
%%#show newedgecover(cc,next_k,I,N): newedgecover(cc,next_k,I,N); step(k); concomp(cc).
%%#show oedge/4.
