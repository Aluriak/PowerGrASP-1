"""Definition of the ConnectedComponent class.

Belongs to the main client API.
See recipes submodule in order to get usage examples.

"""


from powergrasp import motif
from powergrasp.atoms import AtomsModel


class ConnectedComponent:
    """A connected component in a graph. Created by Graph instance.

    Holds the graph itself, and many informations about compression,
    including predicted score bounds.

    """

    def __init__(self, cc_id:str, node_number:int, edge_number:int, atoms:str,
                 observers:iter, config:dict, minimal_score:int=2):
        """

        cc_id -- name of the connected component
        node_number -- number of node in the cc
        edge_number -- number of edge in the cc
        atoms -- name of the file containing the atoms, or the atoms themselves
        observers -- batch of observers that will be notify
        config -- a Configuration instance

        """
        self.name = str(cc_id)
        self.score_min, self.score_max = minimal_score, int(edge_number)
        self.config = config
        self._has_motif = True
        self.step = 1
        self._atoms = AtomsModel.from_(atoms)
        self.initial_edges_count = sum(1 for _ in self._atoms.get('oedge'))


    @property
    def remaining_edges_count(self):
        """Return the number of remaining edges"""
        return sum(1 for _ in self._atoms.get('oedge'))


    def search_motif(self, motif:motif.Motif, alt=None, constraints:str='',
                     best_motif:callable=motif.comparer.by_score):
        """Search for given motif inside the graph.
        If found, compare it to given alterntative,
        and return the best of the two by comparing their score.

        """
        found_motif = motif.search(
            input_atoms=str(self._atoms),
            score_min=self.score_min,
            score_max=self.score_max,
            step=self.step,
            cc=self.name,
        )
        self._has_motif = bool(alt and (found_motif.model or alt.model))
        return found_motif if alt is None else best_motif(found_motif, alt)


    def search_biclique(self, alt=None, constraints:str=''):
        """Return the best biclique found. Alias to search_motif
        with motif set to biclique.
        """
        return search_motif(Motif.BICLIQUE, alt=alt, constraints=constraints)

    def search_clique(self, alt=None, constraints:str=''):
        """Return the best clique found. Alias to search_motif
        with motif set to clique.
        """
        return search_motif(Motif.CLIQUE, alt=alt, constraints=constraints)


    def compress(self, found_motif:'FoundMotif'):
        """Modify self, based on given found motif"""
        if found_motif.model is None:
            self._has_motif = False
        else:
            found_motif.motif.compress(found_motif.model, self._atoms)


    @property
    def has_motif(self):
        """True if a motif has been found during last search"""
        return self._has_motif
