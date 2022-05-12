def remove_prefix(node, prefix):
    if node.data.startswith(prefix):
        if len(node.data) > len(prefix):
            return node.data[len(prefix):]
        print(f"Node: {node.data} has no data after prefix: {prefix}")
        return ""
    print(f"Unexpected Prefix on Node: {node.data}, expected prefix: {prefix}")
    return ""

def verify_node(node, expected_data):
    if node.data != expected_data:
        print(f"Expected node: {expected_data}, found node: {node.data}")
    return node


class Entry():
    def __init__(self, name, pos, value=None):
        self.name = name
        self.pos = pos
        self.value = value

class DataSegment():
    def __init__(self, symbol_table = None):
        self.map = {}
        self.size = 0
        self.counter = 0
        if symbol_table:
            self.map_from_sym_table(symbol_table)

    def find_value(self, value):
        for var in self.map:
            entry = self.map[var]
            if entry.value == value:
                return entry.pos
        return 0
 
    def visit_pass(self, node):
        IMM_MAX = 2047  # TODO: determine actual immediate bounds
        #########################
        # Declist Node
        #########################
        if node.data == "DECLLIST":
            d_typ = remove_prefix(node.children[0], "type:")
            for child in node.children[1:]:
                dec_node = verify_node(child, "DECLID")
                if dec_node.children[0].data == "=":
                    eq_node = verify_node(dec_node.children[0], "=")
                    d_id = remove_prefix(eq_node.children[0], "id:")
                    self.visit_pass(eq_node.children[1]) 
                else:
                    d_id = remove_prefix(dec_node.children[0], "id:")
                self.map[d_id] = Entry(d_id, self.size)
                self.size += 1  # All data is size 1w
            return
        ###########################
        # Int/Float Val
        ###########################
        if "val" in node.data:
            data = 0
            if node.data.startswith("intval:"):
                data = int(remove_prefix(node, "intval:"))
                if data > IMM_MAX:
                    self.map[f"!{self.counter}"] = Entry(f"!{self.counter}", self.size, data)
                    self.size += 1
                    self.counter += 1
            elif node.data.startswith("floatval:"):
                data = float(remove_prefix(node, "floatval:"))
                self.map[f"!{self.counter}"] = Entry(f"!{self.counter}", self.size, data)
                self.size += 1
                self.counter += 1

            
            return
        for child in node.children:
            self.visit_pass(child)

    def print_seg(self):
        for var in self.map:
            (pos, size) = self.map[var]
            print(f"{var} -> @{pos}, {size} bytes")

