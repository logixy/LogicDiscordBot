'''
 Source:
 https://pythonworld.ru/primery-programm/interpretator-brainfuck.html
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
        if iter_count > 1000000:
            result_string += "\n**Iteration overflow! at :** " + str(i) + " \"" + code[i] + "\"\n```" + code[0:i] + "```"
            break

    return result_string

#code = input()
#print(run(code))
