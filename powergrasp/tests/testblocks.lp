
% external clique
edge((a;b;c;d;e),(a;b;c;d;e)).

% external clique 2
edge((f;g;h;i;j;k),(f;g;h;i;j;k)).

% biclique of 4 elements of clique 1 and 2
edge(f,(a;b;c;d)).

% biclique of 4 elements of previous biclique and one external element
edge(l,f).
edge(l,g).
edge(l,h).
