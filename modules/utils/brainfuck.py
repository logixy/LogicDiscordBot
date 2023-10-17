'''
 Source:
 https://pythonworld.ru/primery-programm/interpretator-brainfuck.html
 https://github.com/sstelian/Text-to-Brainfuck/blob/master/brainfuck_generator.py
'''

def block(code):
    opened = []
    blocks = {}
    for i in range(len(code)):
        if code[i] == '[':
            opened.append(i)
        elif code[i] == ']':
            blocks[i] = opened[-1]
            blocks[opened.pop()] = i
    return blocks

def parse(code):
    return ''.join(c for c in code if c in '><+-.,[]')

def run(code):
    code = parse(code)
    x = i = 0
    bf = {0: 0}
    blocks = block(code)
    l = len(code)
    iter_count = 0
    result_string = ''
    while i < l:
        sym = code[i]
        if sym == '>':
            x += 1
            bf.setdefault(x, 0)
        elif sym == '<':
            x -= 1
        elif sym == '+':
            bf[x] += 1
        elif sym == '-':
            bf[x] -= 1
        elif sym == '.':
            result_string += chr(bf[x])
        elif sym == ',':
            bf[x] = int(input('Input: '))
        elif sym == '[':
            if not bf[x]: i = blocks[i]
        elif sym == ']':
            if bf[x]: i = blocks[i]
        i += 1
        iter_count += 1
        if iter_count > 1000000: # limit long iterations
            result_string += "\n**Iteration overflow! at :** " + str(i) + " \"" + code[i] + "\"\n```" + code[0:i] + "```"
            break

    return result_string

# BF Translator functions

def char_to_bf(char):
    buffer = "[-]>[-]<"
    for i in range(ord(char)//10):
        buffer = buffer + "+"
    buffer = buffer + "[>++++++++++<-]>"
    for i in range(ord(char) % 10):
        buffer = buffer + "+"
    buffer = buffer + ".<"
    return buffer


# Uses a similar algorithm to char_to_bf(), but can also decrement, based on the sign of the given argument.
# Optimizes the final Brainfuck source code by altering the current value in the cell, instead of clearing and
# starting from 0.


def delta_to_bf(delta):
    buffer = ""
    for i in range(abs(delta) // 10):
        buffer = buffer + "+"

    if delta > 0:
        buffer = buffer + "[>++++++++++<-]>"
    else:
        buffer = buffer + "[>----------<-]>"

    for i in range(abs(delta) % 10):
        if delta > 0:
            buffer = buffer + "+"
        else:
            buffer = buffer + "-"
    buffer = buffer + ".<"
    return buffer


# Uses the previous helper functions to generate Brainfuck source that prints the string argument of this function.
# The commented argument puts code that generates one character on a new line and appends the printed character, which
# is considered a comment in Brainfuck. Valid Brainfuck source characters are stripped.


def string_to_bf(string, commented):
    buffer = ""
    if string is None:
        return buffer
    for i, char in enumerate(string):
        if i == 0:
            buffer = buffer + char_to_bf(char)
        else:
            delta = ord(string[i]) - ord(string[i - 1])
            buffer = buffer + delta_to_bf(delta)
        if commented:
            buffer = buffer + ' ' + string[i].strip('+-<>[],.') + '\n'
    return buffer
#code = input()
#print(run(code))
