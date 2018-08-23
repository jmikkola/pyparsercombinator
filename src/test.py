from . import EndOfText, NoMatch, StringText, Char, parse

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


if __name__ == '__main__':
    unittest.main()
