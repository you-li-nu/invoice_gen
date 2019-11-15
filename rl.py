import numpy as np
import random
from random import choice, randrange
from datetime import datetime, timedelta

from reportlab.lib import colors, utils
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
    def __init__(self, top_margin_mean=20, left_margin_mean=20, page_width_mean=300, num_item_mean = 5, font_size_mean=10, char_space_mean=3, line_offset_mean=3):
        #=====Objects=====
        self.ground_truth = ''


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
        self.payments = ['VISA CREDIT', 'VISA (SWIPED)', 'VISA (CHIP)', 'MASTERCARD CREDIT', 'MASTERCARD (SWIPED)', 'MASTERCARD (CHIP)', 'AMEX CREDIT', 'AMEX (SWIPED)', 'AMEX (CHIP)']
        self.appreciations = ['Thank You and Please Come Again', 'Thank you']

        #=====Inferred Parameters=====
        file = open('menu.txt','r') 
        self.rows = file.readlines()
        #print (self.rows)
        file.close()


    def infer(self):
        self.top_margin_std = self.top_margin_mean / 3
        self.left_margin_std = self.left_margin_mean / 3
        self.page_width_std = self.page_width_mean / 27
        #self.page_width_std = 0
        self.num_item_std = self.num_item_mean / 3
        self.font_size_std = self.font_size_mean / 9
        self.char_space_std = self.char_space_mean / 9
        self.line_offset_std = self.line_offset_mean / 3

    def get_string_x(self, string, font, size, charspace):
        width = stringWidth(string, font, size)
        width += (len(string) - 1) * charspace
        return width

    def draw_item(self, name, amount, font, font_size, qty=0):
        qty_width = 0
        if qty != 0:
            qty_width = font_size * 2 + self.char_space * 2 + 5
            self.draw_object(str(qty), font, font_size, x_origin=self.left_margin)
            self.y_cursor += font_size + self.line_offset

        self.draw_object(name, font, font_size, x_origin=self.left_margin + qty_width)
        self.y_cursor += font_size + self.line_offset

        amount_name = '$' +str(amount)
        self.draw_object(amount_name, font, font_size, x_origin=(self.page_width - self.left_margin - self.get_string_x(amount_name, font, font_size, self.char_space)))

    def draw_separator(self, font, font_size):
        textobj = self.c.beginText()
        textobj.setFont(font, font_size)
        separator_str = ''
        while self.get_string_x(separator_str, font, font_size, self.char_space) < self.page_width - self.left_margin * 2:
            separator_str += self.separator
        textobj.setTextOrigin(self.left_margin, self.y_cursor)
        textobj.setCharSpace(self.char_space)
        textobj.textLine(separator_str)
        self.c.drawText(textobj)
        self.y_cursor -= font_size + self.line_offset

    def draw_barcode(self, barcode_value):
        bar_height = 25
        barcode39 = code39.Extended39(barcode_value, barHeight=bar_height)
        self.y_cursor -= bar_height
        barcode39.drawOn(self.c, (self.page_width - barcode39.width) / 2.0, self.y_cursor)
        self.y_cursor -= 15

    def draw_qr(self):
        qr_code = qr.QrCodeWidget('www.mousevspython.com')
        bounds = qr_code.getBounds()
        width = bounds[2] - bounds[0]
        height = bounds[3] - bounds[1]
        d = Drawing(0, 0, transform=[60./width,0,0,60./height,0,0])
        d.add(qr_code)
        self.y_cursor -= height
        renderPDF.draw(d, self.c, self.left_margin + (self.page_width - width) / 2.0, self.y_cursor)
        self.y_cursor -= 15

    def draw_address(self, loader, font, font_size):
        
        name = loader.get_name()

        if loader.has_logo():
            print("has_logo")
            path = "database/logos/" + name + ".png"
            img = utils.ImageReader(path)
            img_width, img_height = img.getSize()
            self.y_cursor -= img_height/mm
            self.c.drawImage("database/logos/" + name + ".png", (self.page_width - img_width/mm) / 2.0, self.y_cursor, width=img_width/mm, height=img_height/mm, preserveAspectRatio=True, anchor='c')
            self.y_cursor -= 10

        self.draw_object(name, font, font_size)

        address = loader.get_address()[0]
        self.draw_object(address, font, font_size)

        phone = loader.get_phone()
        self.draw_object(phone, font, font_size)
        self.y_cursor -= 10

    def draw_header(self, font, font_size):
        qty_width = font_size * 2 + self.char_space * 2 + 5
        self.draw_object("QTY", font, font_size, x_origin=self.left_margin)
        self.y_cursor += font_size + self.line_offset

        self.draw_object("NAME", font, font_size, x_origin=self.left_margin + qty_width)
        self.y_cursor += font_size + self.line_offset

        self.draw_object("Amount", font, font_size, x_origin=(self.page_width - self.left_margin - self.get_string_x("Amount", font, font_size, self.char_space)))

    def write_ground_truth(self, name, lower_left_x, lower_left_y, width, height):
        self.ground_truth += str(round(lower_left_x, 2)) + ',' + str(round(self.page_height - lower_left_y - height, 2)) + ','#top_left
        self.ground_truth += str(round(lower_left_x + width, 2)) + ',' + str(round(self.page_height - lower_left_y - height, 2)) + ','#top_right
        self.ground_truth += str(round(lower_left_x + width, 2)) + ',' + str(round(self.page_height - lower_left_y, 2)) + ','#bottom_right
        self.ground_truth += str(round(lower_left_x, 2)) + ',' + str(round(self.page_height - lower_left_y, 2)) + ','#bottom_left
        self.ground_truth += name + '\n'

    def draw_object(self, s, font, font_size, x_origin=None):
        textobj = self.c.beginText()
        textobj.setFont(font, font_size)
        if x_origin == None:
            x_origin = (self.page_width - self.get_string_x(s, font, font_size, self.char_space)) / 2.0
        textobj.setTextOrigin(x_origin, self.y_cursor)
        textobj.setCharSpace(self.char_space)
        textobj.textLine(s)
        self.c.drawText(textobj)

        self.write_ground_truth(s, x_origin, self.y_cursor, self.get_string_x(s, font, font_size, self.char_space), font_size)

        self.y_cursor -= font_size + self.line_offset

    def draw_datetime(self, font, font_size):
        def random_date(start, end):
            """
            This function will return a random datetime between two datetime
            objects.
            """
            delta = end - start
            int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
            random_second = randrange(int_delta)
            return start + timedelta(seconds=random_second)
        d1 = datetime.strptime('1/1/2018 1:30 PM', '%m/%d/%Y %I:%M %p')
        d2 = datetime.strptime('1/1/2019 4:50 AM', '%m/%d/%Y %I:%M %p')

        dt = random_date(d1, d2)
        self.draw_object(str(dt), font, font_size)
        
    def draw_payment(self, font, font_size):
        payment = choice(self.payments)
        self.draw_object(payment, font, font_size, x_origin=self.left_margin)
        self.y_cursor += font_size + self.line_offset

        card_number = '*' + str(random.randrange(10**3, 10**4))
        self.draw_object(card_number, font, font_size, x_origin=(self.page_width - self.left_margin - self.get_string_x(card_number, font, font_size, self.char_space)))

    def draw_invoice(self, height=1000):
        #=====Init Invoice=====
        self.page_height = height
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
        self.y_cursor = (self.page_height - top_margin - (item_font_size + self.line_offset))
        init_y_cursor = self.y_cursor
        print ('y_cursor: %d' % self.y_cursor)
        has_header = bool(random.getrandbits(1))
        
        loader = JsonLoader.JsonLoader("Evanston")
        loader.new_item()

        for epoch in range(2):#First epoch is to estimate page_height
		
            subtotal = 0
            total_qty = 0
            self.ground_truth = ''
            self.y_cursor = (self.page_height - top_margin - (item_font_size + self.line_offset))
            self.c = canvas.Canvas('youl.pdf', (self.page_width, self.page_height))
            self.draw_address(loader, font, item_font_size)

            
            if has_header:
                self.draw_header(font, item_font_size)
                self.draw_separator(font, item_font_size)
            for item_idx in range(num_item):
                amount = np.random.randint(30) + 0.99
                qty = np.random.geometric(p=0.7)
                if qty >= 10:
                    qty = 1
                subtotal += amount * qty
                total_qty += qty
                #self.draw_item('cusine', amount * qty, font, item_font_size, qty)
                cusine = ''
                while True:
                    cusine = random.choice(self.rows)
                    if len(cusine) < 22:
                        break
					
                self.draw_item(cusine.strip(), amount * qty, font, item_font_size, qty)
            self.draw_separator(font, item_font_size)

            subtotal = round(subtotal * 1.00, 2)
            self.draw_item('Subtotal:', subtotal, font, item_font_size)
            tax_rate = 0.10
            tax_amount = round(subtotal * (tax_rate), 2)
            self.draw_item('Tax:', tax_amount, font, item_font_size)
            self.draw_separator(font, item_font_size)

            total = round(subtotal * (1.0 + tax_rate) * 1.00, 2)
            self.draw_item('Total:', total, font, item_font_size + 0)
            #self.draw_item('Quantity:', total_qty, font, item_font_size)
            self.draw_separator(font, item_font_size)
            self.draw_payment(font, item_font_size)

            self.draw_barcode(str(random.randrange(10**11, 10**12)))

            self.draw_datetime(font, item_font_size)
            self.draw_qr()

            appreciation = random.choice(self.appreciations)
            self.draw_object(appreciation, font, item_font_size)
            
            self.c.showPage()
            self.c.save()

            if epoch == 1:
                print(self.ground_truth)
            self.page_height = init_y_cursor - self.y_cursor + 2 * top_margin + (item_font_size + self.line_offset)




if __name__ == '__main__':
    a = youl_invoice_gen()
    a.infer()
    a.draw_invoice(height=1000)
