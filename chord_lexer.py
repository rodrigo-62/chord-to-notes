import ply.lex as lex

tokens = (
    "NOTE",
    "PITCH",
    "MIN",
    "MAJ",
    "DIM",
    "AUG",
    "SLASH",
    "OMIT",
    "LPAREN",
    "RPAREN",
    "COMMA",
    "HALF_DIM7",
    "SUS",
    "ADD",
    "TWO",
    "THREE",
    "FOUR",
    "FIVE",
    "SIX",
    "SEVEN",
    "NINE",
    "ELEVEN",
    "THIRTEEN",
    "SIX_NINE",
)

t_ignore = " \n\t"


def t_NOTE(t):
    r"""C|D|E|F|G|A|B"""
    return t


def t_PITCH(t):
    r"""b{1,2}|\#{1,2}|x|♭{1,2}"""
    if t.value == "x":
        t.value = "##"
    t.value = t.value.replace("♭", "b")
    return t


def t_MAJ(t):
    r"""Maj|maj|Ma|M|Δ"""
    t.value = "M"
    return t


def t_MIN(t):
    r"""min|m|\-"""
    t.value = "m"
    return t


def t_DIM(t):
    r"""dim|º"""
    t.value = "dim"
    return t


def t_AUG(t):
    r"""aug|\+"""
    t.value = "aug"
    return t


def t_SLASH(t):
    r"""\/|\\"""
    t.value = "/"
    return t


def t_OMIT(t):
    r"""omit|no"""
    t.value = "no"
    return t


def t_LPAREN(t):
    r"""\("""
    return t


def t_RPAREN(t):
    r"""\)"""
    return t


def t_COMMA(t):
    r"""\,"""
    return t


def t_HALF_DIM7(t):
    r"""ø"""
    return t


def t_SUS(t):
    r"""sus"""
    return t


def t_ADD(t):
    r"""add"""
    return t


def t_SIX_NINE(t):
    r"""6\/9"""
    return t


def t_TWO(t):
    r"""2"""
    return t


def t_THREE(t):
    r"""3"""
    return t


def t_FOUR(t):
    r"""4"""
    return t


def t_FIVE(t):
    r"""5"""
    return t


def t_SIX(t):
    r"""6"""
    return t


def t_SEVEN(t):
    r"""7"""
    return t


def t_NINE(t):
    r"""9"""
    return t


def t_ELEVEN(t):
    r"""11"""
    return t


def t_THIRTEEN(t):
    r"""13"""
    return t


def t_error(t):
    # print(f"Illegal character '{t.value[0]}' at line {t.lineno}")
    raise lex.LexError(f"Illegal character '{t.value[0]}'", t.lineno)


def t_newline(t):
    r"""\n+"""
    t.lexer.lineno += len(t.value)


lexer = lex.lex()
