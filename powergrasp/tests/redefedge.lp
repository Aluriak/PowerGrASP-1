% first steps: 10*6=60
edge((a1;a2;a3;a4;a5;a6;a7;a8;a9;a10),(g1;g2;g3;g4;g5;g6)).
edge((b1;b2;b3;b4;b5;b6;b7;b8;b9;b10),(h1;h2;h3;h4;h5;h6)).
edge((c1;c2;c3;c4;c5;c6;c7;c8;c9;c10),(i1;i2;i3;i4;i5;i6)).

% first step: 4*6=24
edge((a1;a2;a3;a4),(d1;d2)).
edge((a1;a2;a3;a4),(e1;e2)).
edge((a1;a2;a3;a4),(f1;f2)).

% second step: 6*2=12
edge((b1;b2;b3;b4;b5;b6),(d1;d2)).

% third step: 4*2=8
edge((c1;c2),(d1;d2)).
edge((c1;c2),(e1;e2)).
