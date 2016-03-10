graph [
	comment "This is a sample graph"
	directed 1
	id 42
	label "Hello, I am a graph"
	node [
		id 1
		label "node1"
		thisIsASampleAttribute 42
	]
	node [
		id 2
		label "node2"
		thisIsASampleAttribute 43
	]
	node [
		id 3
		label "node3"
		thisIsASampleAttribute 44
	]
	edge [
		source 1
		target 2
		label "Edge from node1 to node2"
	]
	edge [
		source 2
		target 3
		label "Edge from node2 to node3"
	]
	edge [
		source 3
		target 1
		label "Edge from node3 to node1"
	]
]
