%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Find best clique from preprocessed information on the non-covered graph
%
% initial version:  09/12/2014   J. Nicolas
% revised version:  07/07/2015   L. Bourneuf
%
% Input:
%       - oedge(X,Y): there exist an oriented edge linking X to Y in cc.
%       - membercc(cc,Y): Y is a member of cc.
% Output:
%       - newconcept(cc,k,1,X): X is the member of the clique cc at step k.
%       - clique(cc,k): concept is a clique.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#program findbestclique(cc,k).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%% CONCEPTS %%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Symetric and non-oriented edges
inter(X,Y):- oedge(X,Y).
inter(Y,X):- oedge(X,Y).

% Clique of 3 elements
clique3:- oedge(X,Y); oedge(Y,Z); oedge(X,Z).

% Choice of a  clique of at least 3 elements
3 {newconcept(cc,k,1,X): membercc(cc,X)}:- clique3.

% Consistency of the clique
:- newconcept(cc,k,1,X); newconcept(cc,k,1,Y); X<Y; not oedge(X,Y).

% Maximality of the clique
:- membercc(cc,X); not newconcept(cc,k,1,X); inter(X,Y):newconcept(cc,k,1,Y) ; clique3.

% Compute score as the edge cover of the clique
edgecover((N*(N-1))/2):- N={newconcept(cc,k,1,X):membercc(cc,X)} ; clique3.

% Compatibility with postprocessing: newconcept(cc,k,2,X) exists
newconcept(cc,k,2,X):- newconcept(cc,k,1,X).



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%% CONCEPT PROPERTIES %%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
clique(cc,k).
