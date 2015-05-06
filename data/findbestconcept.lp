%*
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
Rewritting of powercomp4.lp by Lucas Bourneuf,
without special treatment of bipartite case.

Find best concept in the incidence matrix of a simple non oriented graph
A concept can be a biclique or a clique.

Input:
        %- oedge(X,Y): there exists an edge between X and Y in the graph and edge is oriented X<Y.
        - ccedge(cc,X,Y): there exists an edge between X and Y in the
                          subgraph corresponding to connected component cc
        - membercc(cc,Y): Y is a member of cc, but not its root.
        for cliques only:
        - inter(X,Y): there exists an edge between X and Y in the graph (all edges are symmetric).
Output:
        if biclique found:
        - nb(set1,N): set 1 contains N elements. [DEBUG]
        - nb(set2,N): set 2 contains N elements. [DEBUG]
        - newedgecoverb(cc,N): cc have a score (edge covering) of N.
        - newconcept(cc,T,X): X is the member of the set T of the biclique cc.
        if clique found:
        - newedgecoverc(cc,N): score (edge covering) by the clique cc
        - newclique(cc,k,X): X belongs to clique cc
        - clique3(X): cc is a clique of 3 elements
        in all cases:
        - newedgecover(cc,N): score of the (bi)clique cc.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
*%
#program findbestconcept(cc,k).

% Uses program parameters
concomp(cc).
step(k).





%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%% CONCEPTS %%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Node is a paart of things.
onode(cc,1,X):- membercc(cc,X). % X belongs to CC
onode(cc,2,X):- ccedge(cc,X,A). % X is a non-terminal node

% oedge is a non-oriented and non-covered edge
covered(X,Y):- covered(Y,X).
oedge(C,X,Y):- ccedge(C,X,Y) ; not covered(X,Y).
oedge(C,X,Y):- ccedge(C,Y,X) ; not covered(X,Y).


% Choice of the minimum of the concept
1{minobj(cc,k,X):membercc(cc,X)}1.
minobj(X):- minobj(A1,A2,X).

%Choice of elements in part 1
newconcept(cc,k,1,X):- minobj(cc,k,X).
{ newconcept(cc,k,1,X): membercc(cc,X),X>Min }:- minobj(cc,k,Min).
%Choice of elements in part 2
1 { newconcept(cc,k,2,Min); newconcept(cc,k,2,Y):oedge(cc,Min,Y),Y>Min } :- minobj(cc,k,Min).

%impossible element in a concept
% a node is impossible if not linked to all nodes of other part
imp(cc,3-I,X):- membercc(cc,X); newconcept(cc,k,I,Y); not oedge(cc,X,Y); not oedge(cc,Y,X).
%imp(cc,3-I,X):- membercc(cc,X); membercc(cc,Y); not ccedge(cc,X,Y); not ccedge(cc,Y,X).

% Consistency ; no impossible element can  be added to the concept
:- imp(cc,I,Y); newconcept(cc,k,I,Y).

% Maximality  ; all possible elements have to be added to the concept
:- not imp(cc,I,X); not newconcept(cc,k,I,X); I=1..2; onode(cc,I,X).


% Set 1 and Set 2 of bicliques are equal (cliques) or have an empty intersection (bicliques )
nonclique(cc,k):- newconcept(cc,k,1,X); not newconcept(cc,k,2,X).
nonclique(cc,k):- not newconcept(cc,k,1,X); newconcept(cc,k,2,X).
:- newconcept(cc,k,1,X); newconcept(cc,k,2,X); nonclique(cc,k).

% Count element in each set of the concept
%nb(concept1,N):- N={newconcept(cc,1,X)}.
%nb(concept2,N):- N={newconcept(cc,2,X)}.
% are equivalent to:
nb(set1,N):- N=#count{1,X:newconcept(cc,k,1,X)}.
nb(set2,N):- N=#count{1,X:newconcept(cc,k,2,X)}.

% Concept edge cover (score)
newedgecover(cc,k,N1*N2):- N1={newconcept(cc,k,1,X)} ; N2={newconcept(cc,k,2,Y)}.

% Maximize score
#maximize{N@1,N:newedgecover(cc,k,N)}.




%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%% RESULTS %%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#show concept(cc,k,T,X): newconcept(cc,k,T,X).
#show nb/2.
#show edgecover(cc,k,X): newedgecover(cc,k,X).
