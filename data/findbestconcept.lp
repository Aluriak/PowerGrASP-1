%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Find best concept in the incidence matrix of a simple non oriented graph
% A concept can be a biclique or a clique.
%
% initial version:  09/12/2014   J. Nicolas
% revised version:  29/04/2014   L. Bourneuf
%
% Input:
%       - ccedge(cc,X,Y): there exists an edge between X and Y in the
%                         subgraph corresponding to connected component cc
%       - membercc(cc,Y): Y is a member of cc, but not its root.
%       for cliques only:
%       - covered(X,Y): edge(X,Y) is already covered.
% Output:
%       - nb(set1,N): set 1 contains N elements. [DEBUG]
%       - nb(set2,N): set 2 contains N elements. [DEBUG]
%       - concept(cc,k,T,X): X is the member of the set T in the concept cc at step k.
%       - edgecover(cc,k,N): score of the concept cc at step k.
%       - score(cc,k,b(S)): concept cc at step k is a biclique of score S.
%       - score(cc,k,c(S)): concept cc at step k is a   clique of score S.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
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
oedge(cc,X,Y):- ccedge(cc,X,Y) ; not covered(X,Y).
oedge(cc,X,Y):- ccedge(cc,Y,X) ; not covered(X,Y).
oedge(cc,X,X):- membercc(cc,X). % necessity for clique cases

% Choice of the minimum of the concept
1{minobj(cc,k,X):membercc(cc,X)}1.
minobj(X):- minobj(A1,A2,X).

%Choice of elements in part 1
newconcept(cc,k,1,X):- minobj(cc,k,X).
{ newconcept(cc,k,1,X): membercc(cc,X), X>Min }:- minobj(cc,k,Min).
%Choice of elements in part 2
1 { newconcept(cc,k,2,Min); newconcept(cc,k,2,Y):oedge(cc,Min,Y), Y>Min } :- minobj(cc,k,Min).

%impossible element in a concept
% a node is impossible if not linked to all nodes of other part
imp(cc,3-I,X):- membercc(cc,X); newconcept(cc,k,I,Y); not oedge(cc,X,Y); not oedge(cc,Y,X).

% Consistency ; no impossible element can  be added to the concept
:- imp(cc,I,Y); newconcept(cc,k,I,Y).

% Maximality  ; all possible elements have to be added to the concept
:- not imp(cc,I,X); not newconcept(cc,k,I,X); I=1..2; onode(cc,I,X).


% Set 1 and Set 2 of concept are equal (clique) or have an empty intersection (biclique)
nonclique(cc,k):-     newconcept(cc,k,1,X); not newconcept(cc,k,2,X).
nonclique(cc,k):- not newconcept(cc,k,1,X);     newconcept(cc,k,2,X).
:- newconcept(cc,k,1,X) ; newconcept(cc,k,2,X) ; nonclique(cc,k).

% Count element in each set of the concept
%nb(concept1,N):- N={newconcept(cc,1,X)}.
%nb(concept2,N):- N={newconcept(cc,2,X)}.
% are equivalent to:
nb(set1,N):- N=#count{1,X:newconcept(cc,k,1,X)}.
nb(set2,N):- N=#count{1,X:newconcept(cc,k,2,X)}.

% Concept edge cover (score)
newedgecover(cc,k,   N1*N2   ):- N1={newconcept(cc,k,1,X)} ; N2={newconcept(cc,k,2,Y)} ;     nonclique(cc,k).
newedgecover(cc,k,(N*(N-1))/2):-  N={newconcept(cc,k,1,X)}                             ; not nonclique(cc,k).

% Maximize score
#maximize{S@1,S:newedgecover(cc,k,S)}.

% Exclusion of concept with two nodes
:- newedgecover(cc,k,S) ; S<=1 ; not nonclique(cc,k).
:- newedgecover(cc,k,S) ; S<=1 ;     nonclique(cc,k).



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%% RESULTS %%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#show concept(cc,k,T,X): newconcept(cc,k,T,X).
#show nb/2.
#show score(cc,k,b(S)): newedgecover(cc,k,S),     nonclique(cc,k).
#show score(cc,k,c(S)): newedgecover(cc,k,S), not nonclique(cc,k).
