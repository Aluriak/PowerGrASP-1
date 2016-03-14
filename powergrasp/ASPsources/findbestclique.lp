%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Find best clique from preprocessed information on the non-covered graph
%
% initial version:  09/12/2014   J. Nicolas
% revised version:  07/07/2015   L. Bourneuf
%
% Constants:
%       - cc: treated connected component. (cc/1 gives existing cc)
%       -  k: current step of treatment (first step is 1)
%
% Input:
%       - inter(X,Y): there exist an edge linking X and Y in cc.
%       - oedge(X,Y): there exist an oriented edge linking X and Y in cc.
%       - membercc(Y): Y is a member of cc.
% Output:
%       - newconcept(cc,k,1,X): X is the member of the clique cc at step k.
%       - clique(cc,k): concept is a clique.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%% CONCEPTS %%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Clique of 3 elements
clique3:- inter(X,Y); inter(Y,Z); inter(X,Z).

% Choice of a  clique of at least 3 elements
3 {newconcept_nohidden(cc,k,1,X): membercc(X)}:- clique3.

% Consistency of the clique
:- newconcept_nohidden(cc,k,1,X); newconcept_nohidden(cc,k,1,Y); X<Y; not inter(X,Y).

% Maximality of the clique
:- clique3 ; membercc(X); not newconcept_nohidden(cc,k,1,X) ;
   inter(X,Y): newconcept_nohidden(cc,k,1,Y).

% Compatibility with postprocessing: newconcept_nohidden(cc,k,2,X) exists
newconcept(cc,k,2,X):- newconcept(cc,k,1,X).


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%% CONCEPT EXPANSION %%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Choose one hidden node for each node in newconcept that hide other nodes
1 { hidden_used(X,Y): equiv(X,Y) } 1:-  newconcept_nohidden(cc,k,1,X) ; equiv(X,_).

% Use an hidden node instead of any node with a weight >= 2.
% This will decrease the score of this last.
newconcept(cc,k,T,X):- newconcept_nohidden(cc,k,T,X) ; not equiv(X,_).
newconcept(cc,k,T,Y):- newconcept_nohidden(cc,k,T,X) ; equiv(X,Y) ; hidden_used(X,Y).


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%% CONCEPT PROPERTIES %%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% The found concept is a clique.
clique(cc,k).
