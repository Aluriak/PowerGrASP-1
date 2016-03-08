% first biclique
edge((a;d;d2),(b;c;e;q;o)).
edge(b,c).

% second biclique
edge((i;h),(f;g;j;l;p)).
edge(f,g).

% m and n are linked to l,p,q and o
edge((m;m2;n),(l;p;q)).

% m, m2 and n is a clique
edge(n,(m;m2)).
