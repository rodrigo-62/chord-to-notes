import ply.yacc as yacc
from chord_lexer import tokens


def p_All(p):
    r"""All : NOTE Pitch Quality Elements Inversion"""
    p[0] = (p[1], p[2], p[3], p[4], p[5])
    return p


def p_Pitch(p):
    r"""Pitch : PITCH
    |
    """
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = None
    return p


def p_Quality(p):
    r"""Quality : MIN
    | AUG
    | DIM
    | HALF_DIM7
    |
    """
    if len(p) == 1:
        p[0] = "M"
    else:
        p[0] = p[1]
    return p


def p_Elements(p):
    r"""Elements : Elements Element
    |
    """
    if len(p) == 1:
        p[0] = []
    else:
        p[0] = p[1] + [p[2]]
    return p


# PITCH Number causes a shift reduce conflict, resolved with shift
# Example: C#5 = C# 5 or C #5 ?
def p_Element(p):
    r"""Element : SUS SusAux
    | ADD AddAux
    | OMIT OmitAux
    | LPAREN SetElems RPAREN
    | SIX_NINE
    | MAJ MajorType
    """
    if len(p) == 2:
        p[0] = p[1]
    elif len(p) == 3:
        p[0] = (p[1], p[2])
    elif len(p) == 4:
        p[0] = ("set", p[2])
    return p


def p_Element2(p):
    r"""Element : Number"""
    p[0] = ("number", p[1])
    return p[0]


def p_Element3(p):
    r"""Element : PitchNumber"""
    p[0] = ("pitch_number", p[1])


def p_MajorType(p):
    r"""MajorType : SEVEN
    | NINE
    | ELEVEN
    | THIRTEEN
    """
    p[0] = p[1]
    return p


def p_PitchNumber(p):
    r"""PitchNumber : PITCH Number"""
    p[0] = p[1] + p[2]
    return p


def p_Number(p):
    r"""Number : TWO
    | THREE
    | FOUR
    | FIVE
    | SIX
    | SEVEN
    | NINE
    | ELEVEN
    | THIRTEEN
    """
    p[0] = p[1]
    return p


def p_SusAux(p):
    r"""SusAux : PITCH SusNumber
    | SusNumber
    """
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[1] + p[2]
    return p


def p_SusNumber(p):
    r"""SusNumber : TWO
    | FOUR
    """
    p[0] = p[1]
    return p


def p_AddAux(p):
    r"""AddAux : TWO
    | FOUR
    | SIX
    | NINE
    | ELEVEN
    | THIRTEEN
    """
    p[0] = p[1]
    return p


def p_OmitAux(p):
    r"""OmitAux : THREE
    | FIVE
    """
    p[0] = p[1]
    return p


def p_SetElems(p):
    r"""SetElems : SetElems COMMA SetElem
    | SetElem
    """
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]


def p_SetElem(p):
    r"""SetElem : PITCH Number
    | Number
    | OMIT OmitAux
    | ADD AddAux
    | MAJ MajorType
    """
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[1] + p[2]
    return p


def p_Inversion(p):
    r"""Inversion : SLASH NOTE
    | SLASH NOTE PITCH
    |
    """
    if len(p) == 1:
        p[0] = None
    elif len(p) == 3:
        p[0] = (p[1], p[2])
    elif len(p) == 4:
        p[0] = (p[1], p[2] + p[3])
    return p


def p_error(p):
    # print("Syntax error in input!", p)
    parser.exito = False


parser = yacc.yacc()
parser.exito = True
