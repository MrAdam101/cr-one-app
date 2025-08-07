import streamlit as st
import qrcode
from PIL import Image
from io import BytesIO

# Streamlit page config
st.set_page_config(page_title="CR One App ? QR Code Generator", layout="centered")

# App title and description
st.title("?? CR One App ? Custom QR Code Generator")
st.markdown("Create branded QR codes with your link, logo, and style ? ready in seconds.")

# Input fields
url = st.text_input("?? Enter the destination URL")

logo_file = st.file_uploader("??? Drag and drop your logo image (PNG, JPG)", type=["png", "jpg", "jpeg"])

fill_color = st.color_picker("?? Choose QR code color", "#000000")
back_color = st.color_picker("?? Choose background color", "#ffffff")

email = st.text_input("?? Optional: Enter email to receive future updates")

# Generate QR code
if url and logo_file:
    # QR setup
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    # Generate base QR image
    qr_img = qr.make_image(fill_color=fill_color, back_color=back_color).convert("RGB")

    # Load and resize logo
    logo = Image.open(logo_file)
    box_size = 60
    logo = logo.resize((box_size, box_size))

    # Center the logo
    qr_width, qr_height = qr_img.size
    pos = ((qr_width - box_size) // 2, (qr_height - box_size) // 2)
    qr_img.paste(logo, pos, mask=logo if logo.mode == "RGBA" else None)

    # Display the QR image
    st.image(qr_img, caption="?? Your Branded QR Code", use_column_width=True)

    # Prepare for download
    buffer = BytesIO()
    qr_img.save(buffer, format="PNG")

    # Download button
    st.download_button(
        label="?? Download QR Code",
        data=buffer.getvalue(),
        file_name="qr_code.png",
        mime="image/png"
    )

    st.caption("? Powered by CR One App ? Customize. Create. Connect.")

elif url and not logo_file:
    st.warning("?? Please upload a logo image.")
elif logo_file and not url:
    st.warning("?? Please enter a destination URL.")
