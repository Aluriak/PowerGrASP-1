
% external clique
edge(a,b).
edge(a,c).
edge(a,d).
edge(a,e).
edge(b,c).
edge(b,d).
edge(b,e).
edge(c,d).
edge(c,e).
edge(d,e).

% external clique 2
edge(f,g).
edge(f,h).
edge(f,i).
edge(f,j).
edge(g,h).
edge(g,i).
edge(g,j).
edge(h,i).
edge(h,j).
edge(i,j).

% biclique of 4 elements of clique 1 and 2
edge(a,f).
edge(b,f).
edge(c,f).

% biclique of three elements of previous biclique and one external element
edge(k,f).
edge(k,g).
edge(k,h).
