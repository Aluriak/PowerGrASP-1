coedge(X,Y):- not edge(X,Y) ; X<Y ; edge(X,_) ; edge(_,Y).


% Choice of elements in set 1 and 2 of the bipartite stable
1 { stable(1,X): coedge(X,_)}.
1 { stable(2,Y): coedge(_,Y)}.

% A node is impossible in a set if not linked to some node in the other set
imp(1,X):- coedge(X,_), stable(2,Y), not coedge(X,Y), X!=Y.
imp(2,Y):- coedge(_,Y), stable(1,X), not coedge(X,Y), X!=Y.

% Consistency ; no impossible element can be added to the stable
:- imp(T,X), stable(T,X).

% Maximality  ; all possible elements have to be added to the stable
:- not imp(1,X), not stable(1,X), coedge(X,_).
:- not imp(2,Y), not stable(2,Y), coedge(_,Y).

size(T,N):- N={stable(T,_)} ; T=1..2.
score(S):- S=N1*N2 ; size(1,N1) ; size(2,N2).

#maximize{S@1:score(S)}.

#show.
#show stable/2.
