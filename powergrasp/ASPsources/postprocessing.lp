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
% Constants:
%       - cc: treated connected component. (cc/1 gives existing cc)
%       -  k: current step of treatment (first step is 1)
%       - lowerbound: the minimal score (see 'lowerbound optimization')
%       - upperbound: the maximal score (see 'lowerbound optimization')
%
% Input (from findbestclique or findbestbiclique):
%       - newconcept(cc,k,T,X): X is the member of the set T in the concept cc at step k.
%       - powernode(CC,K,T,X): X is the member of the set T in the concept CC at step K.
%       - clique(cc,k): concept is a clique.
%       - star(cc,k,T): set T of concept is a star.
% Output:
%       - powernode(cc,k,T,X): X is the member of the set T in the concept cc at step k.
%       - poweredge(cc,K1,T1,K2,T2): powernode K1,T1 is linked to powernode K2,T2.
%       - poweredge(cc,K1,T1,X): powernode K1,T1 is linked to node X.
%       - covered(X,Y): oriented edge X to Y is covered by returned powernode(s).
%       - include_block(k,B,p(cc,k,T)): block B contains set T of newconcept.
%       - block(k,B,X): block B contains X.
%       - include_powernode(cc,K1,T1,K2,T2): powernode K1,T1 contains K2,T2.
%       - powernode_count(S): S powernode are generated.
%       - edge(X,Y): oriented edge X to Y remains unused at this step
%       - score(cc,k,b(S)): concept cc at step k is a biclique of score S. [DEBUG]
%       - score(cc,k,c(S)): concept cc at step k is a   clique of score S. [DEBUG]
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%#program postprocessing(cc,k,lowerbound,upperbound).



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%  BLOCKS  %%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% ancestor blocks are all blocks containing all elements of the newconcept
ancestor_block(p(cc,K2,T2),T):- newconcept(cc,k,T,_) ; powernode(cc,K2,T2,_) ;
                                powernode(cc,K2,T2,X) : newconcept(cc,k,T,X).

% the parent block is the ancestor block containing no other ancestor block
parent_block(Parent,T):- ancestor_block(Parent,T) ;
                         %include_block(k-1,Parent,Inter) ; ancestor_block(Inter,T).
                         not include_block(k-1,Parent,Inter) : ancestor_block(Inter,T) .

% it can't have more than 2 parent_block, because there is at most two newconcepts.
:- 3 { parent_block(_,_) }.
:- 0 { parent_block(_,_) } 1.

% debug: newconcept T fit perfectly with the powernode cc,L,U
%perfectfit(p(cc,L,U),T):- block(k-1,p(cc,L,U),X) : newconcept(cc,k,T,X) ;
                          %block(k-1,p(cc,L,U),_) ; not star(cc,k,T) ; T=1..2.

% subblocks are all blocks included in P.
subblock(T,C):- parent_block(B,T) ;
                C=p(cc,L,U) ; block(k-1,p(cc,L,U),E) ;
                newconcept(cc,k,T,E) ; L<k ;
                include_block(k-1,B,C).


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
include_block(k,B,p(cc,k,1)):- parent_block(B,1) ; newconcept(cc,k,T,X).
include_block(k,B,p(cc,k,2)):- parent_block(B,2) ; not clique(cc,k).
%    - all blocks included in B that are in P are included in P instead of B
include_block(k,p(cc,k,T),C):- subblock(T,C).
%    - all blocks that aren't related to P are kept "as is" for next step
include_block(k,B,C):- include_block(k-1,B,C) ;
                       not subblock(_,B) ;
                       not subblock(_,C).


% nodes in sub blocks are kept in their sub block
block(k,B,X):- newconcept(cc,k,1,X) ; subblock(1,B) ;
               block(k-1,B,X) ; not star(cc,k,1).
% idem, for the second part of the concept in case of biclique
block(k,B,X):- newconcept(cc,k,2,X) ; subblock(2,B) ;
               block(k-1,B,X) ; not star(cc,k,2) ; not clique(cc,k).

