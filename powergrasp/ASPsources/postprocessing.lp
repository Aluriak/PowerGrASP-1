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
%       - concept(cc,k,T,X): X is the member of the set T in the concept cc at step k.
%       - clique(cc,k): concept is a clique.
%       - star(cc,k,T): set T of concept is a star.
%       - degree(X,D): node X have a degree of D (=there is D nodes linked to X)
%       - powernode(cc,L,T,X): a concept in cc exists, created at step L and having node X in set T
%       - powernode_inclusion(cc,K,V,L,U): powernode K,V includes powernode L,U in cc.
% Output:
%       - powernode(cc,k,T,X): X is the member of the set T in the concept cc at step k.
%       - poweredge(cc,K1,T1,K2,T2): powernode K1,T1 is linked to powernode K2,T2.
%       - poweredge(cc,K1,T1,X): powernode K1,T1 is linked to node X.
%       - covered(X,Y): oriented edge X to Y is covered by returned powernode(s).
%       - powernode_inclusion(cc,K,V,L,U): powernode K,V includes powernode L,U in cc. (only new ones are generated)
%       - powernode_count(S): S new powernode are generated.
%       - edge(X,Y): oriented edge X to Y remains unused at this step
%       - score(cc,k,b(S)): concept cc at step k is a biclique of score S. [DEBUG]
%       - score(cc,k,c(S)): concept cc at step k is a   clique of score S. [DEBUG]
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#program postprocessing(cc,k,lowerbound,upperbound).


% existing powernodes are created in the previous steps
bug(powernodenumber):- powernode(cc,L,_,_) ; L>=k.



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%         COMPARISON between       %%%%%%%%%%%%
%%%%%%%%%%%  a concept set and a power node  %%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
powernode_element(cc,X):- powernode(cc,_,_,X).

% set T is included in an existing powernode, or vice-versa
include1(T,p(cc,L,U)):- concept(cc,k,T,X): powernode(cc,L,U,X) ; powernode(cc,L,U,_) ; concept(cc,k,T,_).
include2(p(cc,L,U),T):- powernode(cc,L,U,X): concept(cc,k,T,X) ; powernode(cc,L,U,_) ; concept(cc,k,T,_).

% set T is either partially overlapping or disjoint from  powernode p(cc,L,U)
exclude(T,p(cc,L,U)):- not include2(p(cc,L,U),T) ; not include1(T,p(cc,L,U)) ; concept(cc,k,T,_) ; powernode(cc,L,U,_).
% set T is partially overlapping powernode p(cc,L,U)
overlaps(T,p(cc,L,U)):- concept(cc,k,T,X) ; powernode(cc,L,U,X) ; exclude(T,p(cc,L,U)).

% in case of partial overlap with an existing powernode P, two sets can be created.
%  when overlap with many powernodes, one set can be created for each partition.
derivative_concept((L,U),T,X):- powernode(cc,L,U,X) ; overlaps(T,p(cc,L,U)) ; concept(cc,k,T,X) ;
                                not powernode(cc,K,V,X): overlaps(T,p(cc,K,V)), powernode_inclusion(cc,L,U,K,V).
derivative_concept((0,0),T,X):- concept(cc,k,T,X) ;
                                not powernode(cc,L,U,X): overlaps(T,p(cc,L,U)).

% keep only the largest concept (with the maximal number of nodes)
node_count((L,U),T,C):- derivative_concept((L,U),T,_) ; C={derivative_concept((L,U),T,_)}.
max_count(T,Max):- Max=#max{S:node_count(_,T,S)} ; T=1..2.
max_concept((L,U),T):- max_count(T,Max) ; node_count((L,U),T,Max) ;
                       not node_count((L2,U2),T,Max): node_count((L2,U2),T,Max), (L,U)>(L2,U2).
% one max concept for each set, but may have 0 or one (if no existing powernode or overlaps)
bug(toomuchmaxconcept):- 3 { max_concept(_,_) }.

% define the newconcept as one of the largest newconcept
newconcept(cc,k,T,X):- derivative_concept((L,U),T,X) ; max_concept((L,U),T).
% when no overlaps is detected
newconcept(cc,k,T,X):- concept(cc,k,T,X) ; not max_concept(_,T).

% Inclusion between previous powernodes and newconcept
newconcept_inclusion(k,T,L,U):- newconcept(cc,k,T,Y) ; powernode(cc,L,U,Y) ; not star(cc,k,T) ;
                                newconcept(cc,k,T,X): powernode(cc,L,U,X).
