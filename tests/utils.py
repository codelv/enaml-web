from enaml.core.enaml_compiler import EnamlCompiler
from enaml.core.parser import parse
from faker import Faker

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
    exec(code, namespace)
    return namespace[item]