% nodes covered by a powernode are set in the associated block, if not in a sub block
block(k,p(cc,k,1),X):- newconcept(cc,k,1,X) ; not subblock(1,B) ;
                       block(k-1,B,X) ; not star(cc,k,1).
% idem, for the second part of the concept in case of biclique
block(k,p(cc,k,2),X):- newconcept(cc,k,2,X) ; not subblock(2,B) ;
                       block(k-1,B,X) ; not star(cc,k,2) ; not clique(cc,k).



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%% EDGE COVER %%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Edge cover is computed as the number of edges replaced by the poweredge.
%  the score is defined as the upperbound (maximal edge cover) minus edge cover.
%  bigger is the edge cover, smaller is the score.
%  solver's job is to minimize the score, thus maximize the edge cover.

% clique: create an edge to powernode itself / don't need to create two powernodes
poweredge(p(cc,k,1),p(cc,k,1)):- clique(cc,k).
% star: link directly the alone node to the second powernode
poweredge(p(cc,k,3-T),      X):- star(cc,k,T) ; newconcept(cc,k,T,X).
% in all other cases: create a poweredge between the two newconcepts
poweredge(p(cc,k,1),p(cc,k,2)):- not clique(cc,k) ; not star(cc,k,T): T=1..2.

% Are covered all edges of concept that link two nodes of different sets.
covered(cc,k,X,Y):- newconcept(cc,k,T,X) ; newconcept(cc,k,3-T,Y) ; X<=Y ; T=1..2.

% Edge cover, the number of edge covered by the concept
edgecover(cc,k,T,N):- N={newconcept(cc,k,T,Y)} ; T=1..2.

% Concept score, equal to maximal score - edge cover.
score(cc,k,N):- N=upperbound-(N1*N2); N>=0   ; not clique(cc,k)    ;
                edgecover(cc,k,1,N1) ; edgecover(cc,k,2,N2).
score(cc,k,N):- N=upperbound-((N1*(N1-1))/2) ; N>=0 ; clique(cc,k) ;
                N1={newconcept(cc,k,1,X)}.


% Minimize score
#minimize{S@1,S:score(cc,k,S)}.

% Exclusion of concepts with not enough nodes.
%  The lowerbound is equals to 1 at least,
%  and determined by the scorebound ASP program.
%  The upperbound is the min between the number of remaining edges
%  in the connected component and the size of the previous concept.
:- score(cc,k,S) ; S>upperbound-lowerbound.




%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%% RESULTS %%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Discard cases when no score is generated
:- not score(cc,k,_).

%#show maxnewedge(N): N=(upperbound-lowerbound)+1.
#show.
#show powernode(cc,k,T,X): newconcept(cc,k,T,X) ; not clique(cc,k) ; not star(cc,k,T).
#show powernode(cc,k,1,X): newconcept(cc,k,_,X) ;     clique(cc,k).
#show poweredge(cc,K1,T1,K2,T2): poweredge(p(cc,K1,T1),p(cc,K2,T2)).
#show poweredge(cc,K1,T1,X): poweredge(p(cc,K1,T1),X) , newconcept(_,_,_,X).
#show include_powernode(cc,K1,T1,K2,T2): include_block(k,b(_,p(cc,K1,T1)),b(_,p(cc,K2,T2))).
#show edge(X,Y): oedge(X,Y) , not covered(X,Y) , not covered(cc,k,X,Y) , X!=Y.
#show powernode_count(1): clique(cc,k).
#show powernode_count(2-S-P): not clique(cc,k) , S={star(cc,k,_)}, P={perfectfit(_,_)}.
#show covered(X,Y): covered(cc,k,X,Y).
#show block(k,P,X): block(k,P,X).
#show include_block(k,B,C): include_block(k,B,C).
#show newconcept/3.
% debug output
#show parent_block/2.
#show score(upperbound-S): score(cc,k,S).  % the outside consider that the edge cover is the score
#show clique/2.
#show upper(upperbound).
#show lower(lowerbound).
%#show star/3.
%#show imp/3.
