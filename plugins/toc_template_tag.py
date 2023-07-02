from bs4 import BeautifulSoup as Soup
from datasette import hookimpl
from jinja2 import nodes
from jinja2.exceptions import TemplateSyntaxError
from jinja2.ext import Extension


@hookimpl
def prepare_jinja2_environment(env):
    env.add_extension(TableOfContentsExtension)


class TableOfContentsExtension(Extension):
    tags = set(["toc"])

    def __init__(self, environment):
        super(TableOfContentsExtension, self).__init__(environment)

    def parse(self, parser):
        # We need this for reporting errors
        lineno = next(parser.stream).lineno
        body = parser.parse_statements(["name:endtoc"], drop_needle=True)
        return nodes.CallBlock(
            self.call_method("_render_toc"),
            [],
            [],
            body,
        ).set_lineno(lineno)

    async def _render_toc(self, caller):
        inner_html = await caller()
        soup = Soup(inner_html, "html5lib")
        # Find all the headings, add IDs to them
        headings = soup.select("h1,h2,h3,h4,h5,h6")
        issued_ids = set()
        menu_links = []
        for heading in headings:
            text = "-".join(strip_special_chars(heading.text.lower()).split())
            suffix = 0
            while True:
                if suffix:
                    id = "{}-{}".format(text, suffix)
                else:
                    id = text
                if id not in issued_ids:
                    break
                suffix += 1
            heading["id"] = id
            issued_ids.add(id)
            menu_links.append((int(heading.name[1:]), heading.text, id))

        tree = build_tree(menu_links)
        return tree_to_html(tree) + "\n\n" + str(soup)


def strip_special_chars(text):
    return "".join(c for c in text if c.isalnum() or c in " -")


def build_tree(links):
    nodes = {1: []}
    for depth, name, link in links:
        node = (depth, name, link, [])
        nodes[depth - 1].append(node)
        nodes[depth] = node[3]
    return nodes[1]


def tree_to_html(tree):
    html = "<ul>\n"
    for depth, name, link, children in tree:
        html += f'    <li><a href="#{link}">{name}</a>'
        if children:
            html += "\n" + tree_to_html(children) + "    "
        html += "</li>\n"
    html += "</ul>"
    return html
