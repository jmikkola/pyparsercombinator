from . import (
    Alternative,
    Char,
    EndOfText,
    EndParser,
    LambdaParser,
    Many,
    Many1,
    NoMatch,
    Optional,
    Predicate,
    Sequence,
    String,
    StringText,
    parse,
    parse_string,
)


import unittest


class TextTest(unittest.TestCase):
    def test_text_stream(self):
        st = StringText('abc')
        cursor0 = st.get_start_cursor()
        (c1, cursor1) = st.read_at_cursor(cursor0)
        self.assertEqual(c1, 'a')
        (c2, cursor2) = st.read_at_cursor(cursor1)
        self.assertEqual(c2, 'b')
        (c3, cursor3) = st.read_at_cursor(cursor2)
        self.assertEqual(c3, 'c')
        with self.assertRaises(EndOfText):
            st.read_at_cursor(cursor3)

        # rewinding should work
        (c2b, _) = st.read_at_cursor(cursor1)
        self.assertEqual(c2b, c2)

    def test_parse_char_match(self):
        st = StringText('abc')
        parser = Char('a')
        self.assertEqual('a', parse(st, parser))

    def test_parse_char_no_match(self):
        st = StringText('abc')
        parser = Char('z')
        with self.assertRaises(NoMatch):
            parse(st, parser)

    def test_parse_char_eot(self):
        st = StringText('')
        parser = Char('a')
        with self.assertRaises(EndOfText):
            parse(st, parser)

    def test_parse_lambda(self):
        self.assertEqual(None, parse(StringText('abc'), LambdaParser()))
        self.assertEqual(None, parse(StringText(''), LambdaParser()))

    def test_parse_eof(self):
        self.assertEqual('', parse(StringText(''), EndParser()))
        with self.assertRaises(NoMatch):
            parse(StringText('asdf'), EndParser())

    def test_parse_sequence(self):
        st = StringText('abc')
        parser = Sequence([Char('a'), Char('b'), Char('c')])
        result = parse(st, parser)
        self.assertEqual(['a', 'b', 'c'], result)

    def test_parse_alternative(self):
        st = StringText('abc')
        p = Alternative([Char('a'), Char('b'), Char('c')])
        parser = Sequence([p, p])
        result = parse(st, parser)
        self.assertEqual(['a', 'b'], result)

    def test_parse_predicate(self):
        st = StringText('abc')
        self.assertEqual('a', parse(st, Predicate(str.isalpha)))
        with self.assertRaises(NoMatch):
            parse(st, Predicate(str.isdigit))

    def test_parse_string(self):
        st = StringText('asdf123')
        p = String('asdf')
        self.assertEqual('asdf', parse(st, p))

    def test_optional(self):
        p = Optional(Predicate(str.isdigit))
        self.assertEqual('1', parse_string('123', p))
        self.assertEqual(None, parse_string('asdf', p))
        self.assertEqual(None, parse_string('', p))

    def test_many(self):
        p = Many(Predicate(str.isdigit))
        self.assertEqual(['1', '2', '3'], parse(StringText('123xyz'), p))
        self.assertEqual([], parse(StringText('asdf'), p))
        self.assertEqual([], parse(StringText(''), p))

    def test_many1(self):
        p = Many1(Predicate(str.isdigit))
        self.assertEqual(['1', '2', '3'], parse(StringText('123xyz'), p))
        self.assertEqual(['1'], parse(StringText('1asdf'), p))
        with self.assertRaises(NoMatch):
            parse(StringText('asdf'), p)


if __name__ == '__main__':
    unittest.main()
