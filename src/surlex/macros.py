from surlex.exceptions import MacroDoesNotExist

class MacroRegistry(object):
    macros = {}
    def __init__(self, macros={}):
        all_macros = {}
        all_macros.update(self.macros)
        all_macros.update(macros)
        self.macros = all_macros

    def get(self, macro_name):
        try:
            return self.macros[macro_name]
        except KeyError:
            raise MacroDoesNotExist('Macro "%s" not defined' % macro_name)

    def set(self, macro_name, regex):
        self.macros[macro_name] = regex

class DefaultMacroRegistry(MacroRegistry):
    global_macros = {}

    def __init__(self):
        super(DefaultMacroRegistry, self).__init__({
            'Y': r'\d{4}', # year, including century
            'y': r'\d{2}', # year, not including century
            'M': r'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)', # month, abbreviated
            'm': r'(0?([1-9])|10|11|12)', # month, 1 or 2 digit
            'd': r'((0|1|2)?([1-9])|[1-3]0|31)', # day, 1 or 2 digit
            '#': r'\d+', # number, any length
            's': r'[\w-]+', # slug
            'u': r'[a-fA-F0-9]{8}-?[a-fA-F0-9]{4}-?[a-fA-F0-9]{4}-?[a-fA-F0-9]{4}-?[a-fA-F0-9]{12}', # uuid
        })

    @classmethod
    def register(cls, macro, regex):
        cls.global_macros[macro] = regex

    def get(self, macro_name):
        try:
            return super(DefaultMacroRegistry, self).get(macro_name)
        except MacroDoesNotExist:
            try:
                return self.__class__.global_macros[macro_name]
            except KeyError:
                raise MacroDoesNotExist('Macro "%s" not defined' % macro_name)

