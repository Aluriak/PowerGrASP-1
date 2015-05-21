%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Update the set of edges contained by the concept of current step,
%  in order to exclude all edges covered by the chosen powernode
%
% initial version:  09/12/2014   J. Nicolas
% revised version:  29/04/2014   L. Bourneuf
%
% Input:
%       - powernode(cc,k,T,X):- X belongs to set T of cc at step k.
% Output:
%       - bcovered(cc,k,X,Y):- edge X to Y is covered by powernode cc at step k.
%       - covered(X,Y):- edge X to Y was covered.
%       - ccedge(cc,X,Y): there exists an edge between X and Y in the
%                         subgraph corresponding to connected component cc
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#program edgeupdate(cc,k).

% Uses program parameters
concomp(cc).
step(k).

% Are covered all edges of concept that link two nodes of different set.
bcovered(cc,k,X,Y):- powernode(cc,k,T,X) ; powernode(cc,k,3-T,Y), X<=Y; T=1..2 ; step(k) ; concomp(cc).
:- bcovered(_,_,X,Y) ; X>Y.

% New edges covered by powernode
covered(X,Y):- bcovered(cc,k,X,Y).
covered(Y,X):- bcovered(cc,k,X,Y).

% All edges not covered
inter(X,Y):- ccedge(cc,X,Y) ; not covered(X,Y).
inter(X,Y):- ccedge(cc,Y,X) ; not covered(X,Y).

#show bcovered/4.
#show  covered/2.
#show  ccedge/3.
