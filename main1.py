import io # допомагає емулювати поведінку файлу (загортати різні данні ніби у файл)
from PIL import Image, ImageDraw # Бібліотека для роботи з картинками

import streamlit as st
from function import *
st.write ('lab-1')

uploaded_file = st.file_uploader ("Pick a file", type=["BMP"])

try:
    image_bytes = uploaded_file.read()

    draw_elements (image_bytes)

except AttributeError:

    st.write("sth went wrong")