import qrcode
from PIL import Image, ImageDraw, ImageOps
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

    qr_img = qr.make_image(fill_color=qr_color, back_color=bg_color).convert("RGBA")
    qr_img = qr_img.resize((size, size), Image.LANCZOS)

    # Add logo in center
    if logo_file:
        logo = Image.open(logo_file).convert("RGBA")
        logo_size = size // 4  # Smaller for scan safety
        logo = logo.resize((logo_size, logo_size), Image.LANCZOS)

        # Optional: Add circle mask for rounded logo effect
        mask = Image.new("L", (logo_size, logo_size), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, logo_size, logo_size), fill=255)
        logo.putalpha(mask)

        # Paste logo
        pos = ((qr_img.size[0] - logo_size) // 2, (qr_img.size[1] - logo_size) // 2)
        qr_img.paste(logo, pos, logo)

    # Show QR
    st.image(qr_img, caption="🔍 Scan-Ready Premium QR Code", use_column_width=True)

    # Download
    buf = io.BytesIO()
    qr_img.save(buf, format="PNG")
    st.download_button(
        label="📥 Download QR Code",
        data=buf.getvalue(),
        file_name="premium_qr.png",
        mime="image/png"
    )
else:
    st.info("👆 Enter a URL and add a logo to generate your branded QR code.")
