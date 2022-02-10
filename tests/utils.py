import sys
import pytest
from enaml.core.enaml_compiler import EnamlCompiler
from enaml.core.parser import parse
from faker import Faker

try:
    from enaml.compat import exec_
except ImportError:
    if sys.version_info.major == 3:
        import builtins

        exec_ = getattr(builtins, "exec")

    else:

        def exec_(code, globs=None, locs=None):
            """Execute code in a namespace."""
            if globs is None:
                frame = sys._getframe(1)
                globs = frame.f_globals
                if locs is None:
                    locs = frame.f_locals
                del frame
            elif locs is None:
                locs = globs
            exec("""exec code in globs, locs""")


faker = Faker()


def compile_source(source, item, filename="<test>", namespace=None):
    """Compile Enaml source code and return the target item.
    Parameters
    ----------
    source : str
        The Enaml source code string to compile.
    item : str
        The name of the item in the resulting namespace to return.
    filename : str, optional
        The filename to use when compiling the code. The default
        is '<test>'.
    namespace : dict
        Namespace in which to execute the code
    Returns
    -------
    result : object
        The named object from the resulting namespace.
    """
    ast = parse(source, filename)
    code = EnamlCompiler.compile(ast, filename)
    namespace = namespace or {}
    exec_(code, namespace)
    return namespace[item]
