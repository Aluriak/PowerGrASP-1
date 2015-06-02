%*
Two obvious bicliques ((a,d) x (b,c,k,e)) and ((i,h) x (f,g,l)).
Linked by m, that create another biclique (m x (k,e)).
And clique (m,l).
*%

% first biclique
edge(a,b).
edge(a,c).
edge(a,e).
edge(a,k).
edge(d,b).
edge(d,c).
edge(d,e).
edge(d,k).

% internal clique
edge(b,c).
edge(b,e).
edge(b,k).
edge(c,e).
edge(c,k).

% second biclique
edge(i,f).
edge(i,g).
edge(f,g).
edge(f,h).
edge(g,h).
edge(i,l).
edge(h,l).

% link between l and k through m
edge(k,m).
edge(e,m).
edge(l,m).
