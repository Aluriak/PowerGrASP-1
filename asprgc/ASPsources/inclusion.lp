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

% a powernode contain another iff have contains all nodes in it.
include_pwrn(p(CC1,K1,T1),p(CC2,K2,T2)):- powernode(CC2,K2,T2,_) ; powernode(CC1,K1,T1,X) ; not powernode(CC2,K2,T2,X).
% a powernode includes its nodes.
include_node(p(CC,K,T),X):- powernode(CC,K,T,X).

% direct inclusion.
direct_include_pwrn(A,B):- include_pwrn(A,B) ; not { include_pwrn(A,Z) ; include_pwrn(Z,B) }.
direct_include_node(A,B):- include_node(A,B) ; not { include_node(A,Z) ; include_node(Z,B) }.

% A powernode is trivial if it contain only one node
trivial(cc,k,T):- 1 {node(cc,k,T,X) : powernode(cc,k,T,X)} 1 ; T=1..2.

% output
#show include_pwrn(A,B): direct_include_pwrn(A,B).
#show include_node(A,B): direct_include_node(A,B).
#show top(A): not direct_include_node(_,A) ; powernode(_,_,_,A).
#show top(p(CC,K,T)): not direct_include_node(_,p(CC,K,T)) ; powernode(CC,K,T,_).
#show trivial/3.
