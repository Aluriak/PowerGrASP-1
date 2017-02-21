%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Addon to add with the motif search and the postprocessing.
%  ensure that the produced concepts does not overlap with a stable,
%  described with the stable/2 atoms.  (cf theorem implementation)
%
% Input specific to this addon:
%   stable(N,X): node X is in part N of the stable (N in [1;2]).
%
% Input from motif search:
%   newconcept(cc,k,T,X): node X is in set T.
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


:- stable(1,X) ; newconcept(cc,k,1,X) ; stable(2,Y) ; newconcept(cc,k,2,Y).
