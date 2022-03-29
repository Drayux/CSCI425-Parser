import sys
from collections import deque

class TreeNode:
    def __init__(self, data, parent):
        self.data = data
        self.parent = parent
        self.children = []

    def add_as_rightmost_child(self, data):
        new_node = TreeNode(data, self)
        self.children.append(new_node)

    def get_rightmost_child(self):
        return self.children[-1]

# A class representing a Context Free Grammar
# Assume all fields in Constructor are present. You should just have to interface with this
class CFG:
    def __init__(self, cfg: dict, rules: list, terminals: set, start_symbol: str):
        self.cfg = cfg              # Dictionary with key : non-terminal, value : list of production results
        self.rules = rules          # List of tuple (non-terminal, production result)
        self.terminals = terminals  # Plus lambda; Non-terminals are keys in CFG
        self.start_symbol = start_symbol
        self.predict_sets = None    # List of tuple (tuple (non-terminal, production result), set of predict terminals)
        self.parse_table = None     # Table built as result of build_parse_table()

    def derives_to_lambda(self, L: str, T: deque = None) -> bool:
        if L == "lambda":
            return True

        if T is None:
            T = deque()

        prod_of_L = []
        # gets all productions with Non-Terminal L on LHS
        if L in self.cfg:
            prod_of_L = self.cfg[L]

        for production in prod_of_L:
            if production in T:  # if we have searched with that Non-Terminal before
                continue
            if production == 'lambda':
                return True
            terminal_in_production = False
            for term in production:
                if term in self.terminals:
                    terminal_in_production = True
                    break
            if terminal_in_production:
                continue

            all_derive_lambda = True
            # for each X_i (a non-terminal) in the production recurse
            # We know it's a non-terminal if it's in the cfg dictionary
            for X_i in production:
                if X_i not in self.cfg:
                    continue
                T.append(X_i)  # pushing non-terminal on T for recursive search
                all_derive_lambda = self.derives_to_lambda(X_i, T.copy())
                T.pop()
                # if one term in the RHS of the rule does not derive to Lambda the entire production can't
                if not all_derive_lambda: break

            if all_derive_lambda:
                return True

        return False

    # This allows easier checking and insertion into T
    def first_set(self, XB: str, T: set = None) -> (set, set):
        # Create the set if first call
        # T is set of grammar rules to ignore to prevent searching Non-Terminals already visited
        if T is None:
            T = set()

        X = XB.strip().split(' ')[0]
        if X == "lambda":
            return set(), T

        # X is a terminal symbol
        if X in self.terminals:
            return set(X), T

        F = set()
        if X not in T:
            T.add(X)
            productions = []
            if X in self.cfg:
                productions = self.cfg[X]  # all production with X in LHS
            for prod in productions:  # production are space delimited
                if prod == 'lambda': continue
                G, _ = self.first_set(prod, T.copy())
                F = F | G

        if self.derives_to_lambda(X) and len(XB[1:]) > 0:
            G, _ = self.first_set(XB[1:], T.copy())
            F = F | G

        return F, T

    # Return list of rules with rhs occurrences of non_terminal
    def find_rhs_occurrences(self, non_terminal: str) -> list:
        occurrences = []
        for (lhs, rhs) in self.rules:
            if non_terminal in rhs:
                occurrences.append((lhs, rhs))
        return occurrences

    # returns true a char c in character sequence is a part of non-terminals or terminals
    def pi_and_sigma_intersection(self, char_sequence: list) -> bool:
        for c in char_sequence:
            if c in self.terminals or c in self.cfg[c]:
                return True
        return False

    # derives to lambda true for all
    def derives_to_lambda_forall(self, char_sequence: list) -> bool:
        for c in char_sequence:
            if c == ' ': continue
            if not self.derives_to_lambda(c, deque()):
                return False
        return True

    def follow_set(self, A: str, T: set = None) -> (set, set):
        if T is None:
            T = set()
        if A in T:
            return set(), T

        T.add(A)
        follow_set = set()
        for lhs, rhs in self.find_rhs_occurrences(A):
            non_t_in_rhs = rhs.find(A, 0)
            pi = []
            while non_t_in_rhs != -1:
                pi.append(rhs[non_t_in_rhs + 1:].strip())
                non_t_in_rhs = rhs.find(A, non_t_in_rhs + 1)

            for p in pi:
                if len(p) > 0:
                    I = set()
                    G, _ = self.first_set(p, T)
                    follow_set = follow_set | G
                elif len(p) == 0 or (not self.pi_and_sigma_intersection(p) and self.derives_to_lambda_forall(p)):
                    G, _ = self.follow_set(lhs, T.copy())
                    follow_set = follow_set | G

        return follow_set, T

    def predict_set(self):
        self.predict_sets = []
        for lhs, rhs in self.rules:
            rule = (lhs, rhs)
            predict_set = self.first_set(rhs)[0]    # ignore the second set result since it's not needed

            # if rhs derives to lambda in more than 1 steps include follow of A
            if self.derives_to_lambda(rhs):
                predict_set = predict_set | self.follow_set(lhs)[0]

            self.predict_sets.append((rule, predict_set))

    def get_predict_set(self, rule):
        for prod_rule, pred_set in self.predict_sets:
            if prod_rule == rule:
                return pred_set

    # Following procedure FILLTABLE(LLTable) in Figure 5.9 on page 153 of the texbook
    def build_parse_table(self):
        self.parse_table = ParseTable(self)

    def build_parse_tree(self, P, ts, LLT):
        T = TreeNode('Root', None)
        K = []
        Current = T
        K.append(self.start_symbol)
        current_file_loc = 0
        while len(K) > 0:
            x = K.pop()
            #tok = ts.read(1)
            #ts.seek(current_file_loc)
            if x in self.cfg.keys():
                p = P[LLT.get_production(x, ts.peek().decode('utf-8'))]
                if p == -1:
                    print("Syntax Error! #1")
                    exit(1)
                K.append('MARKER')
                R = self.rules[p][1]
                for i in range(len(R), 0, -1):
                    K.append(R[i])
                n = [x, []]
                Current.add_as_rightmost_child(x)
                Current = Current[1][-1]
            elif x in self.terminals or x == 'lambda':
                if x in self.terminals:
                    if not x == ts.peek().decode('utf-8'):
                        print("Syntax Error! #2")
                        exit(1)
                    #x = tok
                    #current_file_loc += 1
                    #ts.seek(current_file_loc)
                    x = ts.pop()
                Current.add_as_rightmost_child(x)
            elif x == 'MARKER':
                Current = Current.parent
        return Current.children

