"""Definition of the ConnectedComponent class.

Belongs to the main client API.
See recipes submodule in order to get usage examples.

"""


from powergrasp import utils
from powergrasp import motif
from powergrasp import commons
from powergrasp.atoms import AtomsModel
from powergrasp.observers import Signals


LOGGER = commons.logger()


class ConnectedComponent:
    """A connected component in a graph. Created by Graph instance.

    Holds the graph itself, and many informations about compression,
    including predicted score bounds.

    """

    def __init__(self, cc_id:str, cc_nb:int, node_number:int, edge_number:int, atoms:str,
                 observers:iter, config:dict, minimal_score:int=2):
        """

        cc_id -- name of the connected component
        cc_nb -- index/number of the connected component
        node_number -- number of node in the cc
        edge_number -- number of edge in the cc
        atoms -- name of the file containing the atoms, or the atoms themselves
        observers -- batch of observers that will be notify
        config -- a Configuration instance

        """
        self.observers = observers
        self.name, self.number = str(cc_id), int(cc_nb)
        self.score_min, self.score_max = minimal_score, int(edge_number)
        self.config = config
        self._has_motif = True
        self._last_step = 0
        self.step = 0
        self._atoms = AtomsModel.from_(atoms)
        self.initial_edges_count = sum(1 for _ in self._atoms.get('edge'))
        self._first_call = True
        self.validate()
        self.density = utils.density(self._atoms.counts['membercc'],
                                     self._atoms.counts['edge'])


    def validate(self):
        """Raise errors for different reasons"""
        def gen_nodes():
            for _, args in self._atoms.get('edge'):
                yield from args

        for node in gen_nodes():
            if node in commons.ASP_ARGS_NAMES:
                LOGGER.critical("A node in input data is named <{}>, which is "
                                "reserved. This is not expected.".format(node))
                exit(1)
            if node == '':
                LOGGER.critical("A node in input data is named with no "
                                "characters, i.e. is an empty string, which "
                                "is not expected.".format(node))
                exit(1)


    @property
    def remaining_edges_count(self):
        """Return the number of remaining edges"""
        return sum(1 for _ in self._atoms.get('edge'))


    def search_motif(self, motif:motif.Motif, alt=None, constraints:str='',
                     best_motif:callable=motif.comparer.by_score):
        """Search for given motif inside the graph.
        If found, compare it to given alterntative,
        and return the best of the two by comparing their score.

        Increment step number automatically if previous step was finished.
        (i.e. compressed)

        """
        # this is the first time that search is called since last compression
        if self._last_step == self.step:
            self.step += 1
            self.observers.signal(Signals.StepStarted)
        assert self._last_step < self.step
        if self._first_call:
            self._first_call = False
            self.observers.signal(connected_component_started=(self.number,
                                                               self.name,
                                                               self._atoms,
                                                               self.density))
        found_motif = motif.search(
            input_atoms=self._atoms,
            score_min=self.score_min,
            score_max=self.score_max,
            step=self.step,
            cc=self.name,
        )

        best_model = found_motif if alt is None else best_motif(found_motif, alt)
        # self._has_motif = bool(best_model)
        return best_model


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


    def compress(self, found:'FoundMotif', new_best_score:int=None):
        """Modify self, based on given found motif.

        Terminate the step.
        new_best_score -- if None, set max score to found.score.

        """
        if found.model is None:
            self._has_motif = False
            self.observers.signal(
                connected_component_stopped=self.remaining_edges,
                step_data_generated=([None] * 3),
            )
        else:  # there is a found model
            self._has_motif = True

            assert new_best_score is None or isinstance(new_best_score, int)
            self.score_max = found.score if new_best_score is None else new_best_score

            data = found.motif.compress(found.model, self._atoms)
            assert len(data['poweredge_count']) == 1, "Multiple poweredge_count/1 atoms were generated."
            assert len(data['powernode_count']) == 1, "Multiple powernode_count/1 atoms were generated."
            assert len(data['score']) == 1, "Multiple score/1 atoms were generated."
            LOGGER.debug("Connected Component model: " + str(self._atoms.counts))

            self.observers.signal(
                model_found=found,
                step_data_generated=(int(data['powernode_count'][0]),
                                     int(data['poweredge_count'][0]),
                                     int(data['score'][0]))
            )

        # end current step
        self._last_step = self.step
        self.observers.signal(Signals.StepStopped)
        self.observers.signal(Signals.StepFinalized)


    @property
    def has_motif(self):
        """True if a motif has been found during last search"""
        return self._has_motif

    @property
    def remaining_edges(self):
        return AtomsModel(self._atoms.get('edge'))
