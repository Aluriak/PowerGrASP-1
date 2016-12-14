"""Definition of motif comparision functions

"""


from . import FoundMotif


def by_score(ma:FoundMotif, mb:FoundMotif):
    """Return model that have the greater score, or ma on equality"""
    if not isinstance(ma, FoundMotif) and ma is not None:
        print('ASSERT:', ma, type(ma), FoundMotif)
        assert isinstance(ma, FoundMotif) and ma is not None
    if not isinstance(mb, FoundMotif) and mb is not None:
        print('ASSERT:', mb, type(mb), FoundMotif)
        assert isinstance(mb, FoundMotif) and mb is not None
    ma_score = ma.score if ma else 0
    mb_score = mb.score if mb else 0
    return ma if ma_score >= mb_score else mb
