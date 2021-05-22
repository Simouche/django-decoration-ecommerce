import io
import os
import uuid
from io import BytesIO

from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, FileResponse
from django.template.loader import get_template, render_to_string
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from xhtml2pdf import pisa

from decoration import settings
from decoration.settings import BASE_DIR


class OrderToPDF:
    document_template_class = None
    file_name = None
    page_size = None
    data = None
    table_style_class = None
    options = None

    def __init__(self, *args, **kwargs):
        self.document_template_class = kwargs.get('document_template_class')
        self.file_name = kwargs.get('file_name')
        self.page_size = kwargs.get('page_size')
        self.data = kwargs.get('data')
        self.table_style_class = kwargs.get('table_style_class')
        self.options = kwargs.get('options')

    def get_pdf(self):
        pdf = self.get_document_template_class()(self.get_file_name(), pagesize=self.get_page_size())
        return pdf

    def get_document_template_class(self):
        if self.document_template_class is not None:
            return self.document_template_class
        return SimpleDocTemplate

    def get_file_name(self) -> str:
        if self.file_name is not None:
            return self.generate_file_name(file_name=self.file_name)
        self.file_name = self.generate_file_name()
        return self.file_name

    def generate_file_name(self, file_name=None) -> str:
        """
        :rtype: str
        """
        if file_name:
            if file_name.endswith("pdf"):
                return f"uploads/invoices/{file_name}"
            else:
                return f"uploads/invoices/{file_name}.pdf"
        uuid_str = uuid.uuid4().__str__().replace('-', '')
        name = f"uploads/invoices/{uuid_str}.pdf"
        return name

    def get_page_size(self) -> tuple:
        if self.page_size is not None:
            return self.page_size
        return letter

    def get_data(self):
        if self.data is not None:
            return self.data
        raise ValueError("you need data to generate the pdf.")

    def get_table(self):
        table = Table(self.get_data(), style=self.get_table_style())

        return table

    def get_pdf_elements(self):
        elements = [self.get_header(), self.get_client_info(), self.get_table()]

        return elements

    def build_pdf(self):
        pdf = self.get_pdf()
        pdf.build(self.get_pdf_elements())
        return pdf

    def get_table_style(self):
        if self.table_style_class is not None:
            return self.table_style_class(self.get_style_options())
        return TableStyle(self.get_style_options())

    def get_style_options(self):
        if self.options is not None:
            return self.options

        options = [
            # Table Header Options
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),  # table header background.
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.gold),  # table header text color.
            ('FONTNAME', (0, 0), (-1, 0), 'Courier-Bold'),  # change font for the table header.
            ('FONTSIZE', (0, 0), (-1, 0), 14),  # change font size for the table header.
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),  # add more padding the bottom of the table header by pixels.

            # Global Table Options
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # align all text in all cells to center.

            # Table Body Options
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),  # table body background
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),  # table body background
            ('LINEABOVE', (0, -1), (-1, -1), 2, colors.black),

        ]

        return options

    def get_header(self):
        return Paragraph("SamyDeco")

    def get_client_info(self):
        paragraph = Paragraph()
        return Paragraph(
            """
            Client: Wassim\n
            Phone: 0799136332\n
            Addresse: edsqfklqsdlkjfhqslkdjfhkljqsdhfklj\n
            Commune: Alger\n
            Expidié le: 12/12/92 12:12\n
            """)


def render_to_pdf(template_src, context_dict=None):
    if context_dict is None:
        context_dict = {}

    template = get_template(template_src)
    html = render_to_string(template_src, context_dict, context_dict.get('request'))
    result = io.StringIO()
    name = uuid.uuid4().__str__().replace("-", "")
    pdf = pisa.pisaDocument(io.StringIO(html.encode("UTF-8")), result, link_callback=fetch_resources)
    with open(BASE_DIR / "uploads/invoices/" / (name + ".pdf"), "w") as f:
        f.write(result.getvalue())

    fss = FileSystemStorage(BASE_DIR / "uploads/invoices")
    file = fss.open(name + ".pdf")
    file_url = "/uploads/invoices/" + name + ".pdf"

    return FileResponse(file, as_attachment=True, filename=name + ".pdf")


def render_to_pdf2(template_src, context_dict=None):
    if context_dict is None:
        context_dict = {}

    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("utf8")), result, link_callback=fetch_resources)
    name = uuid.uuid4().__str__().replace("-", "")
    with open(BASE_DIR / "uploads/invoices/" / (name + ".pdf"), "wb") as f:
        f.write(result.getvalue())

    fss = FileSystemStorage(BASE_DIR / "uploads/invoices")
    file = fss.open(name + ".pdf")
    file_url = name + ".pdf"

    return file_url


def fetch_resources(uri, rel):
    path = os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ""))
    return path
