"""
Taken from Sarna Tool
https://github.com/rsrdesarrollo/sarna
"""
import re


def docx_escape(s, quote=False):
    """
    Replace special characters "&", "<" and ">" to HTML-safe sequences.
    If the optional flag quote is true (the default), the quotation mark
    characters, both double quote (") and single quote (') characters are also
    translated.
    """
    s = s.replace("&", "&amp;")  # Must be done first!
    s = s.replace("<", "&lt;")
    s = s.replace(">", "&gt;")
    if quote:
        s = s.replace('"', "&quot;")
        s = s.replace('\'', "’")
    return s


def escape_url(raw):
    """
    Escape urls to prevent code injection craziness. (Hopefully.)
    """
    from urllib.parse import quote
    return quote(raw, safe='/#:;?=@&+$,')


def make_run(rPr, text):
    return '<w:r>{}{}</w:r>'.format(rPr, "<w:br/>".join(
        ('<w:t xml:space="preserve">{}</w:t>'.format(text) for text in docx_escape(text).split('\n'))
    ))


def make_hyperlink_run(rPr, link_text, url_id):
    link_text_xml = '<w:t xml:space="preserve">{}</w:t>'.format(link_text)
    xml = '<w:hyperlink r:id="{}" w:tgtFrame="_blank"><w:r>{}{}</w:r></w:hyperlink>'.format(url_id, rPr, link_text_xml)

    return xml


_sequence_format = """
<w:r>
    <w:t xml:space="preserve">{seq_name} </w:t> 
</w:r>
<w:fldSimple w:instr=" SEQ {seq_name} \* ARABIC ">
    <w:r>
        <w:rPr><w:noProof/></w:rPr> 
        <w:t>1</w:t>
    </w:r>
</w:fldSimple>
<w:r>
    <w:t xml:space="preserve">{separator}</w:t>
</w:r>"""


def make_sequence(seq_name: str, separator: str = ": "):
    return _sequence_format.format(seq_name=seq_name, separator=separator)


def list_level_style(pPr, level):
    return re.sub(
        r'<\s*w:ilvl\s+w:val\s*=\s*"\d+"\s*/>',
        '<w:ilvl w:val="{}"/>'.format(level),
        pPr
    )


def make_paragraph(pPr, content, close_prev=False):
    if close_prev:
        return "</w:p><w:p>{}{}".format(pPr, content)
    else:
        return "<w:p>{}{}</w:p>".format(pPr, content)


def make_table(tblpr, header, content):
    return "<w:tbl><w:tblGrid><w:gridCol w:w=\"9016\"/></w:tblGrid>{}{}{}</w:tbl>".format(tblpr, header, content)


def make_table_row(content):
    return "<w:tr>{}</w:tr>".format(content)


def make_table_cell(pPr, content):
    return "<w:tc>{}</w:tc>".format(make_paragraph(pPr, content))