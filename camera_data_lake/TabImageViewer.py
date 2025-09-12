import streamlit as st
import numpy as np
import cv2

def decode_raw10(data, width, height, stride):
    # For RAW10, stride is typically width * 10 / 8 = width * 5 / 4
    effective_stride = stride if stride > 0 else width * 5 // 4

    expected_size = height * effective_stride
    if len(data) < expected_size:
        st.error(f"Incorrect data size. Expected at least {expected_size} bytes, but got {len(data)} bytes.")
        return None

    # Create a numpy array from the raw data
    raw_data = np.frombuffer(data, dtype=np.uint8)

    # Unpack the 10-bit data
    packed_data = raw_data[:expected_size].reshape(height, effective_stride)
    unpacked_data = np.zeros((height, width), dtype=np.uint16)

    for r in range(height):
        row_data = packed_data[r]
        for c in range(width // 4):
            base = c * 5
            b0, b1, b2, b3, b4 = row_data[base:base+5]

            unpacked_data[r, c*4 + 0] = b0 | ((b4 & 0x03) << 8)
            unpacked_data[r, c*4 + 1] = b1 | ((b4 & 0x0C) << 6)
            unpacked_data[r, c*4 + 2] = b2 | ((b4 & 0x30) << 4)
            unpacked_data[r, c*4 + 3] = b3 | ((b4 & 0xC0) << 2)

    # Normalize 10-bit (0-1023) to 8-bit (0-255)
    img_8bit = (unpacked_data >> 2).astype(np.uint8)
    return img_8bit

def decode_yuv(data, width, height, stride, conversion_code):
    effective_stride = stride if stride > 0 else width

    if conversion_code == cv2.COLOR_YUV2RGB_YUY2:
        # YUYV is packed, 2 bytes per pixel
        effective_stride = stride if stride > 0 else width * 2
        yuv_size = height * effective_stride
        if len(data) < yuv_size:
            st.error(f"Incorrect data size. Expected {yuv_size}, got {len(data)}")
            return None
        yuv_data = np.frombuffer(data[:yuv_size], dtype=np.uint8).reshape(height, effective_stride)
        # Ensure we only use the data corresponding to the actual width
        yuv_shaped = yuv_data[:, :width*2].reshape(height, width, 2)
        rgb = cv2.cvtColor(yuv_shaped, conversion_code)
    else: # Planar/Semi-planar formats (NV12, NV21, I420)
        yuv_size = int(effective_stride * height * 3 / 2)
        if len(data) < yuv_size:
            st.error(f"Incorrect data size. Expected {yuv_size}, got {len(data)}")
            return None
        yuv_data = np.frombuffer(data[:yuv_size], dtype=np.uint8).reshape((height * 3 // 2, effective_stride))
        # Crop to actual width before conversion
        yuv_cropped = yuv_data[:, :width]
        rgb = cv2.cvtColor(yuv_cropped, conversion_code)
    return rgb

def decode_nv12(data, width, height, stride):
    return decode_yuv(data, width, height, stride, cv2.COLOR_YUV2RGB_NV12)

def decode_nv21(data, width, height, stride):
    return decode_yuv(data, width, height, stride, cv2.COLOR_YUV2RGB_NV21)

def decode_i420(data, width, height, stride):
    return decode_yuv(data, width, height, stride, cv2.COLOR_YUV2RGB_I420)

def decode_yuyv(data, width, height, stride):
    # For YUYV, OpenCV uses the YUY2 code
    return decode_yuv(data, width, height, stride, cv2.COLOR_YUV2RGB_YUY2)

def decode_yuv422_sp(data, width, height, stride, conversion_code):
    effective_stride = stride if stride > 0 else width
    yuv_size = effective_stride * height * 2 # Y plane (h*w) + UV plane (h*w)
    if len(data) < yuv_size:
        st.error(f"Incorrect data size. Expected {yuv_size}, got {len(data)}")
        return None

    # For YUV422 semi-planar, the shape is Y plane on top of UV plane
    yuv_data = np.frombuffer(data[:yuv_size], dtype=np.uint8).reshape((height * 2, effective_stride))
    yuv_cropped = yuv_data[:, :width]
    rgb = cv2.cvtColor(yuv_cropped, conversion_code)
    return rgb

def decode_nv16(data, width, height, stride):
    return decode_yuv422_sp(data, width, height, stride, cv2.COLOR_YUV2RGB_NV16)

def decode_nv61(data, width, height, stride):
    return decode_yuv422_sp(data, width, height, stride, cv2.COLOR_YUV2RGB_NV61)

def decode_yuv444(data, width, height, stride):
    effective_stride = stride if stride > 0 else width
    yuv_size = effective_stride * height * 3
    if len(data) < yuv_size:
        st.error(f"Incorrect data size for YUV444. Expected {yuv_size}, got {len(data)}")
        return None
    yuv_data = np.frombuffer(data[:yuv_size], dtype=np.uint8).reshape((height * 3, effective_stride))
    # Crop to actual width before conversion
    yuv_cropped = yuv_data[:, :width]
    rgb = cv2.cvtColor(yuv_cropped, cv2.COLOR_YUV2RGB_I444)
    return rgb

# Dictionary to map format strings to decoding functions
DECODING_FUNCTIONS = {
    "RAW10": decode_raw10,
    "NV12": decode_nv12,
    "NV21": decode_nv21,
    "NV16": decode_nv16,
    "NV61": decode_nv61,
    "I420": decode_i420,
    "YUYV": decode_yuyv,
    "YUV444": decode_yuv444,
}

class TabImageViewer:
    def render(self):
        st.header("Image Viewer")

        uploaded_file = st.file_uploader("Choose an image file", type=None)

        # Sidebar for controls
        st.sidebar.header("Image Properties")
        image_format = st.sidebar.selectbox(
            "Select Image Format",
            list(DECODING_FUNCTIONS.keys())
        )
        width = st.sidebar.number_input("Width", min_value=1, value=1920)
        height = st.sidebar.number_input("Height", min_value=1, value=1080)
        stride = st.sidebar.number_input("Stride", min_value=0, value=0, help="Set to 0 to use width as stride.")

        display_button = st.sidebar.button("Display Image")

        if display_button and uploaded_file is not None:
            file_data = uploaded_file.getvalue()

            decoder_func = DECODING_FUNCTIONS.get(image_format)

            if decoder_func:
                with st.spinner(f"Decoding {image_format} image..."):
                    image_to_display = decoder_func(file_data, width, height, stride)
                    if image_to_display is not None:
                        st.image(image_to_display, caption=f"Decoded Image ({image_format})", use_column_width=True)
            else:
                st.error(f"No decoder available for format: {image_format}")
