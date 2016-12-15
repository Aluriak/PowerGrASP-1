%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Find best biclique from preprocessed information on the oriented graph
%
% initial version:  09/12/2014   J. Nicolas
% revised version:  29/04/2015   L. Bourneuf
% revised version:  08/07/2015   L. Bourneuf
%
% Constants:
%       - cc: treated connected component. (cc/1 gives existing cc)
%       -  k: current step of treatment (first step is 1)
%       - upperbound: the maximal reachable cover
%       - max_set_size: the maximal reachable size of a set
% Input:
%       - edge(X,Y): there exist an oriented edge linking X to Y.
%       - membercc(Y): Y is a member of cc.
% Output:
%       - newconcept(cc,k,1,X): X is the member of the source set in the concept cc at step k.
%       - newconcept(cc,k,2,X): X is the member of the target set in the concept cc at step k.
%       - star(cc,k,T): set T is a star. (T=1..2)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% X and Y are both source of an edge linking to another node.
linked2(X,Y):- edge(X,Z) ; edge(Y,Z) ; X<Y.


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%% CONCEPTS %%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Choice of elements in source set
1 { first_elem(X): edge(X,_) } 1.
% 1 { second_elem(Y) } 1:- newconcept(cc,k,1,Y) ; X!=Y ; first_elem(X).
newconcept(cc,k,1,X):- first_elem(X).
0 { newconcept(cc,k,1,X): membercc(X), linked2(F,X) } :- first_elem(F).

% Choice of elements in target set
% 1 { newconcept(cc,k,2,Y): edge(F,Y), edge(S,Y) } :-  first_elem(F) ; second_elem(S).
1 { newconcept(cc,k,2,Y): edge(F,Y) } :-  first_elem(F).

% An element in a set can't be in the other set.
:- newconcept(cc,k,1,X) ; newconcept(cc,k,2,X).

% A node can't be in a set if not linked to a node of other set
:- newconcept(cc,k,1,X) ; newconcept(cc,k,2,Y) ; not edge(X,Y).


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%% CONCEPT PROPERTIES %%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% a star is a biclique with one powernode composed of only one node
%star(cc,k,T):- 1 { newconcept(cc,k,T,X): weight(X,1) } 1 ; T=1..2.
star(cc,k,T):- 1 { newconcept(cc,k,T,X) } 1 ; T=1..2.
:- star(cc,k,3-T) ; star(cc,k,T) ; T=1..2. % link between two nodes will not be treated as a interesting case
