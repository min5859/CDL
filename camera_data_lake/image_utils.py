# image_utils.py
#import cairosvg
import streamlit as st

def save_svg(svg_content, file_name):
    with open(file_name, "w") as f:
        f.write(svg_content)

def convert_svg_to_png(svg_content, file_name):
    cairosvg.svg2png(bytestring=svg_content.encode('utf-8'), write_to=file_name)

def download_image(file_name, file_type="svg"):
    mime_type = "image/svg+xml" if file_type == "svg" else "image/png"
    with open(file_name, "rb") as f:
        st.download_button(
            label=f"{file_type.upper()} 이미지 다운로드",
            data=f,
            file_name=file_name,
            mime=mime_type
        )
