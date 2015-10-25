%*
Two obvious bicliques ((a,d) x (b,c,n,e)) and ((i,h) x (f,g,l)).
Linked by m, that create another biclique (m x (n,e)).
And clique (m,l).
*%

% first biclique
edge(a,b).
edge(a,c).
edge(a,e).
edge(a,n).
edge(d,b).
edge(d,c).
edge(d,e).
edge(d,n).

% internal clique
edge(b,c).
edge(b,e).
edge(b,n).
edge(c,e).
edge(c,n).

% second biclique
edge(i,f).
edge(i,g).
edge(f,g).
edge(f,h).
edge(g,h).
edge(i,l).
edge(h,l).

% link between l and n through m
edge(n,m).
edge(e,m).
edge(l,m).
