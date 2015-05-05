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
%any_step(0..k). % unused

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%% BICLIQUES %%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% If N node in cc, cc!=Y will be true "N-1 times"
nonsingletoncc(cc):- membercc(cc,Y); cc!=Y.
%#show nonsingletoncc/1.

% Node is a paart of things.
onode(cc,1,X):- membercc(cc,X). % X belongs to CC
onode(cc,2,X):- ccedge(cc,X,A). % X is a non-terminal node
node(X):- onode(Anonymous1,Anonymous2,X).

% oedge is a non-oriented and non-covered edge
covered(X,Y):- covered(Y,X).
oedge(C,X,Y):- ccedge(C,X,Y) ; not covered(X,Y).
oedge(C,X,Y):- ccedge(C,Y,X) ; not covered(X,Y).


%#show covered/2.
%#show oedge/3.
#show node/1.
%#show nbelements/4.
% Choice of a non empty concept

% Choice of the minimum of the concept
1{minobj(cc,k,X):membercc(cc,X)}1.
minobj(X):- minobj(A1,A2,X).


%Choice of elements in part 1
newconcept(cc,k,1,X):- minobj(cc,k,X).
{ newconcept(cc,k,1,X): membercc(cc,X),X>Min }:- minobj(cc,k,Min).
%:- newconcept(cc,k,1,X) ; Min>X ; minobj(cc,k,Min).  % useless assertion
%Choice of elements in part 2
1 { newconcept(cc,k,2,Y):oedge(cc,Min,Y) } :- minobj(cc,k,Min).

%Check that the concepts of simple graphs are not included in a clique of size 3:
%There must exist two elements in a same part that are not related or the concept covers exactly one edge.
nonclique(cc):- newconcept(cc,k,T,X) ; newconcept(cc,k,T,Y) ; X<Y ; not oedge(cc,X,Y).
nonclique(cc):- 2{newconcept(cc,k,T,X)}2.
:- not nonclique(cc).

%impossible element in a concept
% a node is impossible if not linked to all nodes of other part
imp(cc,3-I,X):- membercc(cc,X); newconcept(cc,k,I,Y); not oedge(cc,X,Y); not oedge(cc,Y,X).
%imp(cc,3-I,X):- membercc(cc,X); membercc(cc,Y); not ccedge(cc,X,Y); not ccedge(cc,Y,X).

%% consistency ; no impossible element can  be added to the concept
:- imp(cc,I,Y); newconcept(cc,k,I,Y).

%% maximality  ; all possible elements have to be added to the concept
:- not imp(cc,I,X); not newconcept(cc,k,I,X); I=1..2; onode(cc,I,X).


% Count element in each set of the concept
%nb(concept1,N):- N={newconcept(cc,1,X)}.
%nb(concept2,N):- N={newconcept(cc,2,X)}.
% are equivalent to:
nb(set1,N):- N=#count{1,X:newconcept(cc,k,1,X)}.
nb(set2,N):- N=#count{1,X:newconcept(cc,k,2,X)}.


%% Biclique (Concept) edge cover
%newedgecoverb(cc,k,N1*N2):- N1={newconcept(cc,k,1,X)} ; N2={newconcept(cc,k,2,Y)}.
newedgecoverb(cc,k,N1*N2):- N1={newconcept(cc,k,1,X)} ; N2={newconcept(cc,k,2,Y)}.
%newedgecoverb(cc,k,N1*N2):- nb(set1,N1), nb(set2,N2).


% Maximize cardinal values
%cardinal(cc,k,T,N):- N={newconcept(cc,k,T,X)} ; T=1..2. % unused
%#maximize{N1*N2@1,N1,N2: cardinal(cc,k,1,N1), cardinal(cc,k,2,N2)}.
#maximize{N@1,N:newedgecoverb(cc,k,N)}.

%#show cardinal/3.
%#show imp/3.
%#show minobj/2.
%#show ccedge/3.
%#show onode/3.
%#show node/1.
%#show oedge/3.
%#show ccedge/3.




%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%% CLIQUES %%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
clique3(cc):- oedge(cc,X,Y); oedge(cc,Y,Z); oedge(cc,X,Z).

%Choice of a  clique of at least 3 elements
3{newclique(cc,k,X): membercc(cc,X)}:- clique3(cc).

%consistency of the clique
:- newclique(cc,k,X); newclique(cc,k,Y) ; X<Y ; not oedge(cc,X,Y).

%maximality of the clique
:-  membercc(cc,X) ; not newclique(cc,k,X) ; inter(X,Y):newclique(cc,k,Y) ; clique3(cc).

newedgecoverc(cc,k,(N*(N-1))/2):- N={newclique(cc,k,X):membercc(cc,X)}; clique3(cc).
#maximize{(N*(N-1))/2@1,N: newedgecoverc(cc,k,N)}.



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%% RESULTS %%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
newedgecover(cc,k,b(N1)):- newedgecoverb(CC,k,N1) ;     newedgecoverc(CC,k,N2) ; N1>N2.
newedgecover(cc,k,b(N1)):- newedgecoverb(CC,k,N1) ; not newedgecoverc(CC,k,_).
newedgecover(cc,k,c(N1)):- newedgecoverc(CC,k,N1) ;     newedgecoverb(CC,k,N2) ; N1>N2.
newedgecover(cc,k,c(N1)):- newedgecoverc(CC,k,N1) ; not newedgecoverb(CC,k,_).

#show concept(cc,k,T,X): newconcept(cc,k,T,X) , newedgecover(cc,k,b(N)).
#show clique(cc,k,X): newclique(cc,k,X) , newedgecover(cc,k,c(N)).
%#show newclique/3.
#show nb/2.
#show newedgecover/3.
%#show newedgecover(cc,k,N): newedgecoverb(cc,k,N).
%#show oedge/3.
%#show clique3/1.
%#show newclique/2.
%#show newedgecoverc/2.
