import qrcode
from PIL import Image, ImageDraw
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
size = st.slider("📐 Output Size (pixels)", min_value=600, max_value=1200, value=800, step=100)

if st.button("🚀 Generate QR Code") and url:
    # Create QR code with high error correction
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    qr_img = qr.make_image(fill_color=qr_color, back_color=bg_color).convert('RGB')
    qr_img = qr_img.resize((size, size), Image.LANCZOS)

    # Add logo
    if logo_file:
        logo = Image.open(logo_file)
        logo_size = size // 3
        logo = logo.resize((logo_size, logo_size), Image.LANCZOS)
        pos = ((qr_img.size[0] - logo_size) // 2, (qr_img.size[1] - logo_size) // 2)
        qr_img.paste(logo, pos, mask=logo if logo.mode == "RGBA" else None)

    # Display QR
    st.image(qr_img, caption="🔍 Scan-Ready Stylized QR Code", use_column_width=True)

    # Download option
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
