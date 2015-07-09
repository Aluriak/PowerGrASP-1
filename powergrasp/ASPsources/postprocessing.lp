%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Perform post-processing of the data at each steps.
%  its not a stand alone program, but a set of rules that needs to be grounded with
%  find best clique and find best biclique program
%  the post processing consist of rules shared by cliques and bicliques,
%  like parent block or include block rules, and the associated constraints.
%
%  more important : postprocessing is based on atoms newconcept, clique and star
%  produced (or not) by findbestbiclique and findbestclique.
%  The maximal lowerbound optimization of concept score is performed by postprocessing.
%
% initial version:  09/07/2014   L. Bourneuf
%
% Input (from findbestclique or findbestbiclique):
%       - newconcept(cc,k,T,X): X is the member of the set T in the concept cc at step k.
%       - clique(cc,k): concept is a clique.
%       - star(cc,k,T): set T of concept is a star.
% Output:
%       - powernode(cc,k,T,X): X is the member of the set T in the concept cc at step k.
%       - poweredge(cc,K1,T1,K2,T2): powernode K1,T1 is linked to powernode K2,T2.
%       - poweredge(cc,K1,T1,X): powernode K1,T1 is linked to node X.
%       - covered(X,Y): oriented edge X to Y is covered by returned powernode(s).
%       - include_block():
%       - block():
%       - include_powernode():
%       - powernode_count():
%       - edge(X,Y): oriented edge X to Y remains unused at this step
%       - score(cc,k,b(S)): concept cc at step k is a biclique of score S. [DEBUG]
%       - score(cc,k,c(S)): concept cc at step k is a   clique of score S. [DEBUG]
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#program postprocessing(cc,k,lowerbound,upperbound).



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%  BLOCKS  %%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
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
include_block(k,B,p(cc,k,2)):- parent_block(B,2) ; not clique(cc,k).
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
                          block(k-1,p(cc,L,U),Anonymous) ; T=1..2 ; L<k.
#show perfectfit/2.


% nodes covered by a powernode are set in the associated block
block(k,p(cc,k,1),X):- newconcept(cc,k,1,X) ; not star(cc,k,1).
block(k,p(cc,k,2),X):- newconcept(cc,k,2,X) ; not star(cc,k,2) ; not clique(cc,k).

% keep nodes not covered by new concept in their block
block(k,P,X):- membercc(cc,X) ; not newconcept(cc,k,T,X): T=1..2 ; block(k-1,P,X).
block(k,P,X):- newconcept(cc,k,T,X) ; star(cc,k,T) ; block(k-1,P,X) ; T=1..2.



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%% EDGE COVER %%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% clique: create an edge to powernode itself / don't need to create two powernodes
poweredge(p(cc,k,1),p(cc,k,1)):- clique(cc,k).
% star: link directly the alone node to the second powernode
poweredge(p(cc,k,3-T),      X):- star(cc,k,T) ; newconcept(cc,k,T,X).
% in all other cases: create a poweredge between the two newconcepts
poweredge(p(cc,k,1),p(cc,k,2)):- not clique(cc,k) ; not star(cc,k,T): T=1..2.

% Are covered all edges of concept that link two nodes of different sets.
covered(cc,k,X,Y):- newconcept(cc,k,T,X) ; newconcept(cc,k,3-T,Y) ; X<=Y ; T=1..2.

% Concept edge cover (score)
newedgecover(cc,k,N):- N=N1*N2         ; N<=upperbound ; not clique(cc,k) ;
                       N1={newconcept(cc,k,1,X)} ; N2={newconcept(cc,k,2,Y)}.
newedgecover(cc,k,N):- N=(N1*(N1-1))/2 ; N<=upperbound ;     clique(cc,k) ;
                       N1={newconcept(cc,k,1,X)}.


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
#show.
#show powernode(cc,k,T,X): newconcept(cc,k,T,X) ; not clique(cc,k) ; not star(cc,k,T).
#show powernode(cc,k,1,X): newconcept(cc,k,_,X) ;     clique(cc,k).
#show poweredge(cc,K1,T1,K2,T2): poweredge(p(cc,K1,T1),p(cc,K2,T2)).
#show poweredge(cc,K1,T1,X): poweredge(p(cc,K1,T1),X) , newconcept(_,_,_,X).
#show include_powernode(cc,K1,T1,K2,T2): include_block(k,b(_,p(cc,K1,T1)),b(_,p(cc,K2,T2))).
#show edge(X,Y): oedge(X,Y) , not covered(X,Y) , not covered(cc,k,X,Y) , X!=Y.
#show powernode_count(1): clique(cc,k).
#show powernode_count(2-S): not clique(cc,k) , S={star(cc,k,_)}.
#show covered(X,Y): covered(cc,k,X,Y).
#show block(k,P,X): block(k,P,X).
#show include_block(k,B,C): include_block(k,B,C).
% debug output
#show parent_block/2.
#show score(S): newedgecover(cc,k,S).
#show clique/2.
%#show star/3.
%#show imp/3.