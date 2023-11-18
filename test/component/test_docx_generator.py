#!/usr/bin/env python3
#
#  docx-generator Source Code
#  Copyright (C) 2021 - Airbus CyberSecurity (SAS)
#  ir@cyberactionlab.net
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 3 of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
import json
import os
import re
import shutil
from unittest import TestCase

from docx import Document
from docx.drawing import Drawing
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT, WD_COLOR_INDEX
from docx.opc.constants import RELATIONSHIP_TYPE
from docx.text.paragraph import Paragraph
from docx.text.run import Run

from docx_generator.docx_generator import DocxGenerator
from docx_generator.exceptions.rendering_error import RenderingError


class TestDocxGenerator(TestCase):
    def setUp(self) -> None:
        self._base_path = os.getcwd()
        self._template_path = 'templates'
        self._results_path = 'results'

        self._output_filenames = {
            'basic_template_result': 'basic_template_result.docx',
            'date_filter_template_result': 'date_filter_template_result.docx',
            'image_filter_template_result': 'image_filter_template_result.docx',
            'image_from_uuid_filter_template_result': 'image_from_uuid_filter_template_result.docx',
            'markdown_filter_template_result': 'markdown_filter_template_result.docx',
            'specific_markdown_filter_template_result': 'specific_markdown_filter_template_result.docx',
            'subdoc_filter_template_result': 'subdoc_filter_template_result.docx',
            'recursive_render_result': 'recursive_render_result.docx',
            'recursive_max_depth_render_result': 'recursive_max_depth_render_result.docx',
            'hyperlink_global_result': 'hyperlink_global_result.docx',
            'non_existent_global_result': 'non_existent_global_result.docx',
            'non_existent_filter_result': 'non_existent_filter_result.docx',
            'unclosed_jinja_control_tag_result': 'unclosed_jinja_control_tag_result.docx',
            'richtext_result': 'richtext_result.docx'
        }

        self._subject = DocxGenerator(logger_mode='DEBUG', allow_external_download=True)

    def tearDown(self) -> None:
        shutil.rmtree(os.path.join(self._base_path, 'tmp', 'images'))
        return None
        for filename in self._output_filenames.values():
            try:
                os.remove(os.path.join(self._results_path, filename))
            except FileNotFoundError:
                pass

    def test_should_generate_docx_from_basic_template(self):
        text_to_add = 'Report Name'
        data = {
            'name': text_to_add
        }

        self._subject.generate_docx(
            self._base_path,
            os.path.join(self._template_path, 'basic_template.docx'),
            data,
            os.path.join(self._results_path, self._output_filenames['basic_template_result'])
        )

        has_been_found = False
        document = Document(os.path.join(self._results_path, self._output_filenames['basic_template_result']))
        for paragraph in document.paragraphs:
            if re.search(text_to_add, paragraph.text) is not None:
                has_been_found = True
                break

        self.assertTrue(has_been_found, 'Text passed as data is not found in the generated document.')

    def test_should_generate_docx_from_template_with_timestamp_to_date_filter(self):
        data = {
            'date': '1589480671562'
        }

        converted_date = '14/05/2020'

        self._subject.generate_docx(
            self._base_path,
            os.path.join(self._template_path, 'date_filter_template.docx'),
            data,
            os.path.join(self._results_path, self._output_filenames['date_filter_template_result'])
        )

        has_been_found = False
        document = Document(os.path.join(self._results_path, self._output_filenames['date_filter_template_result']))
        for paragraph in document.paragraphs:
            if re.search(converted_date, paragraph.text) is not None:
                has_been_found = True
                break

        self.assertTrue(has_been_found, 'Converted date is not found in the generated document.')

    def test_should_generate_docx_from_template_with_hyperlink_global(self):
        data = {
            'hyperlink_caption': 'google',
            'hyperlink_url': 'https://www.google.fr',

            'mail_caption': 'alain.dupont@orange.fr',
            'mail_url': 'mailto:alain.dupont@orange.fr'
        }

        self._subject.generate_docx(
            self._base_path,
            os.path.join(self._template_path, 'hyperlink_global_template.docx'),
            data,
            os.path.join(self._results_path, self._output_filenames['hyperlink_global_result'])
        )

        # TESTS
        generated_document = Document(os.path.join(self._results_path, self._output_filenames['hyperlink_global_result']))

        found_hyperlinks = []

        relationships = generated_document.part.rels
        for rel in relationships:
            if relationships[rel].reltype == RELATIONSHIP_TYPE.HYPERLINK:
                found_hyperlinks.append(relationships[rel]._target)

        self.assertEqual(2, len(found_hyperlinks))
        self.assertTrue(data['hyperlink_url'] in found_hyperlinks)
        self.assertTrue(data['mail_url'] in found_hyperlinks)

    def test_should_generate_docx_from_template_with_image_global(self):
        data = {
            'image1': os.path.abspath('./images/test_image.jpg'),
            'image2': os.path.abspath('./images/test_image_small.jpg')
        }

        self._subject.generate_docx(
            self._base_path,
            os.path.join(self._template_path, 'image_filter_template.docx'),
            data,
            os.path.join(self._results_path, self._output_filenames['image_filter_template_result'])
        )

    def test_should_generate_docx_from_template_with_image_from_uuid_global(self):
        data = {
            'uuid': '5bacc2bc-5b90-4c47-93d7-d9291911c4b3',
        }

        self._subject.generate_docx(
            self._base_path,
            os.path.join(self._template_path, 'image_from_uuid_filter_template.docx'),
            data,
            os.path.join(self._results_path, self._output_filenames['image_from_uuid_filter_template_result'])
        )

    def test_should_raise_error_if_uuid_folder_contains_multiple_files(self):
        data = {
            'uuid': '2b910dac-6e10-45ae-89cd-b9c304809eb9',
        }

        with self.assertRaises(RenderingError):
            self._subject.generate_docx(
                self._base_path,
                os.path.join(self._template_path, 'image_from_uuid_filter_template.docx'),
                data,
                os.path.join(self._results_path, self._output_filenames['image_from_uuid_filter_template_result'])
            )

    def test_should_generate_docx_from_template_with_markdown_filter(self):
        markdown_text = 'First Paragraph:\n\n**Strong text**\n*New line with italic text* and `code`\n\nNew paragraph\n\n' \
                        '[link to Google!](http://google.com )\n\nUnordered List:\n\n* Item 1\n* Item 2\n\nOrdered List\n\n' \
                        '1. Item A\n2. Item B\n\nA block of code:\n\n```\ntest with some code\nAnother line of code\n__should not be bold__\n' \
                        '```\n\nTable:\n\n**Markdown** | *Less* | Pretty\n--- | --- | ---\n1 | 2 | 3\n\n \n\n' \
                        'Quote:\n\n> Is a quote !\n> Is still a quote !!\n> **Strong quote**\n' \
                        '```\nPOST /aaa/bbb/ccc\nHTTP / 1.1\nHost: toto.toto.toto\nUser - Agent: curl / 7.58.0 \n' \
                        'Accept: * / *\nContent - Type: application / json\nAuthorization: Bearer c66330ee-cd76-4ab--d37d44bef\n' \
                        'Id_token: __token__\nContent - Length: 305\nConnection: close\n\n{"key1": "value1",\n"key2": "value2\n}\n```'

        markdown_text2 = 'toto'

        data = {
            'text_for_paragraph': markdown_text,
            'text_for_code_block': markdown_text2
        }

        self._subject.generate_docx(
            self._base_path,
            os.path.join(self._template_path, 'markdown_filter_template.docx'),
            data,
            os.path.join(self._results_path, self._output_filenames['markdown_filter_template_result'])
        )

    def test_should_not_fail_with_specific_markdown(self):
        markdown_text = '***possibly an error***'

        markdown_text2 = 'toto'

        data = {
            'text_for_paragraph': markdown_text,
            'text_for_code_block': markdown_text2
        }

        self._subject.generate_docx(
            self._base_path,
            os.path.join(self._template_path, 'markdown_filter_template.docx'),
            data,
            os.path.join(self._results_path, self._output_filenames['specific_markdown_filter_template_result'])
        )

    def test_should_generate_docx_from_template_with_subdocument_global(self):
        subdoc_path = os.path.join(self._template_path, 'sub_document_filter_template_part.docx')

        data = {
            'sub_document_path': subdoc_path
        }

        self._subject.generate_docx(
            self._base_path,
            os.path.join(self._template_path, 'sub_document_filter_template.docx'),
            data,
            os.path.join(self._results_path, self._output_filenames['subdoc_filter_template_result'])
        )

    def test_should_generate_docx_with_nested_variables(self):
        subdoc_path = os.path.join(self._template_path, 'sub_document_filter_template_part_with_nested_variable.docx')

        data = {
            'sub_document_path': subdoc_path,
            'nested_variable': 'A nested value included {{nested_variable_level_2}}',
            'nested_variable_level_2': 'with some more one level under.'
        }

        self._subject.generate_docx(
            self._base_path,
            os.path.join(self._template_path, 'sub_document_filter_template.docx'),
            data,
            os.path.join(self._results_path, self._output_filenames['recursive_render_result'])
        )

    def test_should_generate_docx_with_nested_variables_up_to_5_render(self):
        subdoc_path = os.path.join(self._template_path, 'sub_document_filter_template_part_with_nested_variable.docx')

        data = {
            'sub_document_path': subdoc_path,
            'nested_variable': 'A nested value included {{nested_variable_level_2}}',
            'nested_variable_level_2': 'with some more from level 2 {{nested_variable_level_3}}',
            'nested_variable_level_3': 'with some more from level 3 {{nested_variable_level_4}}',
            'nested_variable_level_4': 'with some more from level 4 {{nested_variable_level_5}}',
            'nested_variable_level_5': 'with some more from level 5 {{nested_variable_level_6}}',
            'nested_variable_level_6': 'with some more from level 6',
        }

        self._subject.generate_docx(
            self._base_path,
            os.path.join(self._template_path, 'sub_document_filter_template.docx'),
            data,
            os.path.join(self._results_path, self._output_filenames['recursive_max_depth_render_result'])
        )

    def test_should_raise_rendering_error_if_global_does_not_exist(self):
        data = {'value': 'test values'}

        with self.assertRaises(RenderingError):
            self._subject.generate_docx(
                self._base_path,
                os.path.join(self._template_path, 'non_existent_global_template.docx'),
                data,
                os.path.join(self._results_path, self._output_filenames['non_existent_global_result'])
            )

    def test_should_raise_rendering_error_if_filter_does_not_exist(self):
        data = {'value': 'test values'}

        with self.assertRaises(RenderingError):
            self._subject.generate_docx(
                self._base_path,
                os.path.join(self._template_path, 'non_existent_filter_template.docx'),
                data,
                os.path.join(self._results_path, self._output_filenames['non_existent_filter_result'])
            )

    def test_should_raise_rendering_error_if_there_is_an_error_with_jinja_control_tags(self):
        data = {'value': 'test values'}

        with self.assertRaises(RenderingError):
            self._subject.generate_docx(
                self._base_path,
                os.path.join(self._template_path, 'unclosed_jinja_control_tag_template.docx'),
                data,
                os.path.join(self._results_path, self._output_filenames['unclosed_jinja_control_tag_result'])
            )

    def test_should_generate_docx_with_richtext(self):
        richtext_content = [
            # 0
            # HEADING 1
            {
                "type": "heading-1",
                "children": [
                    {"text": "This is a test for Richtext"}
                ]
            },
            # 1
            # PARAGRAPH 1
            {
                "type": "paragraph",
                "children": [
                    {"text": "Test "},
                    {"text": "with bold, ", "bold": True},
                    {"text": "with italic and underline", "italic": True, "underline": True}
                ]
            },
            # 2
            # PARAGRAPH 2
            {"type": "paragraph", "children": []},
            # 3
            # PARAGRAPH 3
            {
                "type": "paragraph",
                "align": "center",
                "children": [
                    {"text": "code example Lli", "code": True}
                ]
            },
            # 4
            # CAPTION 1
            {
                "type": "caption",
                "align": "center",
                "children": [
                    {"text": "This is the figure caption 1"}
                ]
            },
            # 5
            # PARAGRAPH 4
            {"type": "paragraph", "children": []},
            # 6
            # IMAGE 1
            {"type": "image-uuid", "image_uuid": "5bacc2bc-5b90-4c47-93d7-d9291911c4b3"},
            # 7
            # BLOCK QUOTE 1
            {"type": "block-quote", "children": [{"text": "This is a test for Block Quote"}]},
            # 8
            # BLOCK QUOTE 2
            {"type": "block-quote", "children": [{"text": "With multiple lines"}]},
            # 9
            # BULLETED LIST 1
            {"type": "bulleted-list", "children": [
                {"type": "list-item", "children": [{"text": "Item1"}]},
                {"type": "list-item", "children": [{"text": "Item2"}]}
            ]},
            # 10
            # PARAGRAPH 5
            {"type": "paragraph", "children": []},
            # 11
            # NUMBERED LIST 1
            {"type": "numbered-list", "children": [
                {"type": "list-item", "children": [{"text": "AAA"}]},
                {"type": "list-item", "children": [{"text": "BBB"}]}
            ]},
            # 12
            # PARAGRAPH 6
            {"type": "paragraph", "children": []},
            # 13
            # PARAGRAPH 7
            {
                "type": "paragraph",
                "align": "center",
                "children": [
                    {"text": "Separation between two lists"}
                ]
            },
            # 14
            # PARAGRAPH 8
            {"type": "paragraph", "children": []},
            # 15
            # NUMBERED LIST 2
            {"type": "numbered-list", "children": [
                {"type": "list-item", "children": [{"text": "CCC"}]},
                {"type": "list-item", "children": [{"text": "DDD"}]}
            ]},
            # 16
            # PARAGRAPH 9
            {"type": "paragraph", "children": []},
            # 17
            # TABLE
            {
                "type": "table",
                "children": [
                    {
                        "type": "table-row",
                        "children": [
                            {
                                "type": "table-cell",
                                "children": [
                                    {
                                        "type": "paragraph",
                                        "align": "right",
                                        "children": [
                                            {
                                                "text": "aa"
                                            }
                                        ]
                                    }
                                ]
                            },
                            {
                                "type": "table-cell",
                                "children": [
                                    {
                                        "type": "paragraph",
                                        "children": [
                                            {
                                                "text": "bb"
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "type": "table-row",
                        "children": [
                            {
                                "type": "table-cell",
                                "children": [
                                    {
                                        "type": "paragraph",
                                        "children": [
                                            {
                                                "text": "cc"
                                            }
                                        ]
                                    }
                                ]
                            },
                            {
                                "type": "table-cell",
                                "children": [
                                    {"type": "bulleted-list", "children": [
                                        {"type": "list-item", "children": [{"text": "Item in cell 1"}]},
                                        {"type": "list-item", "children": [{"text": "Item in cell 2"}]}
                                    ]}
                                ]
                            }
                        ]
                    }
                ]
            },
            # 18
            # CAPTION 2
            {"type": "caption", "children": [{"text": "This is the figure caption 2 "}, {"text": "with some bold", "bold": True}]},
            # 19
            # PARAGRAPH 10
            {"type": "paragraph", "children": []},
            # 20
            # IMAGE 2
            {"type": "image", "image_path": "https://www.vivelapub.fr/wp-content/uploads/2012/01/mire-tdf.jpg"},
            {"type": "image", "image_path": "/etc/passwd"}
        ]

        data = {
            'value': json.dumps(richtext_content)
        }

        style_mapping = {
                "heading-1": "Heading1",
                "heading-2": "Heading2",
                "heading-3": "Heading3",
                "heading-4": "Heading4",
                "heading-5": "Heading5",
                "heading-6": "Heading6",
                "block-quote": "BlockQuote",
                "block-code": "BlockCode",
                "numbered-list": "APNumbered",
                "bulleted-list": "APBulleted",
                "caption": "Caption"
            }

        self._subject.generate_docx(
            self._base_path,
            os.path.join(self._template_path, 'richtext_global_template.docx'),
            data,
            os.path.join(self._results_path, self._output_filenames['richtext_result']),
            style_mapping
        )

        result_file = Document(os.path.join(self._results_path, self._output_filenames['richtext_result']))  # type: Document

        result_file_paragraphs = result_file.paragraphs

        # HEADING 1
        h1_paragraph = result_file_paragraphs[0]  # type: Paragraph
        self.assertEqual('Heading 1', h1_paragraph.style.name)
        self.assertEqual(richtext_content[0].get('children', [])[0].get('text'), h1_paragraph.text)

        # PARAGRAPH 1
        paragraph1 = result_file_paragraphs[1]  # type: Paragraph
        paragraph1_r1 = paragraph1.runs[0]
        self.assertEqual(richtext_content[1].get('children', [])[0].get('text'), paragraph1_r1.text)
        paragraph1_r2 = paragraph1.runs[1]
        self.assertEqual(richtext_content[1].get('children', [])[1].get('text'), paragraph1_r2.text)
        self.assertEqual(True, paragraph1_r2.bold)
        paragraph1_r3 = paragraph1.runs[2]
        self.assertEqual(richtext_content[1].get('children', [])[2].get('text'), paragraph1_r3.text)
        self.assertEqual(True, paragraph1_r3.italic)
        self.assertEqual(True, paragraph1_r3.underline)

        # PARAGRAPH 2
        paragraph2 = result_file_paragraphs[2]  # type: Paragraph
        self.assertEqual('', paragraph2.text)

        # PARAGRAPH 3
        paragraph3 = result_file_paragraphs[3]  # type: Paragraph
        self.assertEqual(WD_PARAGRAPH_ALIGNMENT.CENTER, paragraph3.alignment)
        paragraph3_r1 = paragraph3.runs[0]
        self.assertEqual(richtext_content[3].get('children', [])[0].get('text'), paragraph3_r1.text)
        self.assertEqual('Courier New', paragraph3_r1.font.name)
        self.assertEqual(WD_COLOR_INDEX.GRAY_25, paragraph3_r1.font.highlight_color)

        # CAPTION 1
        caption1 = result_file_paragraphs[4]  # type: Paragraph
        self.assertEqual(WD_PARAGRAPH_ALIGNMENT.CENTER, caption1.alignment)
        self.assertEqual(4, len(caption1.runs))
        caption1_r1 = caption1.runs[0]
        self.assertEqual('Figure ', caption1_r1.text)
        caption1_r2 = caption1.runs[1]  # type: Run
        # TODO: Test if caption numbering exist
        caption1_r3 = caption1.runs[2]  # type: Run
        self.assertEqual(' ', caption1_r3.text)
        caption1_r4 = caption1.runs[3]  # type: Run
        self.assertEqual(richtext_content[4].get('children')[0].get('text'), caption1_r4.text)

        # PARAGRAPH 4
        paragraph2 = result_file_paragraphs[5]  # type: Paragraph
        self.assertEqual('', paragraph2.text)

        # IMAGE 1
        image1 = result_file_paragraphs[6]  # type: Paragraph
        image1_r1 = image1.runs[0]  # type: Run
        self.assertEqual(1, len(list(image1_r1.iter_inner_content())))
        self.assertEqual(Drawing, type(list(image1_r1.iter_inner_content())[0]))

        # BLOCK QUOTE 1
        block_quote1 = result_file_paragraphs[7]  # type: Paragraph
        self.assertEqual(style_mapping['block-quote'], block_quote1.style.style_id)
        self.assertEqual(richtext_content[7].get('children', [])[0].get('text'), block_quote1.text)

        # BLOCK QUOTE 2
        block_quote1 = result_file_paragraphs[8]  # type: Paragraph
        self.assertEqual(style_mapping['block-quote'], block_quote1.style.style_id)
        self.assertEqual(richtext_content[8].get('children', [])[0].get('text'), block_quote1.text)

        # BULLETED LIST 1
        bulleted_list1_item1 = result_file_paragraphs[9]  # type: Paragraph
        self.assertEqual(style_mapping['bulleted-list'], bulleted_list1_item1.style.style_id)
        self.assertEqual(richtext_content[9].get('children', [])[0].get('children', [])[0].get('text'), bulleted_list1_item1.text)

        bulleted_list1_item2 = result_file_paragraphs[10]  # type: Paragraph
        self.assertEqual(style_mapping['bulleted-list'], bulleted_list1_item2.style.style_id)
        self.assertEqual(richtext_content[9].get('children', [])[1].get('children', [])[0].get('text'), bulleted_list1_item2.text)

        # PARAGRAPH 5
        paragraph2 = result_file_paragraphs[11]  # type: Paragraph
        self.assertEqual('', paragraph2.text)

        # NUMBERED LIST 1
        numbered_list1_item1 = result_file_paragraphs[12]  # type: Paragraph
        self.assertEqual(style_mapping['numbered-list'], numbered_list1_item1.style.style_id)
        self.assertEqual(richtext_content[11].get('children', [])[0].get('children', [])[0].get('text'), numbered_list1_item1.text)

        numbered_list1_item2 = result_file_paragraphs[13]  # type: Paragraph
        self.assertEqual(style_mapping['numbered-list'], numbered_list1_item2.style.style_id)
        self.assertEqual(richtext_content[11].get('children', [])[1].get('children', [])[0].get('text'), numbered_list1_item2.text)

        # PARAGRAPH 6
        paragraph6 = result_file_paragraphs[14]  # type: Paragraph
        self.assertEqual('', paragraph6.text)

        # PARAGRAPH 7
        paragraph7 = result_file_paragraphs[15]  # type: Paragraph
        self.assertEqual(WD_PARAGRAPH_ALIGNMENT.CENTER, paragraph7.alignment)
        self.assertEqual('Separation between two lists', paragraph7.text)

        # PARAGRAPH 8
        paragraph8 = result_file_paragraphs[16]  # type: Paragraph
        self.assertEqual('', paragraph8.text)

        # NUMBERED LIST 2
        numbered_list2_item1 = result_file_paragraphs[17]  # type: Paragraph
        self.assertEqual(style_mapping['numbered-list'], numbered_list2_item1.style.style_id)
        self.assertEqual(richtext_content[15].get('children', [])[0].get('children', [])[0].get('text'), numbered_list2_item1.text)

        numbered_list2_item2 = result_file_paragraphs[18]  # type: Paragraph
        self.assertEqual(style_mapping['numbered-list'], numbered_list2_item2.style.style_id)
        self.assertEqual(richtext_content[15].get('children', [])[1].get('children', [])[0].get('text'), numbered_list2_item2.text)

        # PARAGRAPH 9
        paragraph9 = result_file_paragraphs[19]  # type: Paragraph
        self.assertEqual('', paragraph9.text)

        # TODO: test table
        # TABLE
        table = result_file.tables

        # CAPTION 2
        caption2 = result_file_paragraphs[20]  # type: Paragraph
        self.assertEqual(WD_PARAGRAPH_ALIGNMENT.CENTER, caption1.alignment)
        self.assertEqual(4, len(caption1.runs))
        caption2_r1 = caption2.runs[0]
        self.assertEqual('Figure ', caption2_r1.text)
        caption2_r2 = caption2.runs[1]  # type: Run
        # TODO: Test if caption numbering exist
        caption2_r3 = caption2.runs[2]  # type: Run
        self.assertEqual(' ', caption2_r3.text)
        caption3_r4 = caption2.runs[3]  # type: Run
        self.assertEqual(richtext_content[18].get('children')[0].get('text'), caption3_r4.text)
        caption3_r5 = caption2.runs[4]  # type: Run
        self.assertEqual(richtext_content[18].get('children')[1].get('text'), caption3_r5.text)

        # PARAGRAPH 10
        paragraph10 = result_file_paragraphs[21]  # type: Paragraph
        self.assertEqual('', paragraph10.text)

        # IMAGE 2
        image2 = result_file_paragraphs[22]  # type: Paragraph
        image2_r1 = image2.runs[0]  # type: Run
        self.assertEqual(1, len(list(image2_r1.iter_inner_content())))
        self.assertEqual(Drawing, type(list(image2_r1.iter_inner_content())[0]))
