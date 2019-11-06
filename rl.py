import numpy as np
from random import choice
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.graphics.barcode import code39, code128, code93
from reportlab.graphics.barcode import eanbc, qr, usps
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF

import JsonLoader

class youl_invoice_gen():
    def __init__(self, top_margin_mean=12, left_margin_mean=7, page_width_mean=70, num_item_mean = 5, font_size_mean=10, char_space_mean=1, line_offset_mean=1):
        #=====Objects=====


        #=====Learnable Parameters=====
        #=====Gaussian=====
        self.top_margin_mean = top_margin_mean
        self.left_margin_mean = left_margin_mean
        self.page_width_mean = page_width_mean
        self.num_item_mean = num_item_mean
        self.font_size_mean = font_size_mean
        self.char_space_mean = char_space_mean
        self.line_offset_mean = line_offset_mean

        #self.prefer_separate_type = prefer_separate_type
        #self.prefer_font_type = prefer_font_type
        #=====Dataset as PriorKnowledge=====

        self.fonts = ['Courier', 'Courier-Bold', 'Courier-BoldOblique', 'Courier-Oblique', 'Helvetica', 'Helvetica-Bold', 'Helvetica-BoldOblique', 'Helvetica-Oblique', 'Times-Bold', 'Times-BoldItalic', 'Times-Italic', 'Times-Roman']
        self.separators = [' ', '-', '~', '*']

        #=====Inferred Parameters=====


    def infer(self):
        self.top_margin_std = self.top_margin_mean / 3
        self.left_margin_std = self.left_margin_mean / 3
        self.page_width_std = self.page_width_mean / 30
        self.num_item_std = self.num_item_mean / 3
        self.font_size_std = self.font_size_mean / 3
        self.char_space_std = self.char_space_mean / 3
        self.line_offset_std = self.line_offset_mean / 3

    def get_string_x(self, string, font, size, charspace):
        width = stringWidth(string, font, size)
        width += (len(string) - 1) * charspace
        return width

    def draw_item(self, name, amount, font, font_size):
        textobj = self.c.beginText()
        textobj.setFont(font, font_size)
        textobj.setTextOrigin(self.left_margin*mm, self.y_cursor*mm)
        textobj.setCharSpace(self.char_space)
        textobj.textLine(name)
        self.c.drawText(textobj)

        amount_name = '$' +str(amount)
        textobj = self.c.beginText()
        textobj.setFont(font, font_size)
        textobj.setTextOrigin((self.page_width - self.left_margin - self.get_string_x(amount_name, font, font_size, self.char_space)/mm)*mm, self.y_cursor*mm)
        textobj.setCharSpace(self.char_space)
        textobj.textLine(amount_name)
        self.c.drawText(textobj)
        self.y_cursor -= font_size/mm + self.line_offset

    def draw_separator(self, font, font_size):
        textobj = self.c.beginText()
        textobj.setFont(font, font_size)
        separator_str = ''
        while self.get_string_x(separator_str, font, font_size, self.char_space) < self.page_width*mm - self.left_margin*mm * 2:
            separator_str += self.separator
        textobj.setTextOrigin(self.left_margin*mm, self.y_cursor*mm)
        textobj.setCharSpace(self.char_space)
        textobj.textLine(separator_str)
        self.c.drawText(textobj)
        self.y_cursor -= font_size/mm + self.line_offset

    def draw_barcode(self, barcode_value):
        barcode39 = code39.Extended39(barcode_value, barHeight=5*mm)
        self.y_cursor -= 5
        barcode39.drawOn(self.c, (self.page_width*mm - barcode39.width) / 2.0, self.y_cursor*mm)
        self.y_cursor -= 15

    def draw_qr(self):
        qr_code = qr.QrCodeWidget('www.mousevspython.com')
        self.y_cursor -= 5
        bounds = qr_code.getBounds()
        width = bounds[2] - bounds[0]
        height = bounds[3] - bounds[1]
        d = Drawing(45, 45, transform=[45./width,0,0,45./height,0,0])
        d.add(qr_code)
        renderPDF.draw(d, self.c, (self.page_width*mm - width) / 2.0, self.y_cursor*mm)
        self.y_cursor -= 15

    def draw_address(self, font, font_size):
        loader = JsonLoader.JsonLoader("Evanston")
        loader.new_item()
        name = loader.get_name()

        if loader.has_logo():
            print("has_logo")
            self.y_cursor -= 20
            self.c.drawImage("database/logos/" + name + ".png", 10*mm, self.y_cursor*mm, width=None,height=None, preserveAspectRatio=True, anchor='c')
            self.y_cursor -= 10

        textobj = self.c.beginText()
        textobj.setFont(font, font_size)
        textobj.setTextOrigin((self.page_width - self.get_string_x(name, font, font_size, self.char_space)/mm)*mm / 2.0, self.y_cursor*mm)
        textobj.setCharSpace(self.char_space)
        textobj.textLine(name)
        self.c.drawText(textobj)
        self.y_cursor -= font_size/mm + self.line_offset

        address = loader.get_address()[0]
        textobj = self.c.beginText()
        textobj.setFont(font, font_size)
        textobj.setTextOrigin((self.page_width - self.get_string_x(address, font, font_size, self.char_space)/mm)*mm / 2.0, self.y_cursor*mm)
        textobj.setCharSpace(self.char_space)
        textobj.textLine(address)
        self.c.drawText(textobj)
        self.y_cursor -= font_size/mm + self.line_offset

        phone = loader.get_phone()
        textobj = self.c.beginText()
        textobj.setFont(font, font_size)
        textobj.setTextOrigin((self.page_width - self.get_string_x(phone, font, font_size, self.char_space)/mm)*mm / 2.0, self.y_cursor*mm)
        textobj.setCharSpace(self.char_space)
        textobj.textLine(phone)
        self.c.drawText(textobj)
        self.y_cursor -= font_size/mm + self.line_offset

        self.y_cursor -= 10


    def draw_invoice(self):
        #=====Init Invoice=====
        page_height = 300
        self.page_width = max(0, int(np.random.normal(self.page_width_mean, self.page_width_std)))
        print ('page_width: %d' % self.page_width)
        item_font_size = max(0, int(np.random.normal(self.font_size_mean, self.font_size_std)))
        print ('font_size: %d' % item_font_size)
        self.left_margin = max(0, int(np.random.normal(self.left_margin_mean, self.left_margin_std)))
        print ('left_margin: %d' % self.left_margin)
        top_margin = max(0, int(np.random.normal(self.top_margin_mean, self.top_margin_std)))
        print ('top_margin: %d' % top_margin)
        num_item = max(0, int(np.random.normal(self.num_item_mean, self.num_item_std)))
        print ('top_margin: %d' % top_margin)
        self.char_space = max(0, int(np.random.normal(self.char_space_mean, self.char_space_std)))
        print ('char_space: %d' % self.char_space)
        self.line_offset = max(0, int(np.random.normal(self.line_offset_mean, self.line_offset_std)))
        print ('line_offset: %d' % self.line_offset)
        font = choice(self.fonts)
        print ('font: %s' % font)
        self.separator = choice(self.separators)
        print ('separator: %s' % self.separator)
        self.y_cursor = (page_height - top_margin - (item_font_size + self.line_offset) /mm)
        print ('y_cursor: %d' % self.y_cursor)

        subtotal = 0

        self.c = canvas.Canvas('youl.pdf', (self.page_width*mm, page_height*mm))
        self.draw_address(font, item_font_size)
        for item_idx in range(num_item):
            amount = np.random.randint(30) + 0.99
            subtotal += amount
            self.draw_item('cusine', amount, font, item_font_size)
        self.draw_separator(font, item_font_size)

        subtotal = round(subtotal * 1.00, 2)
        self.draw_item('Subtotal:', subtotal, font, item_font_size)
        tax_rate = 0.1
        tax_amount = round(subtotal * (tax_rate), 2)
        self.draw_item('Tax:', tax_amount, font, item_font_size)
        self.draw_separator(font, item_font_size)

        total = round(subtotal * (1.0 + tax_rate) * 1.00, 2)
        self.draw_item('Total:', total, font, item_font_size)

        self.draw_barcode("1234567890")
        self.draw_qr()

        self.c.showPage()
        self.c.save()




if __name__ == '__main__':
    a = youl_invoice_gen()
    a.infer()
    a.draw_invoice()