newconcept_inclusion(L,U,k,T):- newconcept(cc,k,T,Y) ; powernode(cc,L,U,Y) ; not star(cc,k,T) ;
                                powernode(cc,L,U,X): newconcept(cc,k,T,X).
% Inclusion with newconcept as a new powernode or equivalent (definitions of equivalence below)
powernode_inclusion(cc,M,V,L,U):- newconcept_inclusion(k,T,L,U) ; equivalent_powernode(M,V,T).
powernode_inclusion(cc,L,U,M,V):- newconcept_inclusion(L,U,k,T) ; equivalent_powernode(M,V,T).

% set T is strictly equivalent to the powernode p(cc,L,U)(all nodes in common)
%equivalent(T,p(cc,L,U)):- powernode_inclusion(cc,L,U,k,T) ; powernode_inclusion(cc,k,T,L,U).
equivalent(T,p(cc,L,U)):- newconcept_inclusion(L,U,k,T) ; newconcept_inclusion(k,T,L,U).
% use the newconcept iff no existing powernode is equivalent
equivalent_powernode(K,U,T):- newconcept(cc,k,T,_) ; equivalent(T,p(cc,K,U)).
equivalent_powernode(k,T,T):- newconcept(cc,k,T,_) ; not equivalent(T,_).

% a star is a biclique with one powernode composed of only one node
star(cc,k,T):- 1 { newconcept(cc,k,T,X) } 1 ; T=1..2 ; not clique(cc,k).
:- star(cc,k,3-T) ; star(cc,k,T) ; T=1..2. % link between two nodes will not be treated as a interesting case



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%% EDGE COVER %%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Edge cover is computed as the number of edges replaced by the poweredge.
%  the score is defined as the upperbound (maximal edge cover) minus edge cover.
%  bigger is the edge cover, smaller is the score.
%  solver's job is to minimize the score, thus maximize the edge cover.

% clique: create an edge to powernode itself / don't need to create two powernodes
poweredge(p(cc,K,U),p(cc,K,U)):- clique(cc,k) ; equivalent_powernode(K,U,1).
% star: link directly the alone node to the second powernode
poweredge(p(cc,K,U),        X):- star(cc,k,T) ; newconcept(cc,k,T,X) ; equivalent_powernode(K,U,3-T).
% in all other cases: create a poweredge between the two sets of the newconcept
poweredge(p(cc,K,U),p(cc,L,V)):- not clique(cc,k) ; not star(cc,k,T): T=1..2 ;
                                 equivalent_powernode(K,U,1) ; equivalent_powernode(L,V,2).

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
%  the maximal lowerbound is equals to 1 at least,
%  and determined by the scorebound ASP program,
%  as the number of remaining edges in the connected component
%  and the size of the previous concept.
:- score(cc,k,S) ; S>upperbound-lowerbound.




%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%% RESULTS %%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Discard cases when no score is generated
:- not score(cc,k,_).

#show.
#show bug/1.
#show powernode(cc,K,U,X): newconcept(cc,k,T,X) ; equivalent_powernode(K,U,T) ;
                           not clique(cc,k) ; not star(cc,k,T).
#show powernode(cc,K,U,X): newconcept(cc,k,1,X) ; equivalent_powernode(K,U,1) ; clique(cc,k).
#show poweredge(cc,K1,T1,K2,T2): poweredge(p(cc,K1,T1),p(cc,K2,T2)).
#show poweredge(cc,K1,T1,X): poweredge(p(cc,K1,T1),X), newconcept(_,_,_,X).
#show edge(X,Y): oedge(X,Y) , not covered(X,Y) , not covered(cc,k,X,Y) , X!=Y.
#show powernode_count(1): clique(cc,k).
#show powernode_count(2-S-P): not clique(cc,k) , S={star(cc,k,_)}, P={equivalent(_,_)}.
#show covered(X,Y): covered(cc,k,X,Y).
#show powernode_inclusion(cc,k,T,L,U): powernode_inclusion(cc,k,T,L,U), not equivalent(T,p(cc,L,U)).
#show powernode_inclusion(cc,L,U,k,T): powernode_inclusion(cc,L,U,k,T), not equivalent(T,p(cc,L,U)).
#show score(upperbound-S): score(cc,k,S).  % the outside consider that the edge cover is the score
% overlap
%#show clique/2.
%#show equivalent/2.
%#show equivalent_powernode/3.
%#show overlaps/2.
%#show star/3.
%#show newconcept/4.
%#show derivative_concept/3.
%#show include1/2.
%#show include2/2.
%#show concept/4.
% debug output
%#show clique/2.
%#show upper(upperbound).
%#show lower(lowerbound).
%#show powernode/4.
%#show star/3.
%#show imp/3.
