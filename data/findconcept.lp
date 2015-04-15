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
#program findconcepts(cc).

% X belongs to CC if there exists a path from CC to Y
membercc(CC,X):- connectedpath(CC,X).

% If N node in cc, cc!=Y will be true "N-1 times"
nonsingletoncc(cc):- membercc(cc,Y); cc!=Y.

% Sorted with respect to the smallest set 
onode(cc,1,X):- membercc(cc,X). % X belongs to CC
onode(cc,2,X):- ccedge(cc,X,_). % X is not a terminal node
oedge(cc,X,Y):- ccedge(cc,X,Y); X<Y. % oedge(5,3) become oedge(3,5)
oedge(cc,Y,X):- ccedge(cc,X,Y); Y<X.
node(X):- onode(_,_,X).

% N1 elements in set1 and N2 elements in set2 
nbelements(cc,N1,N2):- N1={membercc(cc,X)}; N2={onode(cc,2,Y)}.


% Choice of a non empty concept

% Choice of the minimum of the concept
1{minobj(cc,X):membercc(cc,X)}1.

minobj(X):- minobj(_,X).
 
 
%Choice of elements in part 1
 newconcept(cc,1,X):- minobj(cc,X).
{ newconcept(cc,1,X): membercc(cc,X),X>Min }:- minobj(cc,Min).
%Choice of elements in part 2
1 { newconcept(cc,2,Y):oedge(cc,Min,Y) } :- minobj(cc,Min).
 
%Check that the concepts of simple graphs are not included in a clique of size 3:
%There must exist two elements in a same part that are not related or the concept covers exactly one edge.
nonclique(cc):- newconcept(cc,T,X);newconcept(cc,T,Y); X<Y; not oedge(cc,X,Y).
nonclique(cc):- 2{newconcept(cc,T,X)}2.

%impossible element in a concept
imp(cc,3-I,X) :- membercc(cc,X); newconcept(cc,I,Y); not ccedge(cc,X,Y); not ccedge(cc,Y,X).
imp(cc,1,X) :- membercc(cc,X); onode(cc, 1,X); newconcept(cc,2,Y); not oedge(cc,X,Y).

% consistency ; no impossible element can  be added to the concept
:- imp(cc,I,Y); newconcept(cc,I,Y).

% maximality ; all possible elements have to be added to the concept
:- not imp(cc,I,X); not newconcept(cc,I,X);  I=1..2; onode(cc,I,X).

% Biclique (Concept) edge cover
newedgecoverb(cc,N1*N2):- N1={newconcept(cc,1,X):node(X)}; N2={newconcept(cc,2,X):node(X)}.


#show newconcept(X,Y,Z): newconcept(X,Y,Z).
%#show nbelements/1. #show nbelements/2.
#show imp(X,Y,Z): imp(X,Y,Z). 
#show minobj/2. 
#show ccedge(X,Y,Z):ccedge(X,Y,Z).
#show oedge/3.
#show newedgecoverb/2.
