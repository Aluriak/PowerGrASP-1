%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Addon to add with the motif search and the postprocessing.
%  ensure that the produced concepts involves in priority nodes
%  with higher priority.
%
% Input specific to this addon:
%   priority(X,P): node X have a priority P.
%
% Input from motif search:
%   newconcept(cc,k,T,X): node X is in set T.
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Maximize the full concept priority as a sum of involved nodes priorities.
#maximize{P@2,X: newconcept(cc,k,_,X), priority(X,P)}.
