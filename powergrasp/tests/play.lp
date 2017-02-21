
% First biclique {d,e}×{a,b,c,f,g}, equivalent to edge((d;e),(a;b;c;f;g)).
edge(d,a). edge(d,b). edge(d,c). edge(d,f). edge(d,g).
edge(e,a). edge(e,b). edge(e,c). edge(e,f). edge(e,g).

% Clique, equivalent to edge((j;kk;l;m;n;o),(j;kk;l;m;n;o)).
edge(j,j). edge(j,kk). edge(j,l).edge(j,m). edge(j,n). edge(j,o).
edge(kk,j). edge(kk,kk). edge(kk,l).edge(kk,m). edge(kk,n). edge(kk,o).
edge(l,j). edge(l,kk). edge(l,l).edge(l,m). edge(l,n). edge(l,o).
edge(m,j). edge(m,kk). edge(m,l).edge(m,m). edge(m,n). edge(m,o).
edge(n,j). edge(n,kk). edge(n,l).edge(n,m). edge(n,n). edge(n,o).

% Second biclique, {h,i}×{f,g,j,kk}
edge(h,f). edge(h,g). edge(h,j). edge(h,kk).
edge(i,f). edge(i,g). edge(i,j). edge(i,kk).

edge(h,i). edge(b,c).
