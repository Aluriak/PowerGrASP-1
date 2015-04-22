%*
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
Rewritting of powercomp4.lp by Lucas Bourneuf,
without special treatment of bipartite case.

Find concepts 
in the incidence matrix of a simple non oriented graph 
Input:
	- ccedge(cc,X,Y): there exists an edge between X and Y in the 
                          subgraph corresponding to connected component cc
        - connectedpath(CC,Y): there exists a path in CC to Y
                               (Y belongs to CC)
        - membercc(cc,Y): Y is a member of cc, but not its root.
Output:
        - ?
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
*%
#program findconcept(cc).

% If N node in cc, cc!=Y will be true "N-1 times"
nonsingletoncc(cc):- membercc(cc,Y); cc!=Y.

% Sorted with respect to the smallest set 
onode(cc,1,X):- membercc(cc,X). % X belongs to CC
onode(cc,2,X):- ccedge(cc,X,A). % X is not a terminal node
oedge(cc,X,Y):- ccedge(cc,X,Y); X<Y. % oedge(5,3) become oedge(3,5)
oedge(cc,Y,X):- ccedge(cc,X,Y); Y<X.
node(X):- onode(Anonymous1,Anonymous2,X).

% N1 elements in set1 and N2 elements in set2 
nbelements(cc,N1,N2):- N1=#count{membercc(cc,X):node(X)}; 
                       N2=#count{ onode(cc,2,Y):node(Y)}.


% Choice of a non empty concept

% Choice of the minimum of the concept
1{minobj(cc,X):membercc(cc,X)}1.
minobj(X):- minobj(Anonymous,X).
 

%Choice of elements in part 1
newconcept(cc,1,X):- minobj(cc,X).
{ newconcept(cc,1,X): membercc(cc,X),X>Min }:- minobj(cc,Min).
%Choice of elements in part 2
1 { newconcept(cc,2,Y):oedge(cc,Min,Y) } :- minobj(cc,Min).
 
%Check that the concepts of simple graphs are not included in a clique of size 3:
%There must exist two elements in a same part that are not related or the concept covers exactly one edge.
nonclique(cc):- newconcept(cc,T,X) ; newconcept(cc,T,Y) ; X<Y ; not oedge(cc,X,Y).
nonclique(cc):- 2{newconcept(cc,T,X)}2.
:- not nonclique(cc).

%impossible element in a concept
% a node is impossible if not linked to all nodes of other part
imp(cc,3-I,X):- membercc(cc,X); newconcept(cc,I,Y); not ccedge(cc,X,Y); not ccedge(cc,Y,X).

% consistency ; no impossible element can  be added to the concept
:- imp(cc,I,Y); newconcept(cc,I,Y).

% maximality  ; all possible elements have to be added to the concept
:- not imp(cc,I,X); not newconcept(cc,I,X); I=1..2; onode(cc,I,X).

% Biclique (Concept) edge cover
newedgecoverb(cc,N1*N2):- N1={newconcept(cc,1,X)} ; N2={newconcept(cc,2,Y)}.
nb(concept1,N):- N={newconcept(cc,1,X)}.
nb(concept2,N):- N={newconcept(cc,2,X)}.
nb_explicit(concept1,N):- N=#count{1,X:newconcept(cc,1,X)}.
nb_explicit(concept2,N):- N=#count{1,X:newconcept(cc,2,X)}.


cardinal(cc,T,N1):- N1={newconcept(cc,T,X)} ; T=1..2.
% maximize cardinal values
#maximize{N1*N2@1,N1,N2:cardinal(cc,1,N1),cardinal(cc,2,N2)}.



#show cardinal/3.
#show newconcept/3.
%#show nbelements/1.
%#show nbelements/2.
#show imp/3.
#show minobj/2.
%#show ccedge/3.
#show oedge/3.
#show nb/2.
#show nb_explicit/2.
#show newedgecoverb/2.
