%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Find best biclique from preprocessed information on the non-covered graph
%
% initial version:  09/12/2014   J. Nicolas
% revised version:  29/04/2015   L. Bourneuf
% revised version:  08/07/2015   L. Bourneuf
%
% Input:
%       - oedge(X,Y): there exist an oriented edge linking X to Y in cc.
%       - membercc(cc,Y): Y is a member of cc.
% Output:
%       - newconcept(cc,k,T,X): X is the member of the set T in the concept cc at step k.
%       - star(cc,k,T): set T of concept is a star.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#program findbestbiclique(cc,k).



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%% CONCEPTS %%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Choice of the minimum of the concept
1{minobj(cc,k,X):membercc(cc,X)}1.

% Choice of elements in part 1
newconcept(cc,k,1,X):- minobj(cc,k,X).
{ newconcept(cc,k,1,X): membercc(cc,X), Min<X }:- minobj(cc,k,Min).

% Choice of elements in part 2
1 { newconcept(cc,k,2,Y): oedge(Min,Y), Min<=Y } :- minobj(cc,k,Min).

% Impossible element in a concept
%  a node is impossible if not linked to some node of other part
imp(k,3-T,X):- membercc(cc,X); newconcept(cc,k,T,Y) ; not oedge(X,Y) ; not oedge(Y,X).
%  a node is impossible if in a block different from another element in the same set
imp(k,T,X):- newconcept(cc,k,T,X) ; newconcept(cc,k,T,Y) ; parent_block(B,T) ;
             include_block(k-1,B,P) ; not block(k-1,P,X) ; block(k-1,P,Y) ; X!=Y.

% Consistency ; no impossible element can be added to the concept
:- imp(k,T,Y); newconcept(cc,k,T,Y).

% Maximality  ; all possible elements have to be added to the concept
%:- not imp(k,T,X); not newconcept(cc,k,T,X) ; T=1..2; membercc(cc,X).


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%% CONCEPT PROPERTIES %%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% a star is a biclique with one powernode composed of only one node
star(cc,k,T):- 1 { newconcept(cc,k,T,X) } 1 ; T=1..2.
:- star(cc,k,3-T) ; star(cc,k,T) ; T=1..2. % link between two nodes will not be treated as a interesting case



