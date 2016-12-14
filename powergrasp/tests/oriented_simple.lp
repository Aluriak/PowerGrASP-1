% biclique {a,b} × {c,d}
edge((a;b),(c;d)).

% biclique {a,b} × {c,d,e} unless oriented compression
edge(a,e).
edge(e,b).  % not perfectly symmetric
