
class ParseError(RuntimeError):
    pass


class EndOfText(ParseError):
    pass


class NoMatch(ParseError):
    pass


class AbstractText:
    ''' The base class of text inputs '''
    def get_start_cursor(self):
        ''' Returns a cursor that, when passed to read_at_cursor,
        will give the first character '''
        raise NotImplementedError()

    def read_at_cursor(self, cursor):
        '''
        Returns a tuple of a (character, cursor).
        The returned cursor will point to the next character.
        Raises EndOfText if the text stream is exhaused.
        '''
        raise NotImplementedError()


class StringText(AbstractText):
    def __init__(self, s):
        assert(isinstance(s, str))
        self._s = s

    def get_start_cursor(self):
        return IndexCursor(0)

    def read_at_cursor(self, cursor):
        assert(isinstance(cursor, IndexCursor))

        idx = cursor.get_index()
        if idx >= len(self._s):
            raise EndOfText()
        return (self._s[idx], IndexCursor(idx + 1))


class IndexCursor:
    def __init__(self, idx):
        self._idx = idx

    def get_index(self):
        return self._idx


class Parser:
    def recognize(self, text, cursor):
        '''
        Returns a (processed match result, cursor) if parsing succeeds.
        Raises either a NoMatch or an EndOfText if the parse fails.
        '''
        raise NotImplementedError()


'''
Fundamental parsers
'''


class Char(Parser):
    def __init__(self, ch):
        assert(isinstance(ch, str))
        assert(len(ch) == 1)
        self._ch = ch

    def recognize(self, text, cursor):
        ch, cursor = text.read_at_cursor(cursor)
        if ch != self._ch:
            raise NoMatch()
        return ch, cursor


class Predicate(Parser):
    def __init__(self, pred):
        self._pred = pred

    def recognize(self, text, cursor):
        ch, cursor = text.read_at_cursor(cursor)
        if not self._pred(ch):
            raise NoMatch()
        return ch, cursor


class EndParser(Parser):
    def recognize(self, text, cursor):
        try:
            text.read_at_cursor(cursor)
        except EndOfText:
            return ('', None)
        raise NoMatch


class LambdaParser(Parser):
    def recognize(self, text, cursor):
        return None, cursor


'''
Primitive combinators
'''


class Sequence(Parser):
    def __init__(self, parsers):
        assert(isinstance(parsers, list))
        for p in parsers:
            assert(isinstance(p, Parser))
        self._parsers = parsers

    def recognize(self, text, cursor):
        results = []
        cur = cursor
        for p in self._parsers:
            result, cur = p.recognize(text, cur)
            results.append(result)
        return results, cur


class Alternative(Parser):
    def __init__(self, parsers):
        assert(isinstance(parsers, list))
        for p in parsers:
            assert(isinstance(p, Parser))
        self._parsers = parsers

    def recognize(self, text, cursor):
        for p in self._parsers:
            try:
                return p.recognize(text, cursor)
            except NoMatch:
                pass
            except EndOfText:
                pass
        raise NoMatch()


class Apply(Parser):
    def __init__(self, parser, fn):
        assert(isinstance(parser, Parser))
        self._parser = parser
        self._fn = fn

    def recognize(self, text, cursor):
        result, cur = self._parser.recognize(text, cursor)
        return self._fn(result), cur


class Many(Parser):
    ''' zero or more copies '''
    def __init__(self, parser):
        assert(isinstance(parser, Parser))
        self._parser = parser

    def recognize(self, text, cursor):
        results = []
        cur = cursor
        while True:
            try:
                result, cur = self._parser.recognize(text, cur)
                results.append(result)
            except NoMatch:
                break
            except EndOfText:
                break
        return results, cur


'''
Useful constructions of combinators
'''


def String(s):
    ''' Parses the string s '''
    assert(isinstance(s, str))
    sParser = Sequence([Char(c) for c in s])
    return Apply(sParser, lambda lst: ''.join(lst))


def Optional(p):
    ''' Parses zero or one instance of p '''
    assert(isinstance(p, Parser))
    return Alternative([p, LambdaParser()])


def Many1(p):
    ''' Parses one or more instance of p '''
    assert(isinstance(p, Parser))
    seq = Sequence([p, Many(p)])
    return Apply(seq, lambda lst: [lst[0]] + lst[1])


def parse(text, parser):
    assert(isinstance(text, AbstractText))
    assert(isinstance(parser, Parser))

    cursor = text.get_start_cursor()
    (result, _) = parser.recognize(text, cursor)
    return result


def parse_string(s, parser):
    assert(isinstance(s, str))
    return parse(StringText(s), parser)
