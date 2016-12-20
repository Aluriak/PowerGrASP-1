%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Addon to add with the motif search and the postprocessing.
%  ensure that the produced concepts involves at least one of the node
%  with higher priority.
%
% Input specific to this addon:
%   priority(X,P): node X have a priority P.
%   max_priority(X): node X have a priority P that is the max of all priorities.
%
% Input from motif search:
%   newconcept(cc,k,T,X): node X is in set T.
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


% at least one node of maximal priority is involved in the concept.
ok :- newconcept(cc,k,_,X) ; max_priority(X).
:- not ok.
