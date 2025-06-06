"""
Taken and adapted from Sarna Tool
https://github.com/rsrdesarrollo/sarna
"""
import logging
import re

from docxtpl import DocxTemplate
from mistletoe.base_renderer import BaseRenderer

from docx_generator.adapters.docx.docx_adapter import make_run, escape_url, make_paragraph, list_level_style, \
    make_table, make_table_row, make_table_cell, make_hyperlink_run
from docx_generator.adapters.docx.style_adapter import DocxStyleAdapter
from docx_generator.adapters.logging_adapter import debug_token_rendering
from docx_generator.globals.picture_globals import PictureGlobals


class DocxRenderer(BaseRenderer):
    """
    Render used by Mistletoe
    See mistletoe.BaseRenderer for more information
    """

    def __call__(self, *args, **kwargs):
        self.warnings = set()
        return self

    def __init__(self, docx: DocxTemplate, image_handler: PictureGlobals = None):
        self.warnings = set()
        self.style = None
        self._template = docx
        self._image_handler = image_handler
        self._suppress_ptag_stack = [False]
        self._suppress_rtag_stack = [False]
        self._list_style_stack = []
        self._mod_pstyle_stack = []
        self._list_level = -1

        self._logger = logging.getLogger(__name__)

        super().__init__()

    def set_style(self, style: DocxStyleAdapter):
        self.style = style

    def _render_standard_run(self, token, style_name: str):
        self._suppress_rtag_stack.append(True)
        render = make_run(getattr(self.style, style_name), self.render_inner(token))
        self._suppress_rtag_stack.pop()
        return str(render)

    # TODO: Factorize code
    @debug_token_rendering('Rendering Strong.')
    def render_strong(self, token):
        return self._render_standard_run(token, 'strong')

    @debug_token_rendering('Rendering Emphasis.')
    def render_emphasis(self, token):
        return self._render_standard_run(token, 'italic')

    @debug_token_rendering('Rendering Inline Code.')
    def render_inline_code(self, token):
        return self._render_standard_run(token, 'inline_code')

    @debug_token_rendering('Rendering Strikethrough.')
    def render_strikethrough(self, token):
        return self._render_standard_run(token, 'strike')

    @debug_token_rendering('Rendering Image.')
    def render_image(self, token):
        if self._image_handler is not None:
            self._image_handler.set_template(self._template)
            image = self._image_handler.add_picture(token.src)
            return str(image)
        return ''

    @debug_token_rendering('Rendering Link.')
    def render_link(self, token):
        target = escape_url(token.target)

        for child in token.children:
            child.content = re.sub(r'<.*?>', '', child.content).strip()

        self._suppress_rtag_stack.append(True)
        inner = self.render_inner(token)
        xml = make_hyperlink_run(self.style.hyperlink, inner, self._template.build_url_id(target))
        self._suppress_rtag_stack.pop()

        return str(xml)

    @debug_token_rendering('Rendering Raw Text.')
    def render_raw_text(self, token):
        text = token.content.rstrip('\n').rstrip('\a')
        if self._suppress_rtag_stack[-1]:
            return text
        else:
            return make_run('', text)

    @debug_token_rendering('Rendering Heading.')
    def render_heading(self, token):
        style = getattr(self.style, 'header' + str(token.level))
        return make_paragraph(style, self.render_inner(token))

    @debug_token_rendering('Rendering Paragraph.')
    def render_paragraph(self, token):
        inner = self.render_inner(token)

        try:
            style = self._mod_pstyle_stack.pop()
        except IndexError:
            style = self.style.paragraph

        if self._suppress_ptag_stack[-1]:
            return inner

        return make_paragraph(style, inner)

    @debug_token_rendering('Rendering Block Code.')
    def render_block_code(self, token):
        style = self.style.code
        return make_paragraph(style, self.render_inner(token))

    @debug_token_rendering('Rendering List.')
    def render_list(self, token):
        if token.start:
            self._list_style_stack.append(self.style.ol)
        else:
            self._list_style_stack.append(self.style.ul)
        self._list_level += 1

        inner = self.render_inner(token)

        self._list_level -= 1
        self._list_style_stack.pop()
        return inner

    @debug_token_rendering('Rendering List Item.')
    def render_list_item(self, token):
        style = self._list_style_stack[-1]
        self._suppress_ptag_stack.append(True)
        inner = self.render_inner(token)
        self._suppress_ptag_stack.pop()
        return make_paragraph(list_level_style(style, self._list_level), inner, self._list_level > 0)

    @debug_token_rendering('Rendering Escape Sequence.')
    def render_escape_sequence(self, token):
        return self.render_inner(token)

    @debug_token_rendering('Rendering Line Break.')
    def render_line_break(self, token):
        return '<w:br/>'

    @debug_token_rendering('Rendering Thematic Break. NOT IMPLEMENTED.')
    def render_thematic_break(self, token):
        self.warnings.add('Markdown ThematicBreak is not implemented. It will be ignored')
        return ''

    @debug_token_rendering('Rendering Quote.')
    def render_quote(self, token):
        style = self.style.quote
        return make_paragraph(style, self.render_inner(token.children[0]))

    @debug_token_rendering('Rendering Auto Link. NOT IMPLEMENTED.')
    def render_auto_link(self, token):
        self.warnings.add('Markdown AutoLink is not implemented. It will be ignored')
        return ''

    @debug_token_rendering('Rendering Table.')
    def render_table(self, token):
        header = self.render(token.header)
        content = self.render_inner(token)
        return make_table(self.style.table, header, content)

    @debug_token_rendering('Rendering Table Row.')
    def render_table_row(self, token, is_header=False):
        content = self.render_inner(token)
        return make_table_row(content)

    @debug_token_rendering('Rendering Table Cell.')
    def render_table_cell(self, token, in_header=False):
        content = self.render_inner(token)
        return make_table_cell(self.style.paragraph, content)

    @debug_token_rendering('Rendering Separator.')
    def render_separator(self, token):
        return '<w:p></w:p>'

    @debug_token_rendering('Rendering Document.')
    def render_document(self, token):
        self.footnotes.update(token.footnotes)
        return_value = self.render_inner(token)
        self.warnings = self.warnings | self.style._warnings

        return return_value
