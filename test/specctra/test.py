import unittest
import os, sys

# Add path to development version of upconvert
# so it can be tested without installing
path = os.path.abspath(__file__)
for i in xrange(3):
    path = os.path.dirname(path)
sys.path.insert(0, path)

from upconvert.parser.specctra import DsnParser

class DsnParserTests(unittest.TestCase):
    def testPlainParser(self):
        parser = DsnParser()
        got = parser.parse('''
(pcb test.dsn
  (parser
    (host_cad "Kicad's PCBNEW")
    (host_version "(2011-06-28)")
  )
)''')
        correct = ['pcb', 'test.dsn',
                    ['parser',
                        ['host_cad', "\"Kicad's", "PCBNEW\""],
                        ['host_version', '"', ['2011-06-28'], '"']
                    ]
                ]
 
        self.assertEqual(correct, got)

    def testQuoteParser(self):
        parser = DsnParser()
        got = parser.parse('''
(pcb test.dsn
  (parser
    (string_quote ")
    (host_cad "Kicad's PCBNEW)
    (host_version "(2011-06-28)")
  )
)''')
        correct = ['pcb', 'test.dsn',
                    ['parser',
                        ['string_quote', '"'],
                        ['host_cad', "Kicad's", "PCBNEW"],
                        ['host_version', '(2011-06-28)']
                    ]
                ]
 
        self.assertEqual(correct, got)

    def testQuoteSpaceParser(self):
        parser = DsnParser()
        got = parser.parse('''
(pcb test.dsn
  (parser
    (string_quote ")
    (space_in_quoted_tokens on)
    (host_cad "Kicad's PCBNEW")
    (host_version "(2011-06-28)")
  )
)''')
        correct = ['pcb', 'test.dsn',
                    ['parser',
                        ['string_quote', '"'],
                        ['space_in_quoted_tokens', 'on'],
                        ['host_cad', "Kicad's PCBNEW"],
                        ['host_version', '(2011-06-28)']
                    ]
                ]
 
        self.assertEqual(correct, got)

if __name__ == '__main__':
    unittest.main()
