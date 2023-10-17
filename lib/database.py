import sqlite3
import math
import random
#import asciichartpy

class Database():
    def __init__(self):
        self.db = sqlite3.connect("ldb.db")
        self.cursor = self.db.cursor()
    
    def status() -> str:
        return "TODO: Create database status"
    
    def get_reqs(self):
        return random.randint(0, 25)
    
    def get_sin(self, x, max):
        return 18 * math.sin(x * (math.pi * 4) / max)

    
    def requests_table(self):
        s2 = []
        for i in range(20):
            s2.append(self.get_reqs())
        
        # TODO: make this chart = asciichartpy.plot(s2, {'height': 10, 'offset': 3})
        chart = """
   25.00  ┼              ╭╮
   22.50  ┤         ╭─╮  ││
   20.00  ┤ ╭╮      │ │  ││  ╭
   17.50  ┤ ││╭╮    │ │  ││  │
   15.00  ┤╭╯│││  ╭╮│ │  ││  │
   12.50  ┤│ │││  │││ │  ││  │
   10.00  ┤│ │││╭╮│││ ╰╮ ││ ╭╯
    7.50  ┼╯ ││╰╯││││  │ │╰╮│
    5.00  ┤  ││  ╰╯╰╯  │╭╯ ╰╯
    2.50  ┤  ╰╯        ││
    0.00  ┤            ╰╯
"""
        return chart
    
