# _*_ coding: utf-8

from odf import teletype, text
from odf.opendocument import load, OpenDocumentText
from odf.element import Text
from odf.text import P, H, Span
from pathlib import Path


class Family:
    PARAGRAPH = 'paragraph'
    TEXT = 'text'
    ALL = (PARAGRAPH, TEXT)


class TagName:
    Span = 'text:span'
    P = 'text:p'
    H = 'text:h'


class Style(object):
    def __init__(self, _name=None):
        if _name is None:
            return
        self.name = _name
        self.family = None
        self.is_autostyle = False
        self.is_default_style = False
        self.rsid = None
        self.parent_style = None
        self.font_name = None
        self.font_family = None

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


class ParaStyle(Style):
    pass


class CharStyle(Style):
    pass


# XML namespaces.
_ns_text = 'urn:oasis:names:tc:opendocument:xmlns:text:1.0'
_ns_style = 'urn:oasis:names:tc:opendocument:xmlns:style:1.0'
_ns_officeooo = 'http://openoffice.org/2009/office'
_ns_fo = 'urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0'


class Odt(object):
    # TODO: коррекция meta данных.
    # https://github.com/eea/odfpy/issues/105
    # Удалить, если есть,
    # лишние текстовые элементы (\n\n\n\n\) из мета-данных.

    def __init__(self, _odt=None):
        self.url = _odt
        self.p_odt = Path(_odt)
        self.extension = None
        self.converter = None
        self.style_font = None
        self.doc = load(self.url)
        self.auto_styles = self.doc.automaticstyles
        self.styles = self.doc.styles
        self.para_list = self.doc.getElementsByType(P)
        self.headers_list = self.doc.getElementsByType(H)
        self.spans_list = self.doc.getElementsByType(Span)

        self.styles_list = []
        self.styles_handle()
        self.autostyles_handle()
        try:
            self.styles_list = self.styles_get_fonts_from_parent_style()
        except Exception as e:
            raise e

    def __str__(self):
        return self.url

    def __repr__(self):
        return self.url

    def set_converter(self, _converter):
        self.converter = _converter

    def set_style_font(self, _style_font):
        self.style_font = _style_font

    def set_extension(self, _extension):
        self.extension = f'.{_extension}'

    def autostyles_handle(self):
        for _st in self.auto_styles.childNodes:
            _name = _st.getAttribute('name')
            _family = _st.attributes.get((_ns_style, 'family'))
            _parent_style = _st.attributes.get((_ns_style, 'parent-style-name'))
            _rsid = None
            _font_name = None
            for _prop_node in _st.childNodes:
                if _family == Family.PARAGRAPH:
                    _rsid = _prop_node.attributes.get((_ns_officeooo, 'paragraph-rsid'))
                elif _family == Family.TEXT:
                    _rsid = _prop_node.attributes.get((_ns_officeooo, 'rsid'))
                _font_name = _prop_node.attributes.get((_ns_style, 'font-name'))

            style = Style(_name)
            style.is_autostyle = True
            style.family = _family
            style.parent_style = _parent_style
            style.rsid = _rsid
            style.font_name = _font_name
            self.styles_list.append(style)

    def styles_handle(self):
        # print('STYLES============')
        for _st in self.styles.childNodes:
            _style_name = _st.attributes.get((_ns_style, 'name'))
            _style_family = _st.attributes.get((_ns_style, 'family'))
            _parent_style_name = _st.attributes.get((_ns_style, 'parent-style-name'))
            _font_name = None
            _font_family = None
            if _style_family in (Family.PARAGRAPH, Family.TEXT):
                if _style_family == Family.PARAGRAPH \
                        and not _style_name \
                        and _st.qname[1] == 'default-style':
                    _style_name = 'default-style'
                if _style_name == 'Standard':
                    _parent_style_name = 'default-style'

                for _elem in _st.childNodes:
                    if _elem.qname[1] == 'text-properties':
                        _font_name = _elem.attributes.get((_ns_style, 'font-name'))
                        _font_family = _elem.attributes.get((_ns_fo, 'font-family'))

                style = Style(_style_name)
                style.family = _style_family
                style.parent_style = _parent_style_name
                style.font_name = _font_name
                style.font_family = _font_family
                self.styles_list.append(style)

    def get_style_by_name(self, _style_name):
        for _style_obj in self.styles_list:
            if _style_name == _style_obj.name:
                return _style_obj
        return None

    def styles_get_fonts_from_parent_style(self):
        _out_styles_list = []

        def walk_on_parent_styles(_style):
            if _style.font_name:
                return _style.font_name
            try:
                if _style.parent_style:
                    _parent_style_name = _style.parent_style
                    _parent_style = self.get_style_by_name(_parent_style_name)
                    assert _parent_style, f'Can\'t get_parent style for style={_style}!'

                    if _parent_style.font_name:
                        return _parent_style.font_name
                    else:
                        _parent_font_name = walk_on_parent_styles(_parent_style)
                        if _parent_font_name:
                            return _parent_font_name
                        else:
                            return None
                else:
                    return None
            except AttributeError as e:
                raise e

        for _st in self.styles_list:
            if _st.font_name is None:
                try:
                    _font_name = walk_on_parent_styles(_st)
                except Exception as e:
                    raise e
                if _font_name:
                    _st.font_name = _font_name

            _out_styles_list.append(_st)
        return _out_styles_list

    def txt_handle(self, _element, _font):
        if type(_element) is Text:
            _txt = _element.data
            _txt_cnv = self.converter(_txt, _font_name=_font)
            _element.data = _txt_cnv
            # print(f'{_font}:{_txt_cnv}')
        return None

    def element_handle(self, _element):
        """Общий обработчик элементов (абзац, заголовок, span)

        :param _element:
        :return:
        """
        element_type = _element.tagName
        element_font = None
        element_style_name = _element.getAttribute('stylename')
        element_style = self.get_style_by_name(element_style_name)
        if element_style:
            element_font = element_style.font_name

        if element_type in (TagName.P, TagName.H):
            for _para_part in _element.childNodes:
                # Элементы непосредственно абзаца, вне span.
                self.txt_handle(_para_part, element_font)

        elif element_type == TagName.Span:
            _parent_node = _element.parentNode
            _parent_style_name = _parent_node.getAttribute('stylename')
            _parent_style = self.get_style_by_name(_parent_style_name)
            parent_node_font = None
            if _parent_style:
                parent_node_font = _parent_style.font_name

            for span_node in _element.childNodes:
                span_font = None
                if span_node.hasChildNodes():
                    # span_style_name = span_node.getAttribute('stylename')
                    span_style_name = span_node.attributes.get((_ns_style, 'stylename'))
                    span_style = self.get_style_by_name(span_style_name)
                    if span_style:
                        span_font = span_style.font_name

                    # Для текстовых стилей, у кот-х не указан шрифт.
                    if span_style and span_style.family == Family.TEXT and not span_font:
                        # Взять шрифт стиля parentNode.
                        span_font = parent_node_font
                else:
                    span_font = element_font
                    # Для текстовых стилей, у кот-х не указан шрифт.
                    if not span_font:
                        span_font = parent_node_font

                self.txt_handle(span_node, span_font)

    def spans_handle(self):
        """Обработчик элементов span.

        """
        for _span in self.spans_list:
            self.element_handle(_span)

    def paragraphs_handle(self):
        for _para in self.para_list:
            self.element_handle(_para)

    def headers_handle(self):
        for _header in self.headers_list:
            self.element_handle(_header)

    def set_font_for_all_styles(self):
        def set_font_to_style(_doc_style):
            if _doc_style and _doc_style.hasChildNodes():
                _text_prop = None
                for _elem in _doc_style.childNodes:
                    if _elem.qname[1] == 'text-properties':
                        _text_prop = _elem
                        # Атрибуты задаются без дефисов!!!
                        _text_prop.setAttribute('fontname', self.style_font)
                        _text_prop.setAttribute('fontfamily', self.style_font)
            # else:
            #     # Для стилей у которых не задано ничего.
            #     # TODO: добавить text-properties?
            #     # print(f'empty')
            #     # _name = _doc_style.attributes.get((_ns_style, 'name'))
            #     # style_obj = get_style_by_name(_name)

        for _style in self.styles_list:
            _doc_style = None
            if _style.font_name:
                if _style.name == 'default-style':
                    for _style_elem in self.styles.childNodes:
                        _style_family = _style_elem.attributes.get((_ns_style, 'family'))
                        _qname = _style_elem.qname[1]
                        if _qname == 'default-style' \
                                and _style_family == Family.PARAGRAPH:
                            _doc_style = _style_elem
                            break
                else:
                    _doc_style = self.doc.getStyleByName(_style.name)
                set_font_to_style(_doc_style)

    def convert_with_saving_format(self):
        """Конвертация текста в файле ODT.

        Абзацы, Заголовки, Span-элементы. Форматирование сохраняется.
        Результат записывается в файл *.cnv.odt
        :return: None
        """
        self.paragraphs_handle()
        self.headers_handle()
        self.spans_handle()

        # Замена шрифта в стилях.
        if self.style_font:
            self.set_font_for_all_styles()

        _suffix = '.cnv.odt'
        if self.extension:
            _suffix = self.extension

        new_odt = self.p_odt.with_suffix(_suffix)
        self.doc.save(new_odt.as_posix())

    def convert_text_only(self):
        """Конвертация текста в файле ODT.

        Конвертируется все содерржимое <body>.
        Результат записывается в файл *.cnv.odt
        :return: None
        """

        body = self.doc.body
        new_doc = OpenDocumentText()
        for _body_elem in body.childNodes:
            for _elem in _body_elem.childNodes:
                body_text = teletype.extractText(_elem)
                body_text = self.converter(body_text)
                para = text.P()
                teletype.addTextToElement(para, body_text)
                new_doc.text.addElement(para)
                # print(body_text)

        # Замена шрифта в стилях.
        if self.style_font:
            self.set_font_for_all_styles()

        _suffix = '.all.odt'
        if self.extension:
            _suffix = self.extension

        new_odt = self.p_odt.with_suffix(_suffix)
        new_doc.save(new_odt.as_posix())

    def get_text(self):
        out_text = ''
        body = self.doc.body
        for _body_elem in body.childNodes:
            for _elem in _body_elem.childNodes:
                body_text = teletype.extractText(_elem)
                out_text += f'{body_text}\n'
        return out_text


