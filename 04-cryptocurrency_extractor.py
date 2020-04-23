import re

finder = dict()
finder['btc'] = re.compile(('(?:[ ><=/\"])'
                            '([13][a-km-zA-HJ-NP-Z1-9]{25,34}|'
                            'bc1[ac-hj-np-zAC-HJ-NP-Z02-9]{11,71})'
                            '(?:[ ><=/\"])'))
finder['eth'] = re.compile(('(?:[ ><=/\"])'
                            '(0x[a-fA-F0-9]{40})'
                            '(?:[ ><=/\"])'))
finder['xmr'] = re.compile(('(?:[ ><=/\"])'
                            '(4[0-9AB][1-9A-HJ-NP-Za-km-z]{93})'
                            '(?:[ ><=/\"])'))
