%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Find best biclique from preprocessed information on the non-covered graph
% Input data includes stable/2 atoms.
%
% Constants:
%       - cc: treated connected component. (cc/1 gives existing cc).
%       -  k: current step of treatment (first step is 1).
%       - upperbound: the maximal reachable cover.
%       - max_set_size: the maximal reachable size of a set.
% Input:
%       - inter(X,Y): there exist an edge linking X and Y in cc.
%       - edge(X,Y): there exist a edge linking X and Y in cc (X<Y).
%       - membercc(Y): Y is a member of cc.
%       - stable(N,X): node X is in part N of the stable (N in [1;2]).
% Output:
%       - newconcept(cc,k,T,X): X is the member of the set T in the concept cc at step k.
%       - star(cc,k,T): set T of concept is a star.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%% CONCEPTS %%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Symetric edges.
inter(X,Y):- edge(X,Y).
inter(X,Y):- inter(Y,X).

out_extent(O):- inter(O,_), not stable(1,O), in_intent(A), not inter(O,A).
out_extent(O):- inter(O,_), not stable(2,A), in_intent(A), not inter(O,A).
out_extent(O):- stable(1,O), stable(2,A), in_intent(A).
 in_extent(O):- inter(O,_), not out_extent(O).

out_intent(A):- inter(_,A), not stable(2,A), in_extent(O), not inter(O,A).
out_intent(A):- inter(_,A), not stable(1,O), in_extent(O), not inter(O,A).
out_intent(A):- stable(1,O), stable(2,A), in_extent(O).
 in_intent(A):- inter(_,A), not out_intent(A).

newconcept(cc,k,1,O):- in_extent(O).
newconcept(cc,k,2,A):- in_intent(A).


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%% CONCEPT PROPERTIES %%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% a star is a biclique with one powernode composed of only one node
%star(cc,k,T):- 1 { newconcept(cc,k,T,X): weight(X,1) } 1 ; T=1..2.
star(cc,k,T):- 1 { newconcept(cc,k,T,X) } 1 ; T=1..2.
:- star(cc,k,3-T) ; star(cc,k,T) ; T=1..2. % link between two nodes will not be treated as a interesting case
