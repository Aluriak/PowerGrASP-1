% data from an uml class diagramme,
% where classes are nodes and links are edges.
% the uml can be found at wikipedia:
% https://upload.wikimedia.org/wikipedia/commons/1/14/LOM_base_schema.png

edge("LOMv1.0 schema",("1.General";
                       "2.Lifecycle";
                       "3.Meta-Metadata";
                       "4.Technical";
                       "5.Educational";
                       "6.Rights";
                       "7.Relation";
                       "8.Annotation";
                       "9.Classification")).
edge("Resource",("7.Relation";"Identifier")).
edge("Identifier",("1.General";"3.Meta-Metadata")).
edge("9.Classification","TaxonPath").
edge("TaxonPath","Taxon").
edge("Contribute",("2.Lifecycle";"3.Meta-Metadata")).
edge("Requirement",("4.Technical";"OrComposite")).
