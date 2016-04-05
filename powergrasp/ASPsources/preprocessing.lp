%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Common definitions of findbestbiclique and findbestclique.
%
% Constants:
%       - cc: treated connected component. (cc/1 gives existing cc)
%       -  k: current step of treatment (first step is 1)
%
% Input:
%       - oedge(X,Y): there exist an oriented edge linking X and Y in cc.
%       - membercc(Y): Y is a member of cc.
% Output:
%       - inter(X,Y): there exist an edge linking X and Y in cc.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


% Symetric edges.
inter(X,Y):- oedge(X,Y).
inter(X,Y):- inter(Y,X).
