import ast
import json

UNARY_OPS = (ast.UAdd, ast.USub)
BINARY_OPS = (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod)


"""Various Tools for tdarr_inform Usage."""


def checkattr(inst_obj, attrcheck):

    # Quick check of hasattr
    if hasattr(inst_obj, attrcheck):
        return True

    # Check if attribute is in dir list
    if attrcheck in [x for x in dir(inst_obj) if not x.startswith("__")]:
        return True

    return False


def is_jsonable(x):
    try:
        json.dumps(x)
        return True
    except Exception:
        return False


def is_arithmetic(s):
    def _is_arithmetic(node):
        if isinstance(node, ast.Num):
            return True
        elif isinstance(node, ast.Expression):
            return _is_arithmetic(node.body)
        elif isinstance(node, ast.UnaryOp):
            valid_op = isinstance(node.op, UNARY_OPS)
            return valid_op and _is_arithmetic(node.operand)
        elif isinstance(node, ast.BinOp):
            valid_op = isinstance(node.op, BINARY_OPS)
            return valid_op and _is_arithmetic(node.left) and _is_arithmetic(node.right)
        else:
            raise ValueError('Unsupported type {}'.format(node))

    try:
        return _is_arithmetic(ast.parse(s, mode='eval'))
    except (SyntaxError, ValueError):
        return False


def isint(x):
    try:
        a = float(x)
        b = int(a)
    except ValueError:
        return False
    else:
        return a == b


def isfloat(x):
    try:
        float(x)
    except ValueError:
        return False
    else:
        return True


def closest_int_from_list(lst, K):
    return lst[min(range(len(lst)), key=lambda i: abs(lst[i]-K))]
