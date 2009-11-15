from grammer import Surlex
from macros import MacroRegistry, DefaultMacroRegistry

# This allows "surlex.register_macro" to register to the default registry
register_macro = DefaultMacroRegistry.register

def surlex_to_regex(surlex):
    return Surlex(surlex).translate()

def parsed_surlex_object(surlex):
    object = Surlex(surlex)
    object.translate()
    return object

def match(surlex, subject):
    return Surlex(surlex).match(subject)
