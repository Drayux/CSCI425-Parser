import sys

class ParseTable_LR:
    def __init__(self, file):
        """
        :param file: Can be the string to a file or a file object
        # Parse Table initialization
            The LR(0) parse table will take in a file of .lr type
            and create a LR table from it. It can take a file name
            as a string or as an actual file object.
        """
        self.data = None                # Renamed from table
        self.row = []                   # This is the PARSING STATES
        self.col_labels = []            # This is the GRAMMAR SYMBOLS
        self.grammarMap = dict()        # This will come in handy for the interface

        # Nifty little guy to read a string or a file object
        if(type(file) == str):
            file = open(file, "r")

        # Get all the things from the *.lr file
        self.parse_file(file)

    def parse_file(self, file):
        result_list = []
        # open file and put it in an array of lines
        with file as f:
            lines = f.readlines()

            # Read in the first line with all the grammar symbols
            line = lines[0]
            items = line.split(',')
            items[-1] = items[-1].replace("\n", "")  # remove newline if exists
            for i in range(len(items)):
                if items[i] == '.':
                    continue
                else:
                    self.col_labels.append(items[i])
                    self.grammarMap[items[i]] = i-1

            # Read in the following lines to get all the parsing states
            for i, line in enumerate(lines):
                if i == 0:
                    continue
                items = line.split(',')
                items[-1] = items[-1].replace("\n", "")  # remove newline if exists
                self.row.append(items[1:])

    def lookUp_parsingAction(self, state, grammar_symbol: str = "f"):
        """
        :param state: a tuple<int,str> or integer
        :param grammar_symbol: a string or empty if state is a tuple
        :return: a string representing parsing action in the LR table

        # Parse Table Lookup
            The lookUp_parsingAction function will return the
            appropriate action. The function will accept a tuple
            of type <int, str> or can accept two parameters of type
            int and of type str

            Example:
            tup = (0, "f")
            print(lrTable.lookUp_parsingAction(tup))
            print(lrTable.lookUp_parsingAction(0, "f")
        """
        row = state
        col = self.grammarMap[grammar_symbol]

        if type(state) is tuple:
            row = state[0]
            col = self.grammarMap[state[1]]
        ret = self.row[row][col]
        if ret == '':
            ret = "ERROR"
        return ret

    # Output the production table
    def __str__(self):
        """
        This does not print out the best,
        but its good enough for government work
        :return: a table of the LR table when asked to print
        """
        # Print column labels
        ret = "\t  ||\t"
        for label in self.col_labels:
            if label == 'lambda': continue
            ret += f"{label}\t"
        ret += "\n"

        # Seperator bar
        for x in range(len(self.col_labels) + 1):
            ret += "========"
        ret += "\n"

        # Print the rows
        for linenum, line in enumerate(self.row):
            ret += f"{linenum}\t   ||\t"
            for item in line:
                ret += f"{'-' if item == '' else item}\t"
            ret += "\n"

        return ret


if __name__ == '__main__':
    if len(sys.argv) < 2:
        input = "config/fisher-4-1/fischer-4-1.lr"
    else:
        input = sys.argv[1]

    lrTable = ParseTable_LR(input)

#    tup = (0, "f")
#    print(lrTable.lookUp_parsingAction(tup))
    print(lrTable)
    print(lrTable.lookUp_parsingAction.__doc__)


