%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Perform integrity tests on input data (edge/2)
% Returns atoms that describes possibles problems,
%  and the edge/2, corrected.
%
% revised version:  01/07/2015   L. Bourneuf
%
% Input:
%       - edge(X,Y): there exists an edge between X and Y in the graph
% Output:
%       - edge(X,Y): there exists a corrected and oriented edge between X and Y in the graph
%       - nb(edge,N): 
%       - nb(node,N): 
%       - nb(input_edge,N): 
%       - nb(repeatition,N): 
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


oedge(X,Y):- edge(X,Y) ; X<Y.
oedge(X,Y):- edge(Y,X) ; X<Y.
node(X):- edge(X,_).
node(Y):- edge(_,Y).

nb(node,N):-       N={node(X)   }.
nb(edge,N):-       N={oedge(_,_)}.
nb(input_edge,N):- N={edge(_,_) }.
nb(repeatition,K-L):- nb(edge,L) ; nb(input_edge,K).
bad(node, k):- node( k).  %  k is a constant used for step number
bad(node,cc):- node(cc).  % cc is a constant used for connected component reference

%#show edge(X,Y): oedge(X,Y).
#show nb/2.
#show bad/2.

