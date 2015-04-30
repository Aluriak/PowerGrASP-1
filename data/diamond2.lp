%*
% Simple Test Graph with two components:
% One on (1,2,3,4), one on (a,b,c,d)
% Cliques are (1,2,3) and (2,3,4)
% Concepts are (1,4)X(2,3),  (2)X(1,3,4), (3)X(1,2,4),  (b)X(a,c) and (c)X(b,d)
% Solution cover : 1) (1,4)X(2,3)  2) (2,3)  3) (a,c)X(b)  4)
 update(1)...
concept(1,1,2,2). concept(1,1,2,3). concept(1,1,1,1). concept(1,1,1,4).
 update(2)...
clique(1,2,3). clique(1,2,2).

update(1)...
concept(a,1,2,b). concept(a,1,1,c). concept(a,1,1,a).
 update(2)...
concept(a,2,2,c). concept(a,2,1,d).

*%

% first biclique
edge(a,b).
edge(a,c).
edge(b,c).
edge(b,d).
edge(c,d).

% second biclique
edge(i,f).
edge(i,g).
edge(f,g).
edge(f,h).
edge(g,h).

% k is linked to first biclique
edge(a,k).
%edge(b,k).
%edge(c,k).
edge(d,k).

% l is linked to second biclique
edge(i,l).
%edge(f,l).
%edge(g,l).
edge(h,l).

% link between l and k
edge(k,l).
%edge(l,k).
