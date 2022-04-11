# Class for exceptions

# Exception rasied whenever the configuration file is determined to be malformed
class GrammarError(Exception):
    def __init__(self, *args):
        super().__init__(args)

# Exception raised whenever the source file we are compiling has a syntax error
class SourceSyntaxError(Exception):
    def __init__(self, *args):
        super().__init__(args)
