%*
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%Compile concepts and cliques

Input:
        - clique(cc,X): X is the member of the clique cc.
        - newconcept(cc,T,X): X is the member of the set T of the biclique cc.
        - edgecoverb(cc,N): score N of the biclique cc.
        - edgecoverc(cc,N): score N of the clique cc.
Output:
        - clique(cc,1,model_number,X): X belongs to clique cc at step 1.
        - concept(cc,1,model_number,T,X): X belongs to biclique cc in set T at step 1.
        - edgecover(cc,1,b(model_number),N): N edges covered by biclique cc at step 1.
        - edgecover(cc,1,c(model_number),N): N edges covered by clique   cc at step 1.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
*%

#program firstmodel(cc,model_number).

clique(cc,1,model_number,X)      :-     clique(cc,X).
concept(cc,1,model_number,T,X)   :-  concept(cc,T,X).
edgecover(cc,1,b(model_number),S):- edgecoverb(cc,S).
edgecover(cc,1,c(model_number),S):- edgecoverc(cc,S).


%#show igroundedclique(cc,1,I,X): clique(cc,1,I,X).
%#show igroundedconcept(cc,1,I,T,X): concept(cc,1,I,T,X).
#show edgecover/4.
#show concept/5.
#show clique/4.
#show model_number.
