import streamlit as st
import qrcode
from PIL import Image
import io

st.set_page_config(page_title="CR One App", layout="centered")

st.title("✨ CR One App ✨ Custom QR Code Generator")
st.markdown("Create branded QR codes with your link, logo, and style – ready in seconds.")

# Get destination URL
url = st.text_input("🔗 Enter the destination URL")

# Upload logo image
logo_image = st.file_uploader("📌 Drag and drop your logo image (PNG, JPG)", type=["png", "jpg", "jpeg"])

# QR code color
qr_color = st.color_picker("🎨 Choose QR code color", "#000000")

# Background color
bg_color = st.color_picker("🌈 Choose background color", "#FFFFFF")

# Optional email
email = st.text_input("✉️ Optional: Enter email to receive future updates (not required)")

# Generate QR button
if st.button("🚀 Generate QR Code") and url:
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    # Create QR image
    qr_image = qr.make_image(fill_color=qr_color, back_color=bg_color).convert("RGB")

    # Resize the QR image to 600x600
    qr_image = qr_image.resize((600, 600))

    # If logo is uploaded
    if logo_image is not None:
        logo = Image.open(logo_image)

        # Resize logo
        logo_size = 100
        logo = logo.resize((logo_size, logo_size))

        # Get position to paste logo
        qr_width, qr_height = qr_image.size
        pos = ((qr_width - logo_size) // 2, (qr_height - logo_size) // 2)

        qr_image.paste(logo, pos, mask=logo if logo.mode == 'RGBA' else None)

    # Display the image
    st.image(qr_image, use_container_width=True, caption="🔍 Your Branded QR Code")

    # Allow download
    buf = io.BytesIO()
    qr_image.save(buf, format="PNG")
    byte_im = buf.getvalue()

    st.download_button(
        label="📥 Download QR Code",
        data=byte_im,
        file_name="cr-one-qr.png",
        mime="image/png"
    )
