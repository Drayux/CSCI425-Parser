

class ParseTable_LR:
    def __init__(self, grammar):
        self.data = None                # Renamed from table
        self.row_labels = []            # This is the PARSING STATES
        self.col_labels = []            # This is the GRAMMAR SYMBOLS

        self.create_labels(grammar)     # Renamed from fill_indices
        self.populate(grammar)          # Renamed from fill_table
    # self.table = ([None] * len(self.T_indexes)) * len(self.N_indexes)

    def create_labels(self, grammar):
        for N in grammar.cfg.keys():
            self.row_labels.append(N)

        for T in grammar.terminals:
            self.col_labels.append(T)
        self.col_labels.sort()

    def populate(self, grammar):
        # N = G.cfg.keys()
        # for A in N:
        #    A_index = self.N_indexes.index(A)
        #    for p in G.cfg[A]:
        #        for a in G.predict_set(p):
        #            a_index = self.T_indexes.index(a)
        #            self.table[A_index][a_index] = p

        self.data = [[-1] * len(self.col_labels) for i in range(len(self.row_labels))]
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
