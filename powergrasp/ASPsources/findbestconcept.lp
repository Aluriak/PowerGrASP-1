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
#program findbestconcept(cc,k,lowerbound).
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

% Choice of elements in part 2
1 { newconcept(cc,k,2,Y): oedge(Min,Y), Min<=Y } :- minobj(cc,k,Min).

% a star is a biclique with one powernode composed of only one node
star(cc,k,T):- 1 { newconcept(cc,k,T,X) } 1 ; T=1..2.
:- star(cc,k,3-T) ; star(cc,k,T) ; T=1..2. % link between two nodes will not be treated as a interesting case

% Impossible element in a concept
%  a node is impossible if not linked to some node of other part
imp(k,3-T,X):- membercc(cc,X); newconcept(cc,k,T,Y) ; not oedge(X,Y) ; not oedge(Y,X).
%  a node is impossible if in a block different from another element in the same set
imp(k,T,X):- newconcept(cc,k,T,X) ; newconcept(cc,k,T,Y) ; parent_block(B,T) ;
             include_block(k-1,B,P) ; not block(k-1,P,X) ; block(k-1,P,Y) ; X!=Y.
% the following doesn't works when a powernode must be splitted because of block overlapping
%imp(k,T,X):- not newconcept(cc,k,T,X) ; newconcept(cc,k,T,Y) ; parent_block(B,T) ;
             %include_block(k-1,B,P) ; block(k,P,X) ; block(k,P,Y) ; X!=Y.

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
% parent block is the smaller block B that contain a newconcept P at step k
%   the top block is not the block created by newconcept P.
%parent_block(1,b(1,cc),T):- T=1..2 ; k=1. % initial condition

% B is a parent block of P if it contains it and no other block contained in B contains P.
parent_block(B,T):- block_contains_newconcept(k,B,T) ;
                      B!=b(k,p(cc,k,T)) ;
                      not { include_block(k-1,B,Z) ; block_contains_newconcept(k,Z,T) }.
% it can't have more than 2 parent_block, because there is at most two newconcepts.
:- 3 { parent_block(_,_) }.
:- 0 { parent_block(_,_) } 1.

% a block contains a newconcept if at least one point of it is in block at current step
block_contains_newconcept(k,p(cc,L,U),T):- block(k-1,p(cc,L,U),X) ; newconcept(cc,k,T,X).
block_contains_newconcept(k,cc,T):- block(k-1,cc,X) ; newconcept(cc,k,T,X).

% block inclusion : keep trace of block hierarchy
%  algorithmic for the block P of the new concept, and its parent_block B:
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
include_block(k,B,p(cc,k,1)):- parent_block(B,1).
include_block(k,B,p(cc,k,2)):- parent_block(B,2) ; nonclique(cc,k).
%    - all blocks included in B that are in P are included in P instead of B
include_block(k,p(cc,k,T),C):- parent_block(B,T) ;
                            C=p(cc,L,U) ; block(k-1,p(cc,L,U),E) ;
                            newconcept(cc,k,T,E) ; L<k ;
                            include_block(k-1,B,C).
%    - all blocks that aren't in P are kept «as is» for next step
include_block(k,B,C):- C=p(cc,L,U) ; block(k-1,p(cc,L,U),Anonymous) ; L<k ;
                       0 { block(k-1,p(cc,L,U),E) : newconcept(cc,k,T,E) } 0 ;
                       %0 { e(E): newconcept(cc,k,T,E) , block(k-1,p(cc,L,U),E) } 0 ;
                       include_block(k-1,B,C) ;
                       not include_block(k,p(cc,k,T),C) : T=1..2.

% debug: newconcept T fit perfectly with the powernode cc,L,U
perfectfit(T,p(cc,L,U)):- 0 {block(k-1,p(cc,L,U),X) : not newconcept(cc,k,T,X) } 0 ;
                          block(k-1,p(cc,L,U),Anonymous) ; L<k ; T=1..2.
#show perfectfit/2.


% nodes covered by a powernode are set in the associated block
block(k,p(cc,k,1),X):- newconcept(cc,k,1,X) ; not star(cc,k,1).
block(k,p(cc,k,2),X):- newconcept(cc,k,2,X) ; not star(cc,k,2) ; nonclique(cc,k).

% keep nodes not covered by new concept in their block
block(k,P,X):- membercc(cc,X) ; not newconcept(cc,k,T,X): T=1..2 ; block(k-1,P,X).
block(k,P,X):- newconcept(cc,k,T,X) ; star(cc,k,T) ; block(k-1,P,X) ; T=1..2.




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
%newedgecover(cc,k,N):- N1={newconcept(cc,k,1,X)} ; N2={newconcept(cc,k,2,Y)} ;     nonclique(cc,k) ;
                       %N=N1*N2.
%newedgecover(cc,k,N):- N1={newconcept(cc,k,1,X)}                             ; not nonclique(cc,k) ;
                       %N=(N1*(N1-1))/2.

% take account of minimal upper bound of the minimal node
newedgecover(cc,k,N):- N1={newconcept(cc,k,1,X)} ; N2={newconcept(cc,k,2,Y)} ;     nonclique(cc,k) ;
                       N=N1*N2         ; minobj(cc,k,Min) ; upperbound(Min,U) ; N<U.
newedgecover(cc,k,N):- N1={newconcept(cc,k,1,X)} ; N2={newconcept(cc,k,2,Y)} ;     nonclique(cc,k) ;
                       N=N1*N2         ; minobj(cc,k,Min) ; not upperbound(Min,_).

% Maximize score
#maximize{S@1,S:newedgecover(cc,k,S)}.

% Exclusion of concept with not enough nodes.
%  the maximal lowerbound is equals to 1 at least,
%  and determined by the scorebound ASP program.
:- newedgecover(cc,k,S) ; S<lowerbound.



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%% RESULTS %%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% output
#show powernode(cc,k,T,X): newconcept(cc,k,T,X) ;     nonclique(cc,k) ; not star(cc,k,T).
#show powernode(cc,k,1,X): newconcept(cc,k,_,X) ; not nonclique(cc,k).
#show poweredge(cc,K1,T1,K2,T2): poweredge(p(cc,K1,T1),p(cc,K2,T2)).
#show poweredge(cc,K1,T1,X): poweredge(p(cc,K1,T1),X) , newconcept(_,_,_,X).
#show include_powernode(cc,K1,T1,K2,T2): include_block(k,b(_,p(cc,K1,T1)),b(_,p(cc,K2,T2))).
#show edge(X,Y): oedge(X,Y) , not covered(X,Y) , not covered(cc,k,X,Y) , X!=Y.
% undesirable output
%#show clique(cc,k): not nonclique(cc,k).
#show covered(X,Y): covered(cc,k,X,Y).
#show block(k,P,X): block(k,P,X).
#show trivial/3.
#show include_block(k,B,C): include_block(k,B,C).
#show parent_block/2.
% debug
#show score(cc,k,b(S)): newedgecover(cc,k,S),     nonclique(cc,k).
#show score(cc,k,c(S)): newedgecover(cc,k,S), not nonclique(cc,k).
%#show star/3.
%#show imp/3.
%#show step/1.
