from PIL import Image, ImageDraw
import streamlit as st
import io
from math import ceil
import numpy as np

def net (image, grid_dim=6):

    width, height = image.size

    draw = ImageDraw.Draw (image)

    step_x = round(width / grid_dim, 0)
    step_y = round(height / grid_dim, 0)

    x = step_x
    y = step_y
    
    for i in range (grid_dim):
        draw.line ([(x, 0), (x, height)], fill='blue', width=1)
        x += step_x

    for i in range (grid_dim):

        draw.line ([(0, y), (width, y)], fill='blue', width=1)
        y += step_y

def calc_vector_sign (image, grid_dim = 6):

    pixels = image.load()
    width, height = image.size

    step_x = ceil(width / grid_dim)
    step_y = ceil(height / grid_dim)

    x = 0
    y = 0

    vector = []
    
    iterator = 1

    while iterator <= grid_dim ** 2:

        black_pixels = 0
        
        for i in range (y, y + step_y ): # j - x
                                         # i - y
            if i >= height:

                break
            
            for j in range (x, x + step_x):
            
                if j >= width:

                    break

                r, g, b = pixels[j, i] 

                if r == 0 and g == 0 and b == 0:

                    black_pixels += 1
        
        vector.append (black_pixels)

        if (iterator % grid_dim == 0):

            x = 0

            y += step_y

        else:

            x += step_x
        

        iterator += 1
    
    

    return vector
        
def normalize (vector):

    max_val = max(vector)

    return [round (value / max_val, 3) for value in vector]

def draw_elements (image_bytes, grid_dim = 6):

    orig_image = Image.open (io.BytesIO(image_bytes))
    image = Image.open (io.BytesIO(image_bytes)) # обгортає данні (байти) у 'файл' і далі воно відкривається
    
    net (image, grid_dim)
    st.image (image, caption="uploaded Image", use_column_width=True) # use_column_width - визначає властивість , яка автоматично пропорційно розтягує або стискує зображення

    col1, col2= st.columns(2)

    vector_sign = []
    
    with col1:

        button_calc = st.button ('Calculate vector', type='primary')

        if button_calc:
            
            vector_sign = calc_vector_sign (orig_image, grid_dim)

            st.write (np.array(vector_sign).reshape(grid_dim, grid_dim))

    with col2:

        button_normalize = st.button ('normalize')

        if button_normalize:

            if len(vector_sign) == 0:

                vector_sign = calc_vector_sign (orig_image, grid_dim) # main part of prog

                col1.write (np.array(vector_sign).reshape(grid_dim, grid_dim))
            

            vector_sign = normalize (vector_sign)

            st.write (np.array(vector_sign).reshape(grid_dim, grid_dim))


