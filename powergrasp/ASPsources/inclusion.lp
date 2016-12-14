%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Post-treatments about powernodes for easier
%  conversion to bubble format.
%
% initial version:  19/05/2015   L. Bourneuf
%
% Input:
%       - powernode(cc,k,1..2,Y):- element Y is in powernode cc,k,1 or cc,k,2.
%       - poweredge(X,Y):- powernode X is linked to {power,}node Y.
%       - include_powernode(cc,K1,T1,K2,T2):- powernode cc,K1,T1 contains powernode cc,K2,T2.
%       - edge(X,Y):- there is an edge between nodes X and Y.
% Output:
%       - powernode(cc,k,1..2,Y):- element Y is in powernode cc,k,1 or cc,k,2 ;
%                               if cc,k,t is a clique, only cc,k,2 will be generated ;
%                               if cc,k,t is trivial, it will not be generated.
%       - edge(X,Y):- there is an edge between (power)nodes X and Y.
%       - include_node(C,K,T,X):- powernode C,K,T contains node X.
%       - include_pwrn(C,K,T,D,L,R):- powernode C,K,T contains powernode D,L,R.
%       - include(X,Y):- {power,}node Y is directly included in {power,}node X.
%       - trivial(CC,K,T):- powernode CC,K,T is composed of only one node. [DEBUG]
%       - top(CC,K,T):- powernode CC,K,T is contained by nothing.
%       - topnode(X):- node X is contained by nothing.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%#program inclusion.

node(X):- powernode(_,_,_,X).

% a powernode include another iff contains at least one node of it.
include(p(CC1,K1,T1),p(CC2,K2,T2)):- powernode(CC1,K1,T1,X) ; powernode(CC2,K2,T2,X) ; K1<K2.
%include(p(CC1,K1,T1),p(CC2,K2,T2)):- include_block(_,b(_,p(CC1,K1,T1)),b(_,p(CC2,K2,T2))).
% a powernode includes its nodes.
include(p(CC,K,T),X):- powernode(CC,K,T,X).

% direct inclusion.
direct_include(A,B):- include(A,B) ; not include(Z,B) : include(A,Z).

% A powernode is trivial if it contain only one node
trivial(CC,K,T):- powernode(CC,K,T,_) ; 1{ node(X) : powernode(CC,K,T,X) } 1.

% a {power,}node is on the top if not contains by any powernode
top(CC,K,T):- not direct_include(_,p(CC,K,T)) ; powernode(CC,K,T,_).
top(A):- node(A) ; not include(_,A).

% output
#show powernode(C,K,T,X): powernode(C,K,T,X) ; not clique(C,K).
#show powernode(C,K,1,X): powernode(C,K,_,X) ;     clique(C,K).
#show poweredge/4.
#show poweredge/5.
#show include_pwrn(C,K,T,D,L,R): direct_include(p(C,K,T),p(D,L,R)).
#show include_node(C,K,T,X): direct_include(p(C,K,T),X) , node(X).
#show top(CC,K,T): top(CC,K,T).
#show topnode(A): top(A).
#show trivial/3.
#show edge/2.  % edges in cc handled by compression
