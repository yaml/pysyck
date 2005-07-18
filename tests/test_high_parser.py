
import unittest
import syck
import test_low_parser
import os, mx.DateTime, datetime

INF = 1e300000
NAN = INF/INF

ARROW = "GIF89a\x0c\x00\x0c\x00\x84\x00\x00\xff\xff\xf7\xf5\xf5\xee\xe9\xe9\xe5fff\x00\x00\x00\xe7\xe7\xe7^^^\xf3\xf3\xed\x8e\x8e\x8e\xe0\xe0\xe0\x9f\x9f\x9f\x93\x93\x93\xa7\xa7\xa7\x9e\x9e\x9eiiiccc\xa3\xa3\xa3\x84\x84\x84\xff\xfe\xf9\xff\xfe\xf9\xff\xfe\xf9\xff\xfe\xf9\xff\xfe\xf9\xff\xfe\xf9\xff\xfe\xf9\xff\xfe\xf9\xff\xfe\xf9\xff\xfe\xf9\xff\xfe\xf9\xff\xfe\xf9\xff\xfe\xf9\xff\xfe\xf9!\xfe\x0eMade with GIMP\x00,\x00\x00\x00\x00\x0c\x00\x0c\x00\x00\x05,  \x8e\x810\x9e\xe3@\x14\xe8i\x10\xc4\xd1\x8a\x08\x1c\xcf\x80M$z\xef\xff0\x85p\xb8\xb01f\r\x1b\xce\x01\xc3\x01\x1e\x10' \x82\n\x01\x00;"
BINARY = r"""
- !binary "\
 R0lGODlhDAAMAIQAAP//9/X17unp5WZmZgAAAOfn515eXvPz7Y6OjuDg4J+fn5\
 OTk6enp56enmlpaWNjY6Ojo4SEhP/++f/++f/++f/++f/++f/++f/++f/++f/+\
 +f/++f/++f/++f/++f/++SH+Dk1hZGUgd2l0aCBHSU1QACwAAAAADAAMAAAFLC\
 AgjoEwnuNAFOhpEMTRiggcz4BNJHrv/zCFcLiwMWYNG84BwwEeECcgggoBADs="
-
 !binary |
  R0lGODlhDAAMAIQAAP//9/X17unp5WZmZgAAAOfn515eXvPz7Y6OjuDg4J+fn5
  OTk6enp56enmlpaWNjY6Ojo4SEhP/++f/++f/++f/++f/++f/++f/++f/++f/+
  +f/++f/++f/++f/++f/++SH+Dk1hZGUgd2l0aCBHSU1QACwAAAAADAAMAAAFLC
  AgjoEwnuNAFOhpEMTRiggcz4BNJHrv/zCFcLiwMWYNG84BwwEeECcgggoBADs=
"""

class TestDocuments(test_low_parser.TestDocuments):

    def _testDocuments(self, source, length):
        actual_length = 0
        for document in syck.load_documents(source):
            actual_length += 1
        self.assertEqual(actual_length, length)
        actual_length = 0
        for document in syck.parse_documents(source):
            actual_length += 1
        self.assertEqual(actual_length, length)

class TestValuesAndSources(test_low_parser.TestValuesAndSources):

    def testValues1(self):
        self._testValues(test_low_parser.COMPARE1)

    def testValues2(self):
        self._testValues(test_low_parser.COMPARE2)

    def testValues3(self):
        self._testValues(test_low_parser.COMPARE3)

    def testFileValues1(self):
        self._testFileValues(test_low_parser.COMPARE1)

    def testFileValues2(self):
        self._testFileValues(test_low_parser.COMPARE2)

    def testFileValues3(self):
        self._testFileValues(test_low_parser.COMPARE3)

    def testNonsense(self):
        class MyFile1:
            def read(self, max_length):
                return ' '*(max_length+1)
        class MyFile2:
            def read(self, max_length):
                return None
        self.assertRaises(ValueError, lambda: syck.parse(MyFile1()))
        self.assertRaises(ValueError, lambda: syck.load(MyFile1()))
        self.assertRaises(TypeError, lambda: syck.parse(MyFile2()))
        self.assertRaises(TypeError, lambda: syck.load(MyFile2()))

    def _testValues(self, (source, structure)):
        self.assertEqualStructure(syck.parse(source), structure)
        self.assertEqual(syck.load(source), structure)

    def _testFileValues(self, (source, structure)):
        filename = os.tempnam('/tmp', '_syck_test_')
        file(filename, 'wb').write(source)
        try:
            self.assertEqualStructure(syck.parse(file(filename)), structure)
            self.assertEqual(syck.load(file(filename)), structure)
        except:
            os.remove(filename)
            raise

class TestImplicitScalars(unittest.TestCase):


    def testBinary(self):
        self.assertEqual(syck.load(BINARY), [ARROW, ARROW])

    def testBoolean(self):
        # Syck does not recognize 'y'.
        #self.assertEqual(syck.load('- y\n- NO\n- True\n- on\n'), [True, False, True, True])
        self.assertEqual(syck.load('- yes\n- NO\n- True\n- on\n'), [True, False, True, True])

    def testFloat(self):
        self.assertAlmostEqual(syck.load('6.8523015e+5'), 685230.15)
        # Syck does not understand '_'.
        #self.assertAlmostEqual(syck.load('685.230_15e+03'), 685230.15)
        #self.assertAlmostEqual(syck.load('685_230.15'), 685230.15)
        self.assertAlmostEqual(syck.load('685.23015e+03'), 685230.15)
        self.assertAlmostEqual(syck.load('685230.15'), 685230.15)
        self.assertAlmostEqual(syck.load('190:20:30.15'), 685230.15)
        self.assertEqual(syck.load('-.inf'), -INF)
        self.assertEqual(syck.load('.nan'), NAN)

    def testInteger(self):
        # Syck does not understand '_' and binary integer.
        #self.assertEqual(syck.load(
        #    '- 685230\n- +685_230\n- 02472256\n- 0x_0A_74_AE\n'
        #    '- 0b1010_0111_0100_1010_1110\n- 190:20:30\n'), [685230]*6)
        self.assertEqual(syck.load(
            '- 685230\n- +685230\n- 02472256\n- 0x0A74AE\n'
            '- 190:20:30\n'), [685230]*5)

    def testNull(self):
        self.assertEqual(syck.load('-\n- NULL\n- ~\n'), [None]*3)

    def testTimestamp(self):
        # Again, Syck does not understand the latest two forms.
        #self.assertEqual(syck.load(
        #        '- 2001-12-15T02:59:43.1Z\n'
        #        '- 2001-12-14t21:59:43.10-05:00\n'
        #        '- 2001-12-14 21:59:43.10 -5\n'
        #        '- 2001-12-15 2:59:43.10\n'),
        #    [datetime.datetime(2001, 12, 15, 2, 59, 43, 100000)]*4)
        self.assertEqual(syck.load(
                '- 2001-12-15T02:59:43.1Z\n'
                '- 2001-12-14t21:59:43.10-05:00\n'
                '- 2001-12-14 21:59:43.10 -05\n'
                '- 2001-12-15 02:59:43.10 Z\n'),
            [datetime.datetime(2001, 12, 15, 2, 59, 43, 100000)]*4)
        self.assertEqual(syck.load('2002-12-14'), datetime.datetime(2002, 12, 14))

    def testString(self):
        self.assertEqual('abcd', 'abcd')

