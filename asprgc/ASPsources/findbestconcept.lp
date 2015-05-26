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
%       - covered(X,Y): edge(X,Y) is already covered.
% Output:
%       - powernode(cc,k,T,X): X is the member of the set T in the concept cc at step k.
%       - clique(cc,k): concept cc at step k is a clique.
%       - score(cc,k,b(S)): concept cc at step k is a biclique of score S. [DEBUG]
%       - score(cc,k,c(S)): concept cc at step k is a   clique of score S. [DEBUG]
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#program findbestconcept(cc,k).
step(k).



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%% CONCEPTS %%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% oedge are oriented and non-covered by previous steps
oedge(X,Y):- ccedge(cc,X,Y) ; X<Y ; not covered(X,Y).
oedge(X,Y):- ccedge(cc,Y,X) ; X<Y ; not covered(X,Y).
oedge(X,X):- membercc(cc,X) ; not nonclique(cc,k). % necessity for clique cases

% Choice of the minimum of the concept
1{minobj(cc,k,X):membercc(cc,X)}1.

% Choice of elements in part 1
newconcept(cc,k,1,X):- minobj(cc,k,X).
{ newconcept(cc,k,1,X): membercc(cc,X), Min<X }:- minobj(cc,k,Min).
% or (that need a test)
%{ newconcept(cc,k,1,X): membercc(cc,X), Min<X, block(k-1,P,X) }:- minobj(cc,k,Min) ; block(k-1,P,Min).

% Choice of elements in part 2
1 { newconcept(cc,k,2,Y): oedge(Min,Y), Min<=Y } :- minobj(cc,k,Min).

% Impossible element in a concept
%  a node is impossible if not linked to some node of other part
imp(k,3-T,X):- membercc(cc,X); newconcept(cc,k,T,Y) ; not oedge(X,Y) ; not oedge(Y,X).
%  a node is impossible if in a block different from another element in the same set
imp(k,T,X):- newconcept(cc,k,T,X) ; newconcept(cc,k,T,Y) ; block(k-1,P,Y) ; not block(k-1,P,X).

% Consistency ; no impossible element can be added to the concept
:- imp(k,T,Y); newconcept(cc,k,T,Y).

% Maximality  ; all possible elements have to be added to the concept
:- not imp(k,T,X); not newconcept(cc,k,T,X); T=1..2; membercc(cc,X).

% Set 1 and Set 2 of concept are equal (clique) or have an empty intersection (biclique)
nonclique(cc,k):-     newconcept(cc,k,1,X); not newconcept(cc,k,2,X).
nonclique(cc,k):- not newconcept(cc,k,1,X);     newconcept(cc,k,2,X).
:- newconcept(cc,k,1,X) ; newconcept(cc,k,2,X) ; nonclique(cc,k).



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%  BLOCKS  %%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% initial state of blocks : each node is in its cc
block(0,cc,X):- membercc(cc,X).

% nodes covered by a powernode are set in the associated block
block(k,p(cc,k,T),X):- newconcept(cc,k,T,X).

% keep nodes not covered by new concept in their block
block(k,P,X):- membercc(cc,X) ; not newconcept(cc,k,T,X): T=1..2 ; block(k-1,P,X).




%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%% EDGE COVER %%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Are covered all edges of concept that link two nodes of different sets.
covered(cc,k,X,Y):- newconcept(cc,k,T,X) ; newconcept(cc,k,3-T,Y) ; X<=Y ; T=1..2.

% Concept edge cover (score)
newedgecover(cc,k,   N1*N2   ):- N1={newconcept(cc,k,1,X)} ; N2={newconcept(cc,k,2,Y)} ;     nonclique(cc,k).
newedgecover(cc,k,(N*(N-1))/2):-  N={newconcept(cc,k,1,X)}                             ; not nonclique(cc,k).

% Maximize score
#maximize{S@1,S:newedgecover(cc,k,S)}.

% Exclusion of concept with two nodes
:- newedgecover(cc,k,S) ; S<=1. % 1*1 == 1 and 2*1/2 == 1



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%% RESULTS %%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% output
#show powernode(cc,k,T,X): newconcept(cc,k,T,X).
#show clique(cc,k): not nonclique(cc,k).
#show score(cc,k,b(S)): newedgecover(cc,k,S),     nonclique(cc,k).
#show score(cc,k,c(S)): newedgecover(cc,k,S), not nonclique(cc,k).
#show covered(X,Y): covered(cc,k,X,Y).
#show block/3.
%#show previous_step/1.
%#show step/1.