class ParseTable:
    def __init__(self, grammar):
        self.data = None                # Renamed from table
        self.row_labels = []            # Renamed from N_indexes
        self.col_labels = []            # Renamed from T_indexes

        self.create_labels(grammar)     # Renamed from fill_indices
        self.populate(grammar)          # Renamed from fill_table
        # self.table = ([None] * len(self.T_indexes)) * len(self.N_indexes)

    def create_labels(self, grammar):
        for N in grammar.cfg.keys():
            self.row_labels.append(N)

        for T in grammar.terminals:
            self.col_labels.append(T)

        #print(self.N_indexes)
        #print(self.T_indexes)

    def populate(self, grammar):
        # N = G.cfg.keys()
        # for A in N:
        #    A_index = self.N_indexes.index(A)
        #    for p in G.cfg[A]:
        #        for a in G.predict_set(p):
        #            a_index = self.T_indexes.index(a)
        #            self.table[A_index][a_index] = p

        self.data = [[0] * len(self.col_labels) for i in range(len(self.row_labels))]
            for i in range(0, len(grammar.rules)):
                A, RHS = grammar.rules[i]
                A_index = self.row_labels.index(A)
                a_list = grammar.get_predict_set((A, RHS))

                # print((A, RHS))
                # print(a_list)

                if a_list == None:
                    continue

                for a in a_list:
                    a_index = self.col_labels.index(a)
                    self.data[A_index][a_index] = i

    # Return the production rule respective to the non-terminal and terminal entries
    def get_production(self, nonterminal, terminal):
        row = self.row_labels.index(nonterminal)
        column = self.col_labels.index(terminal)
        return self.data[row][column]


