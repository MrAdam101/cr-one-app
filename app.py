import io, os
import streamlit as st
import qrcode
from PIL import Image, ImageDraw, ImageFont

# svgwrite is optional but enables SVG export
try:
    import svgwrite
    SVG_OK = True
except Exception:
    SVG_OK = False

# ---------- Helpers ----------
def hex_to_rgb(h):
    h = h.strip()
    if h.startswith("#"): h = h[1:]
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def rel_luminance(rgb):
    # WCAG relative luminance
    def lin(v):
        v = v/255
        return v/12.92 if v <= 0.04045 else ((v+0.055)/1.055)**2.4
    r,g,b = rgb
    return 0.2126*lin(r)+0.7152*lin(g)+0.0722*lin(b)

def contrast_ratio(rgb1, rgb2):
    L1, L2 = rel_luminance(rgb1), rel_luminance(rgb2)
    if L1 < L2: L1, L2 = L2, L1
    return (L1 + 0.05) / (L2 + 0.05)

def load_font(pref_size):
    # Try a business-friendly font if present, else fall back
    for f in ["arial.ttf", "DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]:
        try:
            return ImageFont.truetype(f, pref_size)
        except Exception:
            continue
    return ImageFont.load_default()

# ---------- UI ----------
st.set_page_config(page_title="CR One – Fiverr Style QR", layout="centered")
st.title("💼 CR One — Fiverr‑Style Professional QR Generator")

col1, col2 = st.columns(2)
with col1:
    url = st.text_input("🔗 Destination URL (required)")
    fg1_hex = st.color_picker("🎨 Dot Color A", "#4B1AA3")     # FedEx purple vibe
    fg2_hex = st.color_picker("🟧 Dot Color B", "#F77618")     # FedEx orange vibe
    bg_hex  = st.color_picker("⬜ Background", "#FFFFFF")
with col2:
    logo_file = st.file_uploader("🖼 Center Logo (PNG/JPG)", type=["png","jpg","jpeg"])
    size_px = st.slider("📐 QR Pixel Size", 700, 1400, 1000, 100)
    quiet_zone = st.slider("▫️ Quiet Zone (modules)", 4, 8, 4)

two_tone = st.checkbox("Enable two‑tone pattern (A/B alternating rows)", True)

st.subheader("Banners")
top_text = st.text_input("Top banner text (optional)", "Ship With Us")
top_bg   = st.color_picker("Top banner color", "#5C2D91")
top_text_color = st.color_picker("Top text color", "#FFFFFF")

bottom_text = st.text_input("Bottom banner text (optional)", "Scan to visit our site")
bottom_bg   = st.color_picker("Bottom banner color", "#5C2D91")
bottom_text_color = st.color_picker("Bottom text color", "#FFFFFF")

cta_font_size = st.slider("Banner font size", 28, 64, 44, 2)

if st.button("🚀 Generate"):
    if not url:
        st.warning("Please enter a destination URL.")
        st.stop()

    fg1, fg2, bg = hex_to_rgb(fg1_hex), hex_to_rgb(fg2_hex), hex_to_rgb(bg_hex)

    # Contrast safety check (vs background)
    cr1 = contrast_ratio(fg1, bg)
    cr2 = contrast_ratio(fg2, bg)
    if cr1 < 3 or (two_tone and cr2 < 3):
        st.warning("⚠️ Low contrast detected. Consider darker dots or a lighter background for reliable scanning.")

    # Build QR with high error correction & quiet zone
    qr = qrcode.QRCode(
        version=None,                      # automatic
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=1,                        # we draw manually
        border=quiet_zone
    )
    qr.add_data(url)
    qr.make(fit=True)
    matrix = qr.get_matrix()              # boolean grid including border

    modules = len(matrix)
    module_px = size_px // modules
    qr_w = modules * module_px

    # Draw QR manually to control colors
    qr_img = Image.new("RGB", (qr_w, qr_w), bg)
    draw = ImageDraw.Draw(qr_img)

    # Two-tone pattern per row (keeps finders scannable too)
    for y, row in enumerate(matrix):
        # choose color for this row
        row_color = fg1 if (not two_tone or y % 2 == 0) else fg2
        for x, v in enumerate(row):
            if v:
                x0, y0 = x*module_px, y*module_px
                x1, y1 = x0+module_px, y0+module_px
                draw.rectangle([x0, y0, x1, y1], fill=row_color)

    # Reinforce finder patterns (7x7) as dark for reliability
    finder_coords = [(0,0), (modules-7,0), (0,modules-7)]
    for fx, fy in finder_coords:
        draw.rectangle([fx*module_px, fy*module_px, (fx+7)*module_px, (fy+7)*module_px], fill=(0,0,0))
        # inner white 5x5
        draw.rectangle([(fx+1)*module_px, (fy+1)*module_px, (fx+6)*module_px, (fy+6)*module_px], fill=bg)
        # inner dark 3x3
        draw.rectangle([(fx+2)*module_px, (fy+2)*module_px, (fx+5)*module_px, (fy+5)*module_px], fill=(0,0,0))

    # Center logo in circular background matching page bg
    if logo_file:
        logo = Image.open(logo_file).convert("RGBA")
        # Keep logo area ≤ ~22% of QR width for scannability
        logo_d = int(qr_w * 0.22)
        logo = logo.resize((logo_d, logo_d), Image.LANCZOS)

        circle = Image.new("RGBA", (logo_d, logo_d), (*bg, 255))
        mask = Image.new("L", (logo_d, logo_d), 0)
        ImageDraw.Draw(mask).ellipse((0,0,logo_d,logo_d), fill=255)
        circle.paste(logo, (0,0), logo)
        cx = (qr_w - logo_d)//2
        cy = (qr_w - logo_d)//2
        qr_img.paste(circle, (cx, cy), circle)

    # Build bannered canvas
    top_h    = 0 if not top_text else int(qr_w * 0.20)
    bottom_h = 0 if not bottom_text else int(qr_w * 0.22)
    canvas = Image.new("RGB", (qr_w, qr_w + top_h + bottom_h), bg)
    y = 0
    if top_h:
        ImageDraw.Draw(canvas).rectangle([0, 0, qr_w, top_h], fill=hex_to_rgb(top_bg))
        font = load_font(cta_font_size)
        draw_top = ImageDraw.Draw(canvas)
        tw = draw_top.textlength(top_text, font=font)
        draw_top.text(((qr_w - tw)//2, (top_h - cta_font_size)//2), top_text,
                      fill=hex_to_rgb(top_text_color), font=font)
        y = top_h
    canvas.paste(qr_img, (0, y))
    if bottom_h:
        by0 = y + qr_w
        ImageDraw.Draw(canvas).rectangle([0, by0, qr_w, by0 + bottom_h], fill=hex_to_rgb(bottom_bg))
        font = load_font(cta_font_size)
        draw_bot = ImageDraw.Draw(canvas)
        tw = draw_bot.textlength(bottom_text, font=font)
        draw_bot.text(((qr_w - tw)//2, by0 + (bottom_h - cta_font_size)//2),
                      bottom_text, fill=hex_to_rgb(bottom_text_color), font=font)

    # Show preview
    st.image(canvas, caption="Scannable, print‑ready preview", use_container_width=True)

    # PNG download
    png_buf = io.BytesIO()
    canvas.save(png_buf, format="PNG")
    st.download_button("⬇️ Download PNG", png_buf.getvalue(), file_name="qr_premium.png", mime="image/png")

    # SVG download (QR only, no bitmap logo/banners)
    if SVG_OK:
        dw = svgwrite.Drawing(size=(qr_w, qr_w))
        dw.add(dw.rect(insert=(0,0), size=(qr_w, qr_w), fill=bg_hex))
        for y, row in enumerate(matrix):
            row_color = fg1_hex if (not two_tone or y % 2 == 0) else fg2_hex
            for x, v in enumerate(row):
                if v:
                    dw.add(dw.rect(insert=(x*module_px, y*module_px),
                                   size=(module_px, module_px), fill=row_color))
        # Reinforce finders in SVG
        for fx, fy in [(0,0), (modules-7,0), (0,modules-7)]:
            dw.add(dw.rect(insert=(fx*module_px, fy*module_px), size=(7*module_px, 7*module_px), fill="#000000"))
            dw.add(dw.rect(insert=((fx+1)*module_px, (fy+1)*module_px), size=(5*module_px, 5*module_px), fill=bg_hex))
            dw.add(dw.rect(insert=((fx+2)*module_px, (fy+2)*module_px), size=(3*module_px, 3*module_px), fill="#000000"))
        st.download_button("⬇️ Download SVG (vector, QR only)",
                           data=dw.tostring().encode("utf-8"),
                           file_name="qr_premium.svg", mime="image/svg+xml")
    else:
        st.caption("Install 'svgwrite' to enable SVG export.")


