%*
Two obvious bicliques ((a,d) x (b,c,k,e)) and ((i,h) x (f,g,l)).
Linked by m, that create another biclique (m x (k,e)).
And clique (m,l).
*%

% first biclique
edge(a,b).
edge(a,c).
edge(a,e).
edge(b,c).
edge(b,d).
edge(c,d).
edge(d,e).

% second biclique
edge(i,f).
edge(i,g).
edge(f,g).
edge(f,h).
edge(g,h).

% k is linked to first biclique
edge(a,k).
edge(d,k).

% l is linked to second biclique
edge(i,l).
edge(h,l).

% link between l and k through m
edge(k,m).
edge(e,m).
edge(l,m).