# file_name : a file in the cwd of the script
# returns : a list of lines with newlines extra spaces removed
def parse_file(file_name: str) -> list:
    result_list = []
    # open file and put it in an array of lines
    with open(file_name) as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            items = line.split(' ')
            items[-1] = items[-1].replace("\n", "")  # remove newline if exists
            for i in range(len(items) - 1, -1, -1):  # trim empty spaces
                if items[i] == '':
                    items.pop(i)
            result_list.append(' '.join(items))

    return result_list


# lines : a list of lines that describe production rules
# returns : a cfg dict
def generate_cfg(lines: list) -> dict:
    cfg = {}
    non_terminal = ""
    for line in lines:
        # production grab the non-terminal and add rules for it
        if '->' in line:
            split = line.index('->')
            non_terminal = line[:split].strip()
            rhs = line[2 + split:].strip()
            rules = rhs.split('|')
            for rule in rules:
                if non_terminal in cfg:
                    cfg[non_terminal].append(rule.strip())
                else:
                    cfg[non_terminal] = [rule.strip()]
        elif non_terminal != "":  # | on its own line with a previously specified non-terminal
            if "|" in line:
                rules = line.split('|')
                for rule in rules:
                    if rule != "":
                        cfg[non_terminal].append(rule.strip())

    return cfg


def main(file_name, token = None):
    lines = parse_file(file_name)
    cfg = generate_cfg(lines)

    ##########################################
    print("  -- GRAMMAR --")

    # Print start symbol
    start_symbol = ""
    for key, val in cfg.items():
        for result in val:
            if "$" in result:
                print("Start Symbol:", key)
                start_symbol = key
                break

    # Print all rules
    rules = []  # tuple of NonTerminal -> Result
    # print("Rules:")
    rule_num = 0
    for key, val in cfg.items():
        for result in val:
            rules.append((key, result))
            print("  ", rule_num, " : \t", key, "->", result)
            rule_num += 1

    # Print non-terminals:
    print("\nNon-terminals:\n  ", end = "")
    for key in cfg.keys():
        print(key, end = " ")
    print("")

    # Print terminals
    terminals = set()
    for key, val in cfg.items():
        for v in val:
            for value in v.split(' '):
                if value not in cfg and value != '$':  # if not a non terminal
                    terminals.add(value)

    print("\nTerminals:\n  ", end = "")
    for term in terminals:
        print(term, end = " ")
    print("\n")

    ##########################################
    print("\n  -- PREDICTION --")
    grammar = CFG(cfg, rules, terminals, start_symbol)
    grammar.predict_set()       # Update the grammar's predict sets

    # Output which non-terminals derive to lambda
    print("Derives to lambda:\n  ", end = "")
    for key in grammar.cfg.keys():
        if grammar.derives_to_lambda(key):
            print(key, end = " ")
    print()

    # Output first sets of all non-terminals
    print("\nFirst sets:")
    for key in grammar.cfg.keys():
        print(f"  {key} :", end = "\t")
        first_set = grammar.first_set(key)[0]
        if len(first_set) < 1:
            print("NONE - (This is probably an error)")
            continue

        print(first_set)

        # for terminal in first_set:
        #     print(terminal, end = " ")
        # print()

    # Output follow sets of all non-terminals
    print("\nFollow sets:")
    for key in grammar.cfg.keys():
        print(f"  {key} :", end = "\t")
        follow_set = grammar.follow_set(key)[0]
        if len(follow_set) < 1:
            print("NONE")
            continue

        print(follow_set)

    print("\nPredict sets (see GRAMMAR section for ruleno):")
    for x, predict_set in enumerate(grammar.predict_sets):
        print(f"  {x} :", end = "\t")

        if len(predict_set[1]) < 1:
            print("NONE")
            continue

        print(predict_set[1])

    ##########################################
    print("\n  -- PARSING --")
    grammar.build_parse_table()

    # DEBUG EXIT
    exit()

    LL1Table = LLTable(grammar)
    print(LL1Table.table)

    ts = open(token, 'rb')
    tree = grammar.build_parse_tree(grammar.rules,ts, LL1Table)
    print(tree)


if __name__ == '__main__':
    # if (len(sys.argv) != 3):
    #     print("please pass file")
    #     exit(1)
    # main(sys.argv[1], sys.argv[2])

    main(sys.argv[1])
