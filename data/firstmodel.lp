%*
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%Compile concepts and cliques

Input:
        - 
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
*%

#program firstmodel(cc,model_number).

clique(cc,1,model_number,X)      :-     clique(cc,X).
concept(cc,1,model_number,T,X)   :-  concept(cc,T,X).
edgecover(cc,1,b(model_number),N):- edgecoverb(cc,N).
edgecover(cc,1,c(model_number),N):- edgecoverc(cc,N).


%#show igroundedclique(cc,1,I,X): clique(cc,1,I,X).
%#show igroundedconcept(cc,1,I,T,X): concept(cc,1,I,T,X).
#show edgecover/4.
#show concept/5.
#show clique/4.
