import io # допомагає емулювати поведінку файлу (загортати різні данні ніби у файл)
from PIL import Image, ImageDraw # Бібліотека для роботи з картинками

import streamlit as st
from function import *
st.write ('lab-1')

try:
    

    draw_elements (grid_dim=5)

except AttributeError:

    st.write("sth went wrong")