%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Update the set of edges contained by the concept of current step,
%  in order to exclude all edges covered by the chosen powernode
%
% initial version:  09/12/2014   J. Nicolas
% revised version:  29/04/2014   L. Bourneuf
%
% Input:
%       - concept(cc,k,T,X):- X belongs to set T of cc at step k.
% Output:
%       - powernode(cc,k,N):- powernode cc at step k has a score of N.
%       - bcovered(cc,k,X,Y):- edge X to Y is covered by powernode cc at step k.
%       - covered(X,Y):- edge X to Y was covered.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#program edgeupdate(cc,k).

% Uses program parameters
concomp(cc).
step(k).


% Are covered all edges of concept that link two nodes of different set.
bcovered(cc,k,X,Y):- concept(cc,k,T,X) ; concept(cc,k,3-T,Y), X<=Y; T=1..2 ; step(k) ; concomp(cc).
:- bcovered(_,_,X,Y) ; X>Y.

% Powernode are composed of points
#show powernode(cc,k,T,X): concept(cc,k,T,X).

% New edges covered by powernode
covered(     X,Y):- bcovered(cc,k,X,Y).

#show bcovered/4.
#show  covered/2.
