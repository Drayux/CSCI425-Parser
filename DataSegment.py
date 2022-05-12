class DataSegment():
    def __init__(self, symbol_table = None):
        self.map = {}
        self.size = 0
        if symbol_table:
            self.map_from_sym_table(symbol_table)

    def map_from_sym_table(self, symbol_table):
        if symbol_table.tableStack[0]: 
            global_scope = symbol_table.tableStack[0]
            for var in global_scope:
                (_, attr) = global_scope.table[var]
                # Calc size/pos
                var_size = 4
                var_pos = self.size
                # Grow Segment by size of var
                self.size += var_size
                # Add to map
                self.map[var] = (pos, size) 

    def print_seg(self):
        for var in self.map:
            (pos, size) = self.map[var]
            print(f"{var} -> @{pos}, {size} bytes")

