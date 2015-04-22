#program model(cc).
#external step(k).
concomp(cc).


  concept(cc,k,z(I),T,X) :- step(k); concomp(cc); concept(cc,k,b(I,1),T,X).
  concept(cc,k,s(I),T,X) :- step(k); concomp(cc); concept(cc,k,b(I,2),T,X).

   clique(cc,k,z(I),X)   :- step(k); concomp(cc); clique(cc,k,c(I,1),X)   .
   clique(cc,k,s(I),X)   :- step(k); concomp(cc); clique(cc,k,c(I,2),X)   .

edgecover(cc,k,b(z(I)),N):- step(k); concomp(cc); edgecover(cc,k,b(I,1),N).
edgecover(cc,k,b(s(I)),N):- step(k); concomp(cc); edgecover(cc,k,b(I,2),N).
edgecover(cc,k,c(z(I)),N):- step(k); concomp(cc); edgecover(cc,k,c(I,1),N).
edgecover(cc,k,c(s(I)),N):- step(k); concomp(cc); edgecover(cc,k,c(I,2),N).


%#show groundedclique(cc,k,I,X): clique(cc,k,I,X).
%#show groundedconcept(cc,k,I,T,X): concept(cc,k,I,T,X); concomp(cc); step(k).
#show edgecover/4.

