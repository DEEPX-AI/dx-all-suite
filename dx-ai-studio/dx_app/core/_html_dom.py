"""Tiny stdlib-only HTML DOM (html.parser) with a minimal BeautifulSoup-compatible
surface, so the ModelZoo parser needs no third-party dependency.

Supports exactly what dx_app/core/modelzoo.py uses:
  node.name                      tag name (None for a text node)
  node["href"] / node.get(k, d)  attribute access
  node.children                  direct children (text nodes have name=None, .text)
  node.get_text(strip=False)     concatenated descendant text
  node.find_all(names)           descendants matching a tag name (or list of names)
  node.find(name, href=False)    first matching descendant (optionally requiring href)
"""
from html.parser import HTMLParser

# Elements that never have a closing tag / no children.
_VOID = {"br", "img", "input", "meta", "link", "hr", "source", "track",
         "area", "base", "col", "embed", "param", "wbr"}


class Node:
    __slots__ = ("name", "attrs", "children", "text")

    def __init__(self, name=None, attrs=None):
        self.name = name          # None => text node
        self.attrs = dict(attrs or [])
        self.children = []
        self.text = ""            # only for text nodes

    def __getitem__(self, key):
        return self.attrs.get(key)

    def get(self, key, default=None):
        return self.attrs.get(key, default)

    def get_text(self, strip=False):
        parts = []

        def walk(n):
            if n.name is None:
                parts.append(n.text)
            else:
                for c in n.children:
                    walk(c)

        for c in self.children:
            walk(c)
        s = "".join(parts)
        return s.strip() if strip else s

    def find_all(self, names):
        if isinstance(names, str):
            names = [names]
        out = []

        def walk(n):
            for c in n.children:
                if c.name in names:
                    out.append(c)
                walk(c)

        walk(self)
        return out

    def find(self, name, href=False):
        for c in self.find_all(name):
            if not href or c.get("href"):
                return c
        return None


class _DOMBuilder(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node("[document]")
        self.stack = [self.root]

    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs)
        self.stack[-1].children.append(node)
        if tag not in _VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.stack[-1].children.append(Node(tag, attrs))

    def handle_endtag(self, tag):
        # Close up to the nearest matching open tag (tolerant of unclosed tags).
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].name == tag:
                del self.stack[i:]
                return

    def handle_data(self, data):
        tn = Node()
        tn.text = data
        self.stack[-1].children.append(tn)


def parse_html(html):
    """Parse an HTML string into a Node tree; return the document root."""
    b = _DOMBuilder()
    b.feed(html or "")
    b.close()
    return b.root