def convert_unicode_to_ucs(_string, _font_name=None):
    from Onik_functions import unicode_to_ucs
    _out = unicode_to_ucs(_string)
    return _out


def convert_ucs_to_unicode_by_font(_string: str, _font_name=None):
    """Конвертация текста UCS->Unicode согласно шрифта.

    :param _string:
    :param _font_name:
    :return:
    """
    from Ucs_functions import get_font_table, ucs_convert_string_with_font_bforce

    out = _string
    if _font_name is None:
        # raise OdtError('No font!')
        return out
    font_table = get_font_table(_font_name)
    # Конвертация.
    out = ucs_convert_string_with_font_bforce(_string, font_table)
    return out


def convert_test(_string: str):
    _out = _string.upper()
    return _out


def get_text_from_odt(_odt, save_blank=None) -> str:
    """Выводит текст odt документа.

    Абзацы (\n), табуляции(\t), переносы строк (\n) обрабатываются.
    :param _odt:
    :param save_blank: Сохранять ли промежутки между абзацами как \n
    :return: text
    """
    # TODO: save_blank - как в pandoc.
    doc = load(_odt)
    out_text = ''
    body = doc.body
    for _body_elem in body.childNodes:
        for _elem in _body_elem.childNodes:
            body_text = teletype.extractText(_elem)
            out_text += f'{body_text}\n'
    return out_text


if __name__ == "__main__":
    # Пример использования (UCS->Unicode).
    odt = '/home/user/tmp/0001.odt'
    try:
        odt_obj = Odt(odt)
    except Exception as e:
        raise e
    pass
    # odt_obj.set_converter(convert_ucs_to_unicode_by_font)
    # odt_obj.set_style_font('Ponomar Unicode')
    # odt_obj.convert_with_saving_format()

    # Пример использования (Unicode->UCS).
    # odt = 'd:/Temp/prazdnichnaja-mineja-ucs.odt'
    # odt_obj = Odt(odt)
    # odt_obj.set_converter(convert_unicode_to_ucs)
    # odt_obj.set_style_font('Triodion Ucs')
    # odt_obj.convert_with_saving_format()
