class Tree(object):
    def __init__(
        self,
        symbol=None,
        children=[],
        sentence=[],
        leaf=None,
    ):
        self.symbol = symbol
        self.children = children
        self.sentence = sentence
        self.leaf = leaf
        self._str = None

    def __str__(self):
        if self._str is None:
            if len(self.children) != 0:
                childstr = ' '.join(str(c) for c in self.children)
                self._str = '({} {})'.format(self.symbol, childstr)
            else:
                self._str = '({} {})'.format(
                    self.sentence[self.leaf][1],
                    self.sentence[self.leaf][0],
                )
        return self._str

    def propagate_sentence(self, sentence):
        self.sentence = sentence
        for child in self.children:
            child.propagate_sentence(sentence)

    @staticmethod
    def parse(line):
        line += " "
        # sentence = []
        _, t, s = Tree._parse(line.lstrip(), 0)

        if t.symbol == 'TOP' and len(t.children) == 1:
            t = t.children[0]

        return t

    @staticmethod
    def _parse(line, index):
        index += 1
        symbol = None
        sentence = []
        children = []
        leaf = None
        while line[index] != ')':
            if line[index] == '(':
                index, child_t, child_sent = Tree._parse(line, index)
                if len(child_sent) > 0:
                    children.append(child_t)
                    for c in child_sent:
                        sentence.append(c)
            else:
                if symbol is None:
                    rpos = min(line.find(' ', index), line.find('(', index), line.find(')', index)) \
                        if line.find('(', index) != -1 else min(line.find(' ', index), line.find(')', index))
                    symbol = line[index:rpos]
                    symbol = symbol.split('-')[0]
                    symbol = symbol.split('=')[0]
                    if symbol == '' and index < 3:
                        symbol = 'S'
                    index = rpos
                else:
                    rpos = line.find(')', index)
                    word = line[index:rpos]
                    sentence.append([word, symbol])
                    leaf = len(sentence) - 1
                    index = rpos

            while line[index] == " ":
                index += 1

        t = Tree(
            symbol=symbol,
            children=children,
            sentence=sentence,
            leaf=leaf,
        )
        return (index + 1), t, sentence

    def left_span(self):
        """
        return:
            left bound of the span
        """
        try:
            return self._left_span
        except AttributeError:
            if self.leaf is not None:
                self._left_span = self.leaf
            else:
                self._left_span = self.children[0].left_span()
            return self._left_span

    def right_span(self):
        """
        return:
            right bound of the span
        """
        try:
            return self._right_span
        except AttributeError:
            if self.leaf is not None:
                self._right_span = self.leaf
            else:
                self._right_span = self.children[-1].right_span()
            return self._right_span

    @staticmethod
    def load_treefile(fname):
        trees = []
        for line in open(fname):
            t = Tree.parse(line)
            trees.append(t)
        return trees

    def enclosing(self, left, right, equal=True):
        """
        return:
            the smallest span that >= span(left, right) if equal=True,
            else the smallest span that > span(left, right).
        """
        for child in self.children:
            l = child.left_span()
            r = child.right_span()
            if (l <= left) and (right <= r):
                if not equal and (l == left) and (r == right):
                    break
                return child.enclosing(left, right, equal)

        return self

    def span_labels(self, left, right):
        """
        return:
            list of symbols of span(left, right) in top-down order if span(left, right) exists,
            else empty list.
        """
        if self.leaf is not None:
            return []

        if (self.left_span() == left) and (self.right_span() == right):
            result = [self.symbol]
        else:
            result = []

        for child in self.children:
            l = child.left_span()
            r = child.right_span()
            if (l <= left) and (right <= r):
                result.extend(child.span_labels(left, right))
                break

        return result

    def span_splits(self, left, right):
        """
        return:
            list of splits of the smallest span >= span(left, right) between left and right.
        """
        subtree = self.enclosing(left, right, equal=True)
        return [
            child.left_span()
            for child in subtree.children
            if left < child.left_span() <= right
        ]
