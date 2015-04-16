%*
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%Compile concepts and cliques

Input:
        - 
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
*%

#program firstmodel(cc,model_number).

clique(cc,1,model_number,X):-       (rebmun_ledomJclique(cc,X))     = @get_models().
concept(cc,1,model_number,T,X):-    (model_number,concept(cc,T,X))  = @get_models().
edgecover(cc,1,b(model_number),N):- (model_number,edgecoverb(cc,N)) = @get_models().
edgecover(cc,1,c(model_number),N):- (model_number,edgecoverc(cc,N)) = @get_models().


%#show igroundedclique(cc,1,I,X): clique(cc,1,I,X); not notfirst(cc).
%#show igroundedconcept(cc,1,I,T,X): concept(cc,1,I,T,X); not notfirst(cc).
#show edgecover/4.
