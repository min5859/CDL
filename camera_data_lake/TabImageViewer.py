import streamlit as st
import numpy as np
import cv2

def decode_raw10_packed(data, width, height, stride):
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

def decode_raw10_unpacked(data, width, height, stride):
    """
    Decodes RAW10 unpacked data (10-bit data in 16-bit words).
    """
    # For unpacked RAW10, each pixel is 2 bytes.
    effective_stride = stride if stride > 0 else width * 2

    expected_size = height * effective_stride
    if len(data) < expected_size:
        st.error(f"Incorrect data size for RAW10 Unpacked. Expected at least {expected_size} bytes, but got {len(data)} bytes.")
        return None

    # Create a numpy array from the raw data, interpreting it as uint16
    raw_16bit = np.frombuffer(data, dtype=np.uint16)

    # Reshape and crop if necessary
    stride_in_pixels = effective_stride // 2
    expected_elements = height * stride_in_pixels

    if len(raw_16bit) < expected_elements:
        st.error(f"Cannot reshape array for RAW10 Unpacked. Not enough data elements for specified dimensions.")
        return None

    raw_16bit = raw_16bit[:expected_elements].reshape(height, stride_in_pixels)

    # Crop to actual width if stride is larger
    if stride_in_pixels > width:
        raw_16bit = raw_16bit[:, :width]

    # The data is 10-bit, stored in the lower bits of uint16.
    # To normalize 10-bit (0-1023) to 8-bit (0-255), right-shift by 2.
    img_8bit = (raw_16bit >> 2).astype(np.uint8)

    return img_8bit

