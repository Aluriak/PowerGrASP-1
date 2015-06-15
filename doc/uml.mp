input metauml;
beginfig(1);
    Begin.b;
    Activity.extract("Extract graph data", "from the input file");
    Activity.findbestconcept("Find the best concept");
    Activity.update("Update edge coverage");
    Branch.nomodel;
    Activity.format("Save generated concepts", "in output file");
    End.e;


    topToBottom(20)(b, extract, findbestconcept, update, nomodel, format, e);
    drawObjects(b, extract, findbestconcept, update, nomodel, format, e);


    clink(transition)(b, extract);
    clink(transition)(extract, findbestconcept);
    clink(transition)(findbestconcept, update);
    clink(transition)(update, nomodel);
    link(transition)(pathStepX(nomodel.e, findbestconcept.e, 80));
    clink(transition)(nomodel, format);
    clink(transition)(format, e);


    item(iGuard)("next concept")(obj.sw = nomodel.e + (20, 0));
    item(iGuard)("no more concept")(obj.nw = nomodel.s + (0, -4));
endfig;
end
