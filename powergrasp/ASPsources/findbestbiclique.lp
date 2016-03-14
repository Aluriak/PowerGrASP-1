%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Find best biclique from preprocessed information on the non-covered graph
%
% initial version:  09/12/2014   J. Nicolas
% revised version:  29/04/2015   L. Bourneuf
% revised version:  08/07/2015   L. Bourneuf
%
% Constants:
%       - cc: treated connected component. (cc/1 gives existing cc)
%       -  k: current step of treatment (first step is 1)
% Input:
%       - inter(X,Y): there exist an edge linking X and Y in cc.
%       - oedge(X,Y): there exist an oriented edge linking X and Y in cc.
%       - membercc(Y): Y is a member of cc.
% Output:
%       - newconcept(cc,k,T,X): X is the member of the set T in the concept cc at step k.
%       - star(cc,k,T): set T of concept is a star.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%% CONCEPTS %%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
linked2(X,Z):- X!=Z ; inter(X,Y) ; inter(Y,Z).

% Choice of the minimum of the concept
1{minobj(cc,k,X):membercc(X)}1.

% Choice of elements in part 1
newconcept(cc,k,1,X):- minobj(cc,k,X).
{ newconcept(cc,k,1,X): membercc(X), Min<X }:- minobj(cc,k,Min).

% Choice of elements in part 2
1 { newconcept(cc,k,2,Y): inter(Min,Y), Min<=Y } :- minobj(cc,k,Min).

% An element in a set can't be in the other set.
:- newconcept(cc,k,1,X) ; newconcept(cc,k,2,X).

% Impossible element in a concept
%  a node is impossible if not linked to some node of other part
imp(k,3-T,X):- membercc(X); newconcept(cc,k,T,Y) ; not inter(X,Y) ; not inter(Y,X).
%  a node is impossible if not linked2 to some node of the same part
imp(k,T,X):- membercc(X); newconcept(cc,k,T,Y) ; not linked2(X,Y); X!=Y.
% Consistency ; no impossible element can be added to the concept
:- imp(k,T,Y); newconcept(cc,k,T,Y).


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%% CONCEPT PROPERTIES %%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% a star is a biclique with one powernode composed of only one node
%star(cc,k,T):- 1 { newconcept(cc,k,T,X): weight(X,1) } 1 ; T=1..2.
star(cc,k,T):- 1 { newconcept(cc,k,T,X) } 1 ; T=1..2.
:- star(cc,k,3-T) ; star(cc,k,T) ; T=1..2. % link between two nodes will not be treated as a interesting case
