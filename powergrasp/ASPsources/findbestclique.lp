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
%       - powernode(cc,k,1,X): X is the member of the concept cc at step k.
%       - poweredge(cc,K1,T1,K1,T1): powernode K1,T1 to itself.
%       - score(S): found concept is a clique of score S.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#program findbestclique(cc,k,lowerbound).

% Symetric and non-oriented edges
inter(X,Y):- oedge(X,Y).
inter(Y,X):- oedge(X,Y).

% Clique of 3 elements
clique3:- oedge(X,Y); oedge(Y,Z); oedge(X,Z).

% Choice of a  clique of at least 3 elements
3 {newclique(cc,X): membercc(cc,X)}:- clique3.

% Consistency of the clique
:- newclique(cc,X); newclique(cc,Y); X<Y; not oedge(X,Y).

% Maximality of the clique
:- membercc(cc,X); not newclique(cc,X); inter(X,Y):newclique(cc,Y) ; clique3.

% Compute score as the edge cover of the clique
edgecover((N*(N-1))/2):- N={newclique(cc,X):membercc(cc,X)} ; clique3.

% Maximize score
#maximize{S@1,S:edgecover(S)}.

% Discard clique if score is not interesting
:- edgecover(S) ; S<lowerbound.

% Discard model if have no score (no clique)
:- not edgecover(_).

% Outputs
#show.
#show powernode(cc,k,1,X): newclique(cc,X).
#show poweredge(cc,k,1,k,1): clique3.
#show score(S): edgecover(S).
