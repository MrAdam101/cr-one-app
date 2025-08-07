import qrcode
from PIL import Image, ImageDraw, ImageFont
import streamlit as st
import io
import svgwrite

st.set_page_config(page_title="CR One App | Premium QR Generator", layout="centered")
st.title("✨ CR One App | Premium QR Code Generator")

st.markdown("Professional QR codes with SVG export and business‑card mockups included.")

# Inputs
url = st.text_input("🔗 Destination URL")
logo_file = st.file_uploader("🖼 Logo (PNG preferred)", type=["png", "jpg", "jpeg"])
qr_color = st.color_picker("🎨 QR Dot Color", value="#000000")
bg_color = st.color_picker("🌈 Background Color", value="#FFFFFF")
gradient = st.checkbox("🌈 Gradient from dot to background")
add_text = st.text_input("✏️ CTA Text (e.g. \"Scan Me\")")
size = st.slider("📐 QR Size (px)", 600, 1200, 800, 100)

if st.button("Generate QR Code") and url:
    # Create QR
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H)
    qr.add_data(url); qr.make(fit=True)
    qr_img = qr.make_image(fill_color=qr_color, back_color=bg_color).convert("RGB")
    qr_img = qr_img.resize((size, size), Image.LANCZOS)

    # Gradient overlay
    if gradient:
        for y in range(size):
            frac = y/size
            r = int(int(qr_color[1:3], 16)*(1-frac) + int(bg_color[1:3], 16)*frac)
            g = int(int(qr_color[3:5], 16)*(1-frac) + int(bg_color[3:5], 16)*frac)
            b = int(int(qr_color[5:7], 16)*(1-frac) + int(bg_color[5:7], 16)*frac)
            for x in range(size):
                if qr_img.getpixel((x,y)) == tuple(int(qr_color[i:i+2],16) for i in (1,3,5)):
                    qr_img.putpixel((x,y),(r,g,b))

    # Logo (white circle background)
    if logo_file:
        logo = Image.open(logo_file).convert("RGBA")
        logo_size = size // 4
        logo = logo.resize((logo_size, logo_size), Image.LANCZOS)
        bg_rgb = Image.new("RGB",(1,1),bg_color).getpixel((0,0))
        circle = Image.new("RGBA",(logo_size,logo_size),bg_rgb+(255,))
        mask = Image.new("L",(logo_size,logo_size),0)
        ImageDraw.Draw(mask).ellipse((0,0,logo_size,logo_size),fill=255)
        circle.paste(logo,(0,0),logo)
        pos = ((size-logo_size)//2,(size-logo_size)//2)
        qr_img.paste(circle,pos,circle)

    # CTA Text
    if add_text:
        try:
            font = ImageFont.truetype("arial.ttf", 44)
        except:
            font = ImageFont.load_default()
        pad = 80
        new_h = size + pad
        canvas = Image.new("RGB",(size,new_h),bg_color)
        canvas.paste(qr_img,(0,0))
        draw = ImageDraw.Draw(canvas)
        tw = draw.textlength(add_text,font=font)
        draw.text(((size-tw)//2, size+10), add_text, fill=qr_color, font=font)
        qr_img = canvas

    # Draw border/frame
    border = Image.new("RGB",(size+20, size+20+(80 if add_text else 0)), bg_color)
    border.paste(qr_img,(10,10))
    final_img = border

    st.image(final_img, caption="✅ Business‑Card Preview", use_column_width=True)

    # PNG download
    buf = io.BytesIO()
    final_img.save(buf,format="PNG")
    st.download_button("Download PNG", buf.getvalue(), "qr_business.png", "image/png")

    # SVG export
    w = svgwrite.Drawing(size=(size, size))
    w.add(w.rect(insert=(0,0), size=(size,size), fill=bg_color))
    matrix = qr.get_matrix()
    fill = qr_color
    for y, row in enumerate(matrix):
        for x, v in enumerate(row):
            if v:
                w.add(w.rect(insert=(x*10, y*10), size=(10,10), fill=fill))
    svg_bytes = w.tostring().encode("utf-8")
    st.download_button("Download SVG", svg_bytes, "qr_code.svg", "image/svg+xml")
else:
    st.info("❗ Enter a URL to customize output")