def decode_raw12_packed(data, width, height, stride):
    """
    Decodes RAW12 packed data.
    In this format, 2 pixels (12-bit each) are packed into 3 bytes.
    """
    # For RAW12 packed, stride is typically width * 12 / 8 = width * 3 / 2
    effective_stride = stride if stride > 0 else width * 3 // 2

    expected_size = height * effective_stride
    if len(data) < expected_size:
        st.error(f"Incorrect data size for RAW12. Expected at least {expected_size} bytes, but got {len(data)} bytes.")
        return None

    # Create a numpy array from the raw data
    raw_data = np.frombuffer(data, dtype=np.uint8)

    # Unpack the 12-bit data
    packed_data = raw_data[:expected_size].reshape(height, effective_stride)
    unpacked_data = np.zeros((height, width), dtype=np.uint16)

    for r in range(height):
        row_data = packed_data[r]
        # Process 2 pixels (3 bytes) at a time
        for c in range(width // 2):
            base = c * 3
            b0, b1, b2 = row_data[base:base+3]

            # Unpack 2 pixels from 3 bytes
            # A common packing is:
            # Byte 0: P1[7:0]
            # Byte 1: P2[7:0]
            # Byte 2: P2[11:8] (upper nibble), P1[11:8] (lower nibble)
            # So, B2 = (P2_msb << 4) | P1_msb
            # P1 = B0 | ( (B2 & 0x0F) << 8 )
            # P2 = B1 | ( (B2 & 0xF0) << 4 )
            unpacked_data[r, c*2 + 0] = b0 | ((b2 & 0x0F) << 8)
            unpacked_data[r, c*2 + 1] = b1 | ((b2 & 0xF0) << 4)

    # Normalize 12-bit (0-4095) to 8-bit (0-255) by right-shifting by 4
    img_8bit = (unpacked_data >> 4).astype(np.uint8)
    return img_8bit

def decode_raw12_unpacked(data, width, height, stride):
    """
    Decodes RAW12 unpacked data (12-bit data in 16-bit words).
    """
    # For unpacked RAW12, each pixel is 2 bytes.
    effective_stride = stride if stride > 0 else width * 2

    expected_size = height * effective_stride
    if len(data) < expected_size:
        st.error(f"Incorrect data size for RAW12 Unpacked. Expected at least {expected_size} bytes, but got {len(data)} bytes.")
        return None

    # Create a numpy array from the raw data, interpreting it as uint16
    raw_16bit = np.frombuffer(data, dtype=np.uint16)

    # Reshape and crop if necessary
    stride_in_pixels = effective_stride // 2
    expected_elements = height * stride_in_pixels

    if len(raw_16bit) < expected_elements:
        st.error(f"Cannot reshape array for RAW12 Unpacked. Not enough data elements for specified dimensions.")
        return None

    raw_16bit = raw_16bit[:expected_elements].reshape(height, stride_in_pixels)

    # Crop to actual width if stride is larger
    if stride_in_pixels > width:
        raw_16bit = raw_16bit[:, :width]

    # The data is 12-bit, stored in the lower bits of uint16.
    # To normalize 12-bit (0-4095) to 8-bit (0-255), right-shift by 4.
    img_8bit = (raw_16bit >> 4).astype(np.uint8)

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

# --- YUV420 (2-Plane) ---
def decode_nv12(data, width, height, stride):
    return decode_yuv(data, width, height, stride, cv2.COLOR_YUV2RGB_NV12)

def decode_nv21(data, width, height, stride):
    return decode_yuv(data, width, height, stride, cv2.COLOR_YUV2RGB_NV21)

def decode_p010(data, width, height, stride):
    """
    Decodes P010 format (10-bit YUV 4:2:0 semi-planar).
    The 10-bit samples are stored in 16-bit words (low-endian).
    This function converts the P010 data to 8-bit NV12-like data and then uses
    the existing NV12 to RGB conversion.
    """
    effective_stride = stride if stride > 0 else width

    # P010 is 10-bit data in 16-bit words, so 2 bytes per component.
    # Y plane size: height * effective_stride * 2 bytes
    # UV plane size: (height / 2) * effective_stride * 2 bytes
    # Total size: 1.5 * height * effective_stride * 2 bytes
    expected_size = int(height * 3 / 2 * effective_stride * 2)

    if len(data) < expected_size:
        st.error(f"Incorrect data size for P010. Expected at least {expected_size} bytes, but got {len(data)} bytes.")
        return None

    # Create a numpy array from the raw data, interpreting it as uint16
    # The data is little-endian by default which is what P010 usually is.
    yuv_16bit = np.frombuffer(data[:expected_size], dtype=np.uint16)

    # Reshape to semi-planar format
    yuv_16bit = yuv_16bit.reshape((height * 3 // 2, effective_stride))

    # Crop to actual width if stride is larger
    if effective_stride > width:
        yuv_16bit = yuv_16bit[:, :width]

    # Convert 10-bit data (in 16-bit words) to 8-bit data by right-shifting by 2.
    # This creates an 8-bit NV12-like image.
    yuv_8bit = (yuv_16bit >> 2).astype(np.uint8)

    # Use OpenCV to convert from NV12 (which is what yuv_8bit now is) to RGB
    rgb = cv2.cvtColor(yuv_8bit, cv2.COLOR_YUV2RGB_NV12)

    return rgb

def decode_p012(data, width, height, stride):
    """
    Decodes P012 format (12-bit YUV 4:2:0 semi-planar).
    The 12-bit samples are stored in 16-bit words (low-endian).
    This function converts the P012 data to 8-bit NV12-like data and then uses
    the existing NV12 to RGB conversion.
    """
    effective_stride = stride if stride > 0 else width

    # P012 is 12-bit data in 16-bit words, so 2 bytes per component.
    # Total size is calculated the same way as P010.
    expected_size = int(height * 3 / 2 * effective_stride * 2)

    if len(data) < expected_size:
        st.error(f"Incorrect data size for P012. Expected at least {expected_size} bytes, but got {len(data)} bytes.")
        return None

    # Create a numpy array from the raw data, interpreting it as uint16
    yuv_16bit = np.frombuffer(data[:expected_size], dtype=np.uint16)

    # Reshape to semi-planar format
    yuv_16bit = yuv_16bit.reshape((height * 3 // 2, effective_stride))

    # Crop to actual width if stride is larger
    if effective_stride > width:
        yuv_16bit = yuv_16bit[:, :width]

    # Convert 12-bit data (in 16-bit words) to 8-bit data by right-shifting by 4.
    # This creates an 8-bit NV12-like image.
    yuv_8bit = (yuv_16bit >> 4).astype(np.uint8)

    # Use OpenCV to convert from NV12 (which is what yuv_8bit now is) to RGB
    rgb = cv2.cvtColor(yuv_8bit, cv2.COLOR_YUV2RGB_NV12)

    return rgb

# --- YUV420 (3-Plane) ---
def decode_i420(data, width, height, stride):
    return decode_yuv(data, width, height, stride, cv2.COLOR_YUV2RGB_I420)

def decode_yv12(data, width, height, stride):
    # YV12 is YUV420 Planar, with V plane before U plane.
    # The memory layout is compatible with what decode_yuv expects for 420 formats.
    return decode_yuv(data, width, height, stride, cv2.COLOR_YUV2RGB_YV12)

# --- YUV422 (1-Plane) ---
def decode_yuyv(data, width, height, stride):
    # For YUYV, OpenCV uses the YUY2 code
    return decode_yuv(data, width, height, stride, cv2.COLOR_YUV2RGB_YUY2)

# --- YUV422 (2-Plane) ---
def decode_nv16(data, width, height, stride):
    return decode_yuv422_sp(data, width, height, stride, cv2.COLOR_YUV2RGB_NV16)

def decode_nv61(data, width, height, stride):
    return decode_yuv422_sp(data, width, height, stride, cv2.COLOR_YUV2RGB_NV61)

def decode_nv20(data, width, height, stride):
    """
    Decodes NV20 format (10-bit YUV 4:2:2 semi-planar).
    This function adapts the P010/P012 logic (10-bit data in 16-bit words)
    to the NV16 (4:2:2) memory layout.
    """
    effective_stride = stride if stride > 0 else width

    # NV16 (8-bit 4:2:2) has a shape of (height*2, stride).
    # NV20 is the 10-bit version, so samples are 16-bit words.
    # Total size = height * stride * 2 (for Y+UV planes) * 2 (bytes per sample)
    expected_size = int(height * 2 * effective_stride * 2)

    if len(data) < expected_size:
        st.error(f"Incorrect data size for NV20. Expected at least {expected_size}, got {len(data)} bytes.")
        return None

    # Create a numpy array from the raw data, interpreting it as uint16
    yuv_16bit = np.frombuffer(data[:expected_size], dtype=np.uint16)
    yuv_16bit = yuv_16bit.reshape((height * 2, effective_stride))

    # Crop to actual width if stride is larger
    if effective_stride > width:
        yuv_16bit = yuv_16bit[:, :width]

    # Convert 10-bit data (in 16-bit words) to 8-bit data by right-shifting by 2.
    yuv_8bit = (yuv_16bit >> 2).astype(np.uint8)

    # Now we have an 8-bit NV16-like buffer, which can be converted to RGB.
    rgb = cv2.cvtColor(yuv_8bit, cv2.COLOR_YUV2RGB_NV16)
    return rgb

# --- YUV444 (2-Plane) ---
def decode_nv24(data, width, height, stride):
    """
    Decodes NV24 format (8-bit YUV 4:4:4 semi-planar, Y-plane followed by interleaved UV plane).
    This is done by de-interleaving the UV plane and using the I444 (planar) converter.
    """
    effective_stride = stride if stride > 0 else width
    y_size = effective_stride * height
    uv_size = effective_stride * height * 2 # Full-size U and V planes, interleaved
    expected_size = y_size + uv_size

    if len(data) < expected_size:
        st.error(f"Incorrect data size for NV24. Expected at least {expected_size}, got {len(data)} bytes.")
        return None

    yuv_data = np.frombuffer(data[:expected_size], dtype=np.uint8)

    y_plane = yuv_data[:y_size].reshape(height, effective_stride)
    uv_plane = yuv_data[y_size:].reshape(height, effective_stride * 2)

    # Crop to actual width if stride is larger
    if effective_stride > width:
        y_plane = y_plane[:, :width]
        uv_plane = uv_plane[:, :width*2]

    # De-interleave UV plane
    u_plane = uv_plane[:, 0::2]
    v_plane = uv_plane[:, 1::2]

    # Stack the Y, U, V planes to create a planar I444 image
    yuv_planar = np.vstack([y_plane, u_plane, v_plane])

    # Convert from I444 (YUV444 Planar) to RGB
    rgb = cv2.cvtColor(yuv_planar, cv2.COLOR_YUV2RGB_I444)
    return rgb

def decode_nv42(data, width, height, stride):
    """
    Decodes NV42 format (8-bit YUV 4:4:4 semi-planar, Y-plane followed by interleaved VU plane).
    This is the U/V swapped version of NV24.
    """
    effective_stride = stride if stride > 0 else width
    y_size = effective_stride * height
    vu_size = effective_stride * height * 2
    expected_size = y_size + vu_size

    if len(data) < expected_size:
        st.error(f"Incorrect data size for NV42. Expected at least {expected_size}, got {len(data)} bytes.")
        return None

    yuv_data = np.frombuffer(data[:expected_size], dtype=np.uint8)

    y_plane = yuv_data[:y_size].reshape(height, effective_stride)
    vu_plane = yuv_data[y_size:].reshape(height, effective_stride * 2)

    # Crop to actual width if stride is larger
    if effective_stride > width:
        y_plane = y_plane[:, :width]
        vu_plane = vu_plane[:, :width*2]

    # De-interleave VU plane (V is first, U is second)
    v_plane = vu_plane[:, 0::2]
    u_plane = vu_plane[:, 1::2]

    # Stack the Y, U, V planes to create a planar I444 image
    yuv_planar = np.vstack([y_plane, u_plane, v_plane])

    # Convert from I444 (YUV444 Planar) to RGB
    rgb = cv2.cvtColor(yuv_planar, cv2.COLOR_YUV2RGB_I444)
    return rgb

# --- YUV444 (3-Plane) ---
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
    "RAW10_PACKED": decode_raw10_packed,
    "RAW10_UNPACKED": decode_raw10_unpacked,
    "RAW12_PACKED": decode_raw12_packed,
    "RAW12_UNPACKED": decode_raw12_unpacked,
    # --- YUV420 Formats ---
    # 2-Plane
    "NV12": decode_nv12,   # Semi-Planar
    "NV21": decode_nv21,   # Semi-Planar (V and U swapped)
    "P010": decode_p010,   # Semi-Planar 10-bit
    "P012": decode_p012,   # Semi-Planar 12-bit
    # 3-Plane
    "I420": decode_i420,   # Planar
    "YV12": decode_yv12,   # Planar (V and U swapped)
    # --- YUV422 Formats ---
    # 1-Plane
    "YUYV": decode_yuyv,   # Packed
    # 2-Plane
    "NV16": decode_nv16,   # Semi-Planar
    "NV61": decode_nv61,   # Semi-Planar (V and U swapped)
    "NV20": decode_nv20,   # Semi-Planar 10-bit
    # --- YUV444 Formats ---
    # 2-Plane
    "NV24": decode_nv24,   # Semi-Planar
    "NV42": decode_nv42,   # Semi-Planar (V and U swapped)
    # 3-Plane
    "YUV444": decode_yuv444, # Planar
}

FORMAT_DISPLAY_NAMES = {
    "RAW10_PACKED": "RAW10 (1-Plane 10-bit, Packed)",
    "RAW10_UNPACKED": "RAW10 (1-Plane 10-bit, Unpacked)",
    "RAW12_PACKED": "RAW12 (1-Plane 12-bit, Packed)",
    "RAW12_UNPACKED": "RAW12 (1-Plane 12-bit, Unpacked)",
    # YUV420
    "NV12": "NV12 (YUV420 2-Plane)",
    "NV21": "NV21 (YUV420 2-Plane, VU swapped)",
    "P010": "P010 (YUV420 2-Plane, 10-bit)",
    "P012": "P012 (YUV420 2-Plane, 12-bit)",
    "I420": "I420 (YUV420 3-Plane)",
    "YV12": "YV12 (YUV420 3-Plane, VU swapped)",
    # YUV422
    "YUYV": "YUYV (YUV422 1-Plane, Packed)",
    "NV16": "NV16 (YUV422 2-Plane)",
    "NV61": "NV61 (YUV422 2-Plane, VU swapped)",
    "NV20": "NV20 (YUV422 2-Plane, 10-bit)",
    # YUV444
    "NV24": "NV24 (YUV444 2-Plane)",
    "NV42": "NV42 (YUV444 2-Plane, VU swapped)",
    "YUV444": "YUV444 (YUV444 3-Plane)",
}

class TabImageViewer:
    def render(self):
        st.header("Image Viewer")

        uploaded_file = st.file_uploader("Choose an image file", type=None)

        # Create a list of display names in the correct order
        format_options = [FORMAT_DISPLAY_NAMES.get(key, key) for key in DECODING_FUNCTIONS.keys()]
        # Create a reverse map from display name to format key
        format_key_map = {v: k for k, v in FORMAT_DISPLAY_NAMES.items()}

        # Sidebar for controls
        st.sidebar.header("Image Properties")
        selected_display_name = st.sidebar.selectbox(
            "Select Image Format",
            format_options
        )
        image_format = format_key_map.get(selected_display_name, selected_display_name)

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
