# -*- coding: utf-8 -*-
"""Генерирует 2 тестовых PDF: цифровой (с текстовым слоем) и скан (картинка)."""
import os
import fitz
from PIL import Image, ImageDraw, ImageFont

base = os.path.dirname(os.path.abspath(__file__))
in_dir = os.path.join(base, "input")
os.makedirs(in_dir, exist_ok=True)

FONT = r"C:\Windows\Fonts\arial.ttf"

# --- 1. Цифровой PDF (текстовый слой + таблица), кириллический шрифт ---
doc = fitz.open()
page = doc.new_page()
page.insert_text((72, 72), "Заключение эксперта № 123/2025",
                 fontsize=14, fontfile=FONT, fontname="ar")
page.insert_text((72, 110),
                 "Анализ финансового состояния ООО «Ромашка» за 2024 год.",
                 fontsize=11, fontfile=FONT, fontname="ar")
# простая таблица
rows = [["Показатель", "2023", "2024"],
        ["Выручка, тыс. руб.", "15000", "18500"],
        ["Чистая прибыль", "1200", "2100"],
        ["Активы", "42000", "47800"]]
x0, y0, cw, rh = 72, 150, 150, 24
for r, row in enumerate(rows):
    for c, val in enumerate(row):
        rect = fitz.Rect(x0 + c*cw, y0 + r*rh, x0 + (c+1)*cw, y0 + (r+1)*rh)
        page.draw_rect(rect, color=(0, 0, 0), width=0.5)
        page.insert_text((rect.x0 + 4, rect.y0 + 16), val,
                         fontsize=10, fontfile=FONT, fontname="ar")
doc.save(os.path.join(in_dir, "tsifrovoy_test.pdf"))
doc.close()

# --- 2. Скан-PDF (картинка без текстового слоя) ---
W, H = 1654, 2339  # ~A4 @200dpi
img = Image.new("RGB", (W, H), "white")
d = ImageDraw.Draw(img)
f_big = ImageFont.truetype(FONT, 42)
f = ImageFont.truetype(FONT, 32)
d.text((120, 120), "Заключение эксперта № 456/2025", font=f_big, fill="black")
d.text((120, 220), "Расчёт размера убытков по делу А40-99999/2025.", font=f, fill="black")
# таблица-сетка
tbl = [["Период", "Сумма, руб.", "Примечание"],
       ["I квартал", "350 000", "по договору"],
       ["II квартал", "420 000", "с учётом пени"],
       ["III квартал", "510 000", "уточнено"]]
tx, ty, tcw, trh = 120, 360, 460, 80
for r, row in enumerate(tbl):
    for c, val in enumerate(row):
        x1, y1 = tx + c*tcw, ty + r*trh
        d.rectangle([x1, y1, x1+tcw, y1+trh], outline="black", width=2)
        d.text((x1+15, y1+22), val, font=f, fill="black")
img_pdf = fitz.open()
p = img_pdf.new_page(width=W*72/200, height=H*72/200)
tmp = os.path.join(in_dir, "_scan.png")
img.save(tmp)
p.insert_image(p.rect, filename=tmp)
img_pdf.save(os.path.join(in_dir, "skan_test.pdf"))
img_pdf.close()
os.remove(tmp)

print("Созданы: tsifrovoy_test.pdf, skan_test.pdf в", in_dir)
