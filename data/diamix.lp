%*
% Simple Test Graph with two components:
% One on (1,2,3,4), one on (a,b,c,d)
Cliques are (1,2,3) and (2,3,4)
Concepts are (1,4)X(2,3),  (2)X(1,3,4), (3)X(1,2,4),  (b)X(a,c) and (c)X(b,d)
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

%% Default case : (described above)
%edge(1,2).
%edge(1,3).
%edge(2,3).
%edge(2,4).
%edge(3,4).

%% link with next cc
%edge(4,5).

%% a big cc
%edge(5,6..8).
%edge(9,6..8).
%edge(7,5..6).
%edge(7,8..9).

%% something from default case
%edge(a,b).
%edge(b,c).
%edge(c,d).

%% translation of default case with letters
%% NB: letters can't be adressed like a..z !
%edge(a,b).
%edge(a,c).
%edge(b,c).
%edge(b,d).
%edge(c,d).

%edge(z,b).
%edge(z,c).
%edge(b,c).
%edge(b,d).
%edge(c,d).

edge("2HN4M", "32OE8").
edge("2HN4M", "KEI").
edge("32OE8", "KEI").
edge("32OE8", "BÉP").
edge("KEI", "BÉP").

%% translation of default case
%edge(m,n).
%edge(n,o).
%edge(o,p).
