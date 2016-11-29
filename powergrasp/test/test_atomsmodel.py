
import unittest

from powergrasp import atoms as atoms_module
from powergrasp.atoms import AtomsModel, ASPAtom


class TestASPAtom(unittest.TestCase):

    def test_only(self):
        atom = ASPAtom('oedge', [1, 2])
        self.assertEqual(atom.name, 'oedge')
        self.assertSequenceEqual(atom.args, [1, 2])
        with self.assertRaises(ValueError) as ctxt:
            atom.only_arg


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

        b_name, b_args = model.get_only('b')
        self.assertEqual(b_name, 'b')
        self.assertSequenceEqual(b_args, ('"ah?bon."', '5'))


    def test_builder_cons(self):
        data = (('p', ['1']), ('p', ['2']), ('abcde', ('1', '"fgh"')))
        model = AtomsModel(data)

        name, args = model.get_only('abcde')
        self.assertEqual(name, 'abcde')
        self.assertSequenceEqual(args, ('1', '"fgh"'))

        p_atoms = model.get('p')
        for name, args in p_atoms:
            self.assertEqual(name, 'p')
            self.assertIn(list(args), (['1'], ['2']))
