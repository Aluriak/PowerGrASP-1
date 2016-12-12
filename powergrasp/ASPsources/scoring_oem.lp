%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Perform scoring of the postprocessed data at each steps.
%  The score equals to the edge cover of the concept.
%
% The Outgoing Edge Minimization method try to minimize the number of elements
%  linked to the internal 
%
% Constants:
%       - cc: treated connected component. (cc/1 gives existing cc)
%       -  k: current step of treatment (first step is 1)
%       - lowerbound: the minimal score
%       - upperbound: the maximal score
%
% Input (from findbestclique or findbestbiclique and postprocessing):
%       - newconcept(cc,k,T,X): X is the member of the set T in the concept cc at step k.
%       - clique(cc,k): concept is a clique.
%       - star(cc,k,T): set T of concept is a star.
% Output:
%       - score(S): concept cc at step k is a motif of score S.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%     EFFECTIVE SCORING         %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% number of node in each set.
size_set(T,N):- N={newconcept(cc,k,T,_)} ; T=1..2 ; N<=max_set_size.

% maximization of x'.
#maximize{S@1,S:size_set(1,S)}.

% maximization of x''.
#maximize{S@1,S:size_set(2,S)}.

% minimization of ẋ' - x''.
outside_neighbor(X):- inter(I,X) ; newconcept(cc,k,_,I) ; not newconcept(cc,k,_,X) ; not clique(cc,k).
outside_neighbor(X):- star(cc,k,T) ; newconcept(cc,k,T,I) ; inter(I,X) ; not newconcept(cc,k,_,X).
nb_outside_neighbor(N):- N={outside_neighbor(_)} ; not clique(cc,k).

#minimize{S@1,S:nb_outside_neighbor(S)}.



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%   REGULAR SCORE COVER         %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Are covered all edges of concept that link two nodes of different sets.
covered(cc,k,X,Y):- newconcept(cc,k,T,X) ; newconcept(cc,k,3-T,Y) ; X<Y ; T=1..2.

% Node count in each set of the biclique is given by summing weights of all nodes.
% Edge cover is the number of node covered by the set.
edgecover(cc,k,T,N):- size_set(T,N).

% Concept score, equal to maximal score - edge cover.
score(N):- N=upperbound-(N1*N2); N>=0   ; not clique(cc,k)    ;
           edgecover(cc,k,1,N1) ; edgecover(cc,k,2,N2).
score(N):- N=upperbound-((N1*(N1-1))/2) ; N>=0 ; clique(cc,k) ;
           N1={newconcept(cc,k,1,X)}.


% Exclusion of concepts with not enough nodes.
%  The lowerbound is equals to 1 at least,
%  and determined by the scorebound ASP program.
%  The upperbound is the min between the number of remaining edges
%  in the connected component and the size of the previous concept.
:- score(S) ; S>upperbound-lowerbound.
:- not score(_).

% Discard cases when no score is generated
:- size_set(1,0).
:- size_set(2,0).
