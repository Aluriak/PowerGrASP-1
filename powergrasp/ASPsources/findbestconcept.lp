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

% a newconcept is trivial iff it contains only one node or newconcept
trivial(cc,k,T):- newconcept(cc,k,T,_) ; 1 { newconcept(cc,k,T,X) } 1.
trivial(cc,k,T):- newconcept(cc,k,T,_) ; 0 { newconcept(cc,k,T,X) } 0 ;
                  1 { include_block(k,b(k,p(cc,k,T)),b(k,X)) } 1.

% a star is a biclique with one powernode composed of only one node
star(cc,k,T):- 1 { newconcept(cc,k,T,X) } 1 ; T=1..2.
%:- star(cc,k,3-T) ; star(cc,k,T) ; T=1..2. % link between two nodes will not be treated as a interesting case

% Impossible element in a concept
%  a node is impossible if not linked to some node of other part
imp(k,3-T,X):- membercc(cc,X); newconcept(cc,k,T,Y) ; not oedge(X,Y) ; not oedge(Y,X).
%  a node is impossible if in a block different from another element in the same set
imp(k,T,X):- newconcept(cc,k,T,X) ; newconcept(cc,k,T,Y) ; topblock(k,B,P) ; include_block(k,B,b(k,P)) ; not block(K,P,X) ; block(K,P,Y).
%imp(k,T,X):- newconcept(cc,k,T,X) ; newconcept(cc,k,T,Y) ; not block(k-1,P,X) ; block(k-1,P,Y).

% Consistency ; no impossible element can be added to the concept
:- imp(k,T,Y); newconcept(cc,k,T,Y).

% Maximality  ; all possible elements have to be added to the concept
%:- not imp(k,T,X); not newconcept(cc,k,T,X) ; T=1..2; membercc(cc,X).

% Set 1 and Set 2 of concept are equal (clique) or have an empty intersection (biclique)
nonclique(cc,k):-     newconcept(cc,k,1,X); not newconcept(cc,k,2,X).
nonclique(cc,k):- not newconcept(cc,k,1,X);     newconcept(cc,k,2,X).
:- newconcept(cc,k,1,X) ; newconcept(cc,k,2,X) ; nonclique(cc,k).



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%  BLOCKS  %%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% top block is the smaller block B that contain a newconcept P at step k
%   the top block is not the block created by newconcept P.
topblock(1,b(0,cc),p(cc,k,T)):- k=1 ; T=1..2.
topblock(k,B,P):- include_block(k-1,B,C) ; C=b(k-1,P) ; P=p(cc,K,T) ;
                  not { include_block(k-1,B,Z) ; include_block(k-1,Z,C) }.

% block inclusion : keep trace of block hierarchy
%  algorithmic for the block P of the new concept, and its topblock B:
%    if all nodes of B are in P (<=> P == B): done
%    else: (<=> P is included in B)
%      create include_block(k,B,P)
%      for each block C in B:
%        assert(C is included in P OR C inter P = {0})
%        if C included in P:
%          don't create include_block(k,B,C)
%          create include_block(k,P,C)
%        else: (C inter P = {0})
%          do nothing else
%
%  in a more logical way:
%    - P is included in B
include_block(k,B,b(k,P)):- topblock(k,B,P).
%    - all blocks included in B that are in P are included in P instead of B
include_block(k,b(k,P),C):- topblock(k,B,P) ;
                            C=b(k-1,p(cc,L,T)) ; newconcept(cc,L,T,E) ;
                            P=p(cc,k,U) ; newconcept(cc,k,U,E) ;
                            include_block(k-1,B,C).
%    - all blocks that aren't in P are kept «as is» for next step
include_block(k,B,C):-  not include_block(K,b(k,P),C): K=(k-1)..k ;
                        C=b(k-1,p(cc,L,T)) ; block(k-1,p(cc,L,T),_) ;
                        P=p(cc,k,U) ; newconcept(cc,k,U,_) ;
                        include_block(k-1,B,C).

#show topblock/3.
#show include_block/3.



% initial state of blocks : each node is in its cc
block(0,cc,X):- membercc(cc,X).

% nodes covered by a powernode are set in the associated block
block(k,p(cc,k,T),X):- newconcept(cc,k,T,X).

% keep nodes not covered by new concept in their block
block(k,P,X):- membercc(cc,X) ; not newconcept(cc,k,T,X): T=1..2 ; block(k-1,P,X).




%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%% EDGE COVER %%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% clique: create an edge to powernode itself / don't need to create two powernodes
poweredge(p(cc,k,1),p(cc,k,1)):- not nonclique(cc,k).
% star: link directly the alone node to the second powernode
poweredge(p(cc,k,3-T),      X):- star(cc,k,T) ; newconcept(cc,k,T,X).
% in all other cases: create a poweredge between the two newconcepts
poweredge(p(cc,k,1),p(cc,k,2)):- nonclique(cc,k) ; not star(cc,k,T): T=1..2.

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
#show powernode(cc,k,T,X): newconcept(cc,k,T,X) ;     nonclique(cc,k).
#show powernode(cc,k,1,X): newconcept(cc,k,_,X) ; not nonclique(cc,k).
#show poweredge(cc,K1,T1,K2,T2): poweredge(p(cc,K1,T1),p(cc,K2,T2)).
#show poweredge(cc,K1,T1,X): poweredge(p(cc,K1,T1),X).
#show include_powernode(cc,K1,T1,K2,T2): include_block(k,b(_,p(cc,K1,T1)),b(_,p(cc,K2,T2))).
% undesirable output
#show clique(cc,k): not nonclique(cc,k).
#show covered(X,Y): covered(cc,k,X,Y).
#show block(k,P,X): block(k,P,X).
#show trivial/3.
#show include_block(k,B,C): include_block(k,B,C).
% debug
#show score(cc,k,b(S)): newedgecover(cc,k,S),     nonclique(cc,k).
#show score(cc,k,c(S)): newedgecover(cc,k,S), not nonclique(cc,k).
%#show imp/3.
%#show step/1.
