%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Post-treatments about powernodes for easier
%  conversion to bubble format.
%
% initial version:  19/05/2014   L. Bourneuf
%
% Input:
%       - powernode(cc,k,1..2,Y):- element Y is in powernode cc,k,1 or cc,k,2.
% Output:
%       - include(X,Y):- {power,}node Y is directly included in {power,}node X.
%       - trivial(CC,K,T):- powernode CC,K,T is composed of only one node.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#program inclusion.

node(X):- powernode(_,_,_,X).

% a powernode include another iff contains at least one node of it.
include(p(CC1,K1,T1),p(CC2,K2,T2)):- powernode(CC1,K1,T1,X) ; powernode(CC2,K2,T2,X) ; K1<K2.
% a powernode includes its nodes.
include(p(CC,K,T),X):- powernode(CC,K,T,X).

% direct inclusion.
direct_include(A,B):- include(A,B) ; not { include(A,Z) ; include(Z,B) }.

% A powernode is trivial if it contain only one node
trivial(CC,K,T):- powernode(CC,K,T,_) ; 1 {node(X)} 1.

% a {power,node} is on the top if not contains by any powernode
top(CC,K,T):- not direct_include(_,p(CC,K,T)) ; powernode(CC,K,T,_).
top(A):- node(A) ; not include(_,A).

% output
#show include_pwrn(C,K,T,D,L,R): direct_include(p(C,K,T),p(D,L,R)).
#show include_node(C,K,T,X): direct_include(p(C,K,T),X) , node(X).
#show top(CC,K,T): top(CC,K,T).
#show topnode(A): top(A).
#show trivial/3.
