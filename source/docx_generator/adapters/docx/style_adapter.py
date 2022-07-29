"""
Taken and adapted from Sarna Tool
https://github.com/rsrdesarrollo/sarna
"""

import re
from typing import AnyStr, Set, Dict

from docx import Document
from docx.document import Document as DocType
from docx.table import Table
from docx.text.paragraph import Paragraph
from jinja2.exceptions import TemplateSyntaxError

_BEGIN_STYLE = re.compile(r'##\s*begin\s*style\s*(\w+)\s*##', re.IGNORECASE)
_END_STYLE = re.compile(r'##\s*end\s*style\s*##', re.IGNORECASE)
_TAG_STYLE = re.compile(r'##\s*(\w+)\s*##', re.IGNORECASE)

PARAGRAPH_STYLE_TAGS = {'ul', 'ol', 'paragraph', 'code', 'quote', 'image_caption', 'header1', 'header2', 'header3', 'header4', 'header5'}
RAW_STYLE_TAGS = {'hyperlink', 'strong', 'italic', 'strike', 'inline_code'}
TABLE_STYLE_TAGS = {'table', }


class DocxStyleAdapter:
    name: AnyStr
    _warnings: Set

    header1: AnyStr
    header2: AnyStr
    header3: AnyStr
    header4: AnyStr
    header5: AnyStr

    ul: AnyStr
    ol: AnyStr
    paragraph: AnyStr
    inline_code: AnyStr
    code: AnyStr
    quote: AnyStr
    hyperlink: AnyStr
    image_caption: AnyStr

    strong: AnyStr
    italic: AnyStr
    strike: AnyStr

    table: AnyStr

    _data = dict(
        header1=None,
        header2=None,
        header3=None,
        header4=None,
        header5=None,
        ul=None,
        ol=None,
        paragraph=None,
        inline_code=None,
        code=None,
        quote=None,
        hyperlink=None,
        image_caption=None,
        strong=None,
        italic=None,
        strike=None,
        table=None
    )

    def __init__(self, **kwargs):
        if 'name' not in kwargs:
            raise ValueError('Attribute name is required for a RenderStyle')

        self.name = kwargs.pop('name')
        self._warnings = set()

        for k, v in kwargs.items():
            if k in self._data and not k.startswith('_'):
                self._data[k] = v
            else:
                self._warnings.add(
                    'Invalid style descriptor {} on style name {}'.format(k, self.name)
                )

    def __getattr__(self, item):
        attr = self._data.get(item, None)
        if attr is None:
            self._warnings.add(
                "Try to use {} on style {} but is not defined".format(item, self.name)
            )
        return attr


class RenderStylesCollection:
    _styles: Dict[AnyStr, DocxStyleAdapter]

    def __init__(self):
        self._styles = dict()

    def add_style(self, style: DocxStyleAdapter):
        if style.name in self._styles:
            raise ValueError('Style {} already defined'.format(style.name))
        self._styles[style.name] = style
        return self

    def get_style(self, name='default'):
        if name not in self._styles:
            raise ValueError('Style {} not defined'.format(name))
        return self._styles[name]


def _iter_block_items(parent):
    """
    Generate a reference to each paragraph and table child within *parent*,
    in document order. Each returned value is an instance of either Table or
    Paragraph. *parent* would most commonly be a reference to a main
    Document object, but also works for a _Cell object, which itself can
    contain paragraphs and tables.

    Author @scanny: https://github.com/python-openxml/python-docx/issues/276#issuecomment-199502885
    """
    from docx.table import _Cell
    from docx.oxml import CT_P
    from docx.oxml import CT_Tbl

    if isinstance(parent, DocType):
        parent_elm = parent.element.body
    elif isinstance(parent, _Cell):
        parent_elm = parent._tc
    else:
        raise ValueError("something's not right")

    for child in parent_elm.iterchildren():
        if isinstance(child, CT_P):
            yield Paragraph(child, parent)
        elif isinstance(child, CT_Tbl):
            yield Table(child, parent)


def get_document_render_styles(doc_path) -> RenderStylesCollection:
    styles = RenderStylesCollection()

    doc: DocType = Document(doc_path)

    style_name = None
    attrs = dict()

    for element in _iter_block_items(doc):
        if not style_name and not isinstance(element, Paragraph):
            continue

        if not style_name:
            match = _BEGIN_STYLE.match(element.text)
            if match:
                style_name = match.group(1)
        else:
            if isinstance(element, Table):
                attrs['table'] = element._tblPr.xml
            else:
                text = element.text
                if _END_STYLE.match(text):
                    styles.add_style(DocxStyleAdapter(name=style_name, **attrs))
                    style_name = None
                    attrs = dict()
                    continue

                match = _TAG_STYLE.match(text)
                if match:
                    tag_name = match.group(1).lower()
                    if tag_name in PARAGRAPH_STYLE_TAGS:
                        # Get style from paragraph
                        if element._element.pPr is not None:
                            attrs[tag_name] = element._element.pPr.xml
                        else:
                            attrs[tag_name] = '<w:pPr></w:pPr>'
                    elif tag_name in RAW_STYLE_TAGS:
                        # Get style from Run
                        if element.runs[0]._element.rPr is not None:
                            attrs[tag_name] = element.runs[0]._element.rPr.xml
                        else:
                            attrs[tag_name] = '<w:rPr></w:rPr>'

    if style_name is not None:
        raise TemplateSyntaxError(
            'Unexpected end of template style definition {}. Never closed'.format(style_name),
            None
        )

    return styles
