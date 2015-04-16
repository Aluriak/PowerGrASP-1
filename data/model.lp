#program model(cc,k).


concept(cc,k,z(I),T,X) :- step(k); concomp(cc); newconcept(cc,k,b(I,1),T,X) = @get_models().
concept(cc,k,s(I),T,X) :- step(k); concomp(cc); newconcept(cc,k,b(I,2),T,X) = @get_models().
clique(cc,k,z(I),X):- step(k); concomp(cc); newclique(cc,k,c(I,1),X) = @get_models().
clique(cc,k,s(I),X):- step(k); concomp(cc); newclique(cc,k,c(I,2),X) = @get_models().
edgecover(cc,k,b(z(I)),N):- step(k); concomp(cc); newedgecover(cc,k,b(I,1),N) = @get_models().
edgecover(cc,k,b(s(I)),N):- step(k); concomp(cc); newedgecover(cc,k,b(I,2),N) = @get_models().
edgecover(cc,k,c(z(I)),N):- step(k); concomp(cc); newedgecover(cc,k,c(I,1),N) = @get_models().
edgecover(cc,k,c(s(I)),N):- step(k); concomp(cc); newedgecover(cc,k,c(I,2),N) = @get_models().


%#show groundedclique(cc,k,I,X): clique(cc,k,I,X).
%#show groundedconcept(cc,k,I,T,X): concept(cc,k,I,T,X); concomp(cc); step(k).
%#show edgecover/4.

