#!/bin/python3
import sys

def consume(stream):
    c = stream.pop()
    match c:
        case '|':
            return ("pipe", '|')
        case '*':
            return ("kleene", '*')
        case '+':
            return ("plus", '+')
        case '(':
            return ("open", '(')
        case ')':
            return ("close", ')')
        case '.':
            return ("dot", '.')
        case '-':
            return ("dash", '-')
        case '\\':
            return ("char", stream.pop())
        case _:
            return ("char", c)

def scan(input): 
    stream = list(input)
    stream.reverse()
    output = []
    #loop
    while stream:
        token = consume(stream)
        output.append(token)
    return output

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Not Enought Arguments!")
    else: 
        input = sys.argv[1]
        token_stream = scan(input)
        for token in token_stream:
            print(token)
