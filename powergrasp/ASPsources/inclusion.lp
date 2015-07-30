%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Post-treatments about powernodes for easier
%  conversion to bubble format.
%
% initial version:  19/05/2015   L. Bourneuf
%
% Input:
%       - powernode(cc,k,1..2,Y):- element Y is in powernode cc,k,1 or cc,k,2.
%       - poweredge(X,Y):- powernode X is linked to {power,}node Y.
%       - edge(X,Y):- there is an edge between nodes X and Y.
%       - powernode_inclusion(cc,K,T,L,U): powernode K,T includes powernode L,U in cc
% Output:
%       - powernode(cc,k,1..2,Y):- element Y is in powernode cc,k,1 or cc,k,2.
%       - edge(X,Y):- there is an edge between (power)nodes X and Y.
%       - include_node(C,K,T,X):- powernode C,K,T contains node X.
%       - include_pwrn(C,K,T,D,L,R):- powernode C,K,T contains powernode D,L,R.
%       - include(X,Y):- {power,}node Y is directly included in {power,}node X.
%       - trivial(CC,K,T):- powernode CC,K,T is composed of only one node. [DEBUG]
%       - top(CC,K,T):- powernode CC,K,T is contained by nothing.
%       - topnode(X):- node X is contained by nothing.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#program inclusion.

node(X):- powernode(_,_,_,X).

% a powernode include another iff contains at least one node of it.
include(p(CC,K,T),p(CC,L,U)):- powernode_inclusion(CC,K,T,L,U).
% a powernode includes its nodes.
include(p(CC,K,T),X):- powernode(CC,K,T,X).

% direct inclusion.
direct_include(A,B):- include(A,B) ; not include(Z,B) : include(A,Z).

% direct inclusions, depending of the included object
include_pwrn(C,K,T,C,L,R):- direct_include(p(C,K,T),p(C,L,R)).
include_node(C,K,T,X):- direct_include(p(C,K,T),X) ; node(X).

% a {power,}node is on the top if not contains by any powernode
top(CC,K,T):- not direct_include(_,p(CC,K,T)) ; powernode(CC,K,T,_).
top(A):- node(A) ; not include(_,A).

% impossible for a node to be direct included in more than one powernode
:- 2 { include_node(_,_,_,X) } ; node(X).
% powernodes can't perform reflexive includes
:- include_pwrn(C,K,T,C,L,R) ; include_pwrn(C,L,R,C,K,T).

% output
#show.
#show bug/2.
#show powernode/4.
#show poweredge/5.
#show poweredge/4.
#show include_pwrn/6.
#show include_node/4.
#show top/3.
#show topnode(A): top(A).
#show edge/2.
% debug
%#show include/2.
%#show powernode_inclusion/5.
%#show direct_include/2.
%%#show powernode(C,K,T,X): powernode(C,K,T,X) ; not clique(C,K).
%%#show powernode(C,K,1,X): powernode(C,K,_,X) ;     clique(C,K).
%#show edge(X,Y): ccedge(_,X,Y).
