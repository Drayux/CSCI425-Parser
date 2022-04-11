import sys
from ParseExceptions import GrammarConfigError as ConfigError

# Set/List utility function (that isn't natively included for some reason?)
def find(s, i):
    arr = None
    if type(s) is list: arr = s
    elif type(s) is set:
        arr = [x for x in s]
    else: raise TypeError("Cannot retrieve elements from non-set type")

    for x in arr:
        if x == i:
            return x

    return None

# Rule class
class Grammar:
    def __init__(self, path):
        self.rules = {}                                 # Dict of lists of nonterminals/symbols
        self.empty = 'lambda'                           # Name of empty rule character (as seen in the config file)
        self.prodend = '$'                              # Character representing the end of production
        self.start = None                               # Name of entry rule
        self.nonterminals = []                          # Set of non-terminals (strings) : Keys of rules dict
        self.terminals = { self.empty, self.prodend }   # Set of terminals (strings)

        try: self.load(path, True)
        except ConfigError as ce:
            print("ERROR:", ce)
            exit(1)

    def __str__(self):
        ret = "-- GRAMMAR --\n"
        if self.start is None:
            ret += "EMPTY"
            return ret

        # Start symbol
        ret += f"START: {self.start}\n"

        # Grammar rules
        ruleno = 0
        for nt in self.nonterminals:
            for rule in self.rules[nt]:
                ret += f"  {ruleno} : \t{nt} ->"
                ruleno += 1

                for symbol in rule: ret += f" {symbol}"
                ret += "\n"

        # Nonterminals
        ret += "\nTERMINALS:\n "
        for t in self.terminals: ret += f" {t}"

        # Terminals
        ret += "\n\nNON-TERMINALS:\n "
        for t in self.nonterminals: ret += f" {t}"
        ret += "\n"

        return ret

    # Loads a grammar from a configuration file
    # strict -> Should the rules follow strict naming convention (nonterms must contain a capital)
    def load(self, path, strict = False):
        config = None
        with open(path, "r") as inf: config = [l.strip().split(' ') for l in inf]

        # Create a list of all of the nonterminal symbols
        # Nonterminals defined as anything that precedes an arrow ( -> )
        lineCount = 0
        for rule in config:
            lineCount += 1                  # For accurate error messages
            symbol = None
            try: symbol = rule[1]
            except IndexError: continue     # Empty line

            # Line contains a rulename
            if symbol == '->':
                symbol = rule[0]

                # Check for strict formatting rules
                if strict and symbol == symbol.lower():
                    raise ConfigError(f"Nonterminal '{symbol}' does not contain a capital letter ({path}: line {lineCount})")

                # Check for invalid characters...could be revised with stricter formatting
                if symbol == '->' or symbol == '|' or symbol == self.empty or symbol == self.prodend:
                    raise ConfigError(f"Unexpected symbol '{symbol}' at start of line {lineCount} ({path})")

                self.nonterminals.append(symbol)
                self.rules[symbol] = []

        # Build the dict of grammar rules
        rulename = None     # Key under which to place rules in the grammar dictionary
        for lc, rule in enumerate(config):
            # Empty line, skip
            if len(rule) == 0: continue
            symbol = rule.pop(0)

            # Rule with explicit name
            if symbol in self.nonterminals:
                # Check length (Needs to be at least 3, but we popped the first element)
                if len(rule) < 2: raise ConfigError(f"Invalid rule ({path}: line {lc})")
                rule.pop(0)     # Next token will be an arrow
                rulename = symbol

            # Config file syntax checking
            elif symbol != '|':
                raise ConfigError(f"Unexpected symbol '{symbol}' at start of line {lc} ({path})")

            # Iterate through the rest of the line
            # Determine token type (operator, non-terminal, or symbol)
            rewrite = []        # Actual rule associated with the rulename
            for token in rule:
                pointer = None

                # Alternation: Save the new rule
                if token == '|':
                    if len(rewrite) == 0:
                        raise ConfigError(f"Zero-length rule in line {lc} ({path})")

                    self.rules[rulename].append(rewrite)
                    rewrite = []
                    continue

                # End or production: Save rule as start goal
                if token == self.prodend:
                    if self.start is not None and self.start != rulename:
                        raise ConfigError(f"Multiple start symbols '{rulename}' and '{self.start}' ({path}: line {lc})")
                    elif self.start is None: self.start = rulename

                    # Use the same pointer
                    rewrite.append(self.prodend)
                    continue

                # Lambda rule: Can later be expanded to use special lamda char
                if token == self.empty:
                    if len(rewrite) > 0:
                        raise ConfigError(f"Unexpected lambda in nonempty rewrite rule ({path}: line {lc})")

                    rewrite.append(self.empty)
                    break

                # -- APPEND THE RULE COMPONENT --
                # Find the item in the set to return the same pointer, prevents memory duplicates
                pointer = find(self.nonterminals, token)

                # If nothing, token was a terminal
                if pointer is None:
                    if strict and (token != token.lower()):
                        raise ConfigError(f"Terminal '{token}' contains a capital letter ({path}: line {lc})")

                    self.terminals.add(token)
                    pointer = find(self.terminals, token)

                rewrite.append(pointer)

            if len(rewrite) == 0:
                raise ConfigError(f"Zero-length rule in line {lc} ({path})")
            self.rules[rulename].append(rewrite)

        # Ensure that the start rule is configured correctly
        if self.start is None: raise ConfigError(f"Grammar has no start symbol")
        for rule in self.rules[self.start]:
            symbol = rule[-1]
            if symbol != self.prodend:
                raise ConfigError(f"Inconsistent end of production rules, symbol: '{self.start}'")


if __name__ == "__main__":
    path = sys.argv[1]
    grammar = Grammar(path)

    print(grammar)
    print("test")
