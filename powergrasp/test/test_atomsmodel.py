
import unittest

from powergrasp import atoms as atoms_module
from powergrasp.atoms import AtomsModel, ASPAtom


class TestASPAtom(unittest.TestCase):

    def test_general(self):
        atom = ASPAtom('edge', [1, 2])
        self.assertEqual(atom.name, 'edge')
        self.assertSequenceEqual(atom.args, [1, 2])
        with self.assertRaises(ValueError) as ctxt:
            atom.only_arg

    def test_only(self):
        atom = ASPAtom('cc', [2])
        self.assertEqual(atom.name, 'cc')
        self.assertSequenceEqual(atom.args, [2])
        self.assertEqual(atom.only_arg, 2)


class TestAtomsFunctions(unittest.TestCase):

    def test_atoms_from_aspstr(self):
        atoms = atoms_module.atoms_from_aspstr('p.a(1).a(2).b("ah?bon.",5).')
        self.assertSequenceEqual(
            sorted(tuple(atoms)),
            [('a', ('1',)), ('a', ('2',)), ('b', ('"ah?bon."', '5')), ('p', ())]
        )


class TestAtomsModel(unittest.TestCase):

    def test_builder_string(self):
        model = AtomsModel.from_('p.a(1).a(2).b("ah?bon.",5).')
        p_name, p_args = model.get_only('p')
        self.assertEqual(p_name, 'p')
        self.assertEqual(p_args, ())

        atoms_a = model.get('a')
        for name, args in atoms_a:
            self.assertEqual(name, 'a')
            self.assertIn(list(args), (['1'], ['2']))

        atoms_ap = model.get(('a', 'p'))
        for name, args in atoms_ap:
            self.assertIn(name, ('a', 'p'))
            self.assertIn(list(args), (['1'], ['2'], []))

        self.assertSetEqual(set(model.get_unique_args('a')), {'1', '2'})

        b_name, b_args = model.get_only('b')
        self.assertEqual(b_name, 'b')
        self.assertSequenceEqual(b_args, ('"ah?bon."', '5'))


    def test_builder_graph(self):
        model = AtomsModel.from_({1: (2, 3)})
        self.assertSetEqual(set(model.get_args('edge')), {(1, 2), (1, 3)})


    def test_builder_cons(self):
        data = (('p', ['1']), ('p', ['2']), ('abcde', ('1', '"fgh"')), ('a', [1]))
        model = AtomsModel(data)

        name, args = model.get_only('abcde')
        self.assertEqual(name, 'abcde')
        self.assertSequenceEqual(args, ('1', '"fgh"'))

        self.assertEqual(model.get_unique_only_arg('a'), 1)
        self.assertSetEqual(set(model.get_unique_args('a')), {1})
        self.assertSetEqual(set(model.get_unique_args('p')), {'1', '2'})

        p_atoms = model.get('p')
        for name, args in p_atoms:
            self.assertEqual(name, 'p')
            self.assertIn(list(args), (['1'], ['2']))


    def test_set(self):
        data = (('p', ['1']), ('p', ['2']), ('abcde', ('1', '"fgh"')), ('a', [1]))
        model = AtomsModel(data)

        self.assertEqual(model.counts['p'], 2)
        self.assertEqual(model.counts['a'], 1)
        self.assertEqual(model.counts['abcde'], 1)

        new_args = ((0,), (1,), (2,))
        model.set_args('p', new_args)
        self.assertEqual(set(model.get_args('p')), set(new_args))

        self.assertEqual(model.counts['p'], 3)
