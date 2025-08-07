import qrcode
from PIL import Image, ImageDraw, ImageFont
import streamlit as st
import io

st.set_page_config(page_title="CR One App | Premium QR Generator", layout="centered")
st.title("✨ CR One App | Premium QR Code Generator")

st.markdown("Generate premium QR codes with a drag-and-drop logo and stylized visuals like professional Fiverr examples.")

# Input fields
url = st.text_input("🔗 Enter the destination URL")
logo_file = st.file_uploader("🖼️ Drag & Drop Your Logo (PNG preferred)", type=["png", "jpg", "jpeg"])
qr_color = st.color_picker("🎨 QR Code Dot Color", value="#000000")
bg_color = st.color_picker("🌈 Background Color", value="#FFFFFF")
shape_option = st.selectbox("🔲 QR Dot Shape", ["square", "rounded"])
gradient = st.checkbox("🌈 Enable Gradient Fill (Dot Color to Background Color)")
add_text = st.text_input("✏️ Optional Text Below QR (Brand/CTA)")
size = st.slider("📐 Output Size (pixels)", min_value=600, max_value=1200, value=800, step=100)

if st.button("🚀 Generate QR Code") and url:
    # Create base QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    # Basic QR image first
    qr_img = qr.make_image(fill_color=qr_color, back_color=bg_color).convert('RGB')
    qr_img = qr_img.resize((size, size), Image.LANCZOS)

    # Apply rounded dot mask (simulate)
    if shape_option == "rounded":
        pixels = qr_img.load()
        for y in range(qr_img.size[1]):
            for x in range(qr_img.size[0]):
                if pixels[x, y] == Image.new("RGB", (1, 1), qr_color).getpixel((0, 0)):
                    pixels[x, y] = tuple(map(lambda v: int(v * 0.9), pixels[x, y]))

    # Optional gradient overlay
    if gradient:
        grad = Image.new("RGB", (size, size), bg_color)
        for y in range(size):
            r = int(int(qr_color[1:3], 16) * (1 - y / size) + int(bg_color[1:3], 16) * (y / size))
            g = int(int(qr_color[3:5], 16) * (1 - y / size) + int(bg_color[3:5], 16) * (y / size))
            b = int(int(qr_color[5:7], 16) * (1 - y / size) + int(bg_color[5:7], 16) * (y / size))
            for x in range(size):
                if qr_img.getpixel((x, y)) == Image.new("RGB", (1, 1), qr_color).getpixel((0, 0)):
                    qr_img.putpixel((x, y), (r, g, b))

    # Add logo with background-matching circle background
    if logo_file:
        logo = Image.open(logo_file).convert("RGBA")
        logo_size = size // 4
        logo = logo.resize((logo_size, logo_size), Image.LANCZOS)

        bg_rgb = Image.new("RGB", (1, 1), bg_color).getpixel((0, 0))
        circle_bg = Image.new("RGBA", (logo_size, logo_size), (255, 255, 255, 0))
        draw = ImageDraw.Draw(circle_bg)
        draw.ellipse((0, 0, logo_size, logo_size), fill=bg_rgb + (255,))

        mask = Image.new("L", (logo_size, logo_size), 0)
        draw_mask = ImageDraw.Draw(mask)
        draw_mask.ellipse((0, 0, logo_size, logo_size), fill=255)

        circle_bg.paste(logo, (0, 0), mask=logo.split()[3])
        pos = ((qr_img.size[0] - logo_size) // 2, (qr_img.size[1] - logo_size) // 2)
        qr_img.paste(circle_bg, pos, circle_bg)

    # Add text below QR
    if add_text:
        try:
            font = ImageFont.truetype("arial.ttf", 36)
        except:
            font = ImageFont.load_default()
        text_height = 60
        new_img = Image.new("RGB", (qr_img.width, qr_img.height + text_height + 20), bg_color)
        new_img.paste(qr_img, (0, 0))
        draw = ImageDraw.Draw(new_img)
        text_width = draw.textlength(add_text, font=font)
        draw.text(((qr_img.width - text_width) // 2, qr_img.height + 10), add_text, fill=qr_color, font=font)
        qr_img = new_img

    # Show image
    st.image(qr_img, caption="🔍 Scan-Ready Stylized QR Code", use_column_width=True)

    buf = io.BytesIO()
    qr_img.save(buf, format="PNG")
    st.download_button(
        label="📅 Download Your QR Code",
        data=buf.getvalue(),
        file_name="fiverr_style_qr.png",
        mime="image/png"
    )
else:
    st.info("👆 Add a URL and drag in your logo to generate a branded, scannable QR code.")
