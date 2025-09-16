from PIL import Image, ImageDraw
import streamlit as st
import io
from math import ceil
import numpy as np
import copy

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

        # black_pixels = 0
        white_pixel = 0
        
        for i in range (y, y + step_y ): # j - x
                                         # i - y
            if i >= height:

                break
            
            for j in range (x, x + step_x):
            
                if j >= width:

                    break

                # r, g, b = pixels[j, i] 

                # if r == 0 and g == 0 and b == 0:

                    # black_pixels += 1
                
                pixel = pixels[j,i]

                if (pixel != 0):

                    white_pixel+=1
        
        # vector.append (black_pixels)
        vector.append(white_pixel)

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

def  calcVectorSignForEtalon(etalon_image_list, grid_dim = 6):

    result_list = []

    for image_ in etalon_image_list:

        vector_sign = calc_vector_sign (image_, grid_dim)
        vector_sign = normalize (vector_sign)

        result_list.append (vector_sign)

    return result_list

def classification(etalon_lists, vector_sign):

    index = -1
    min_elem = -1

    for i, list_ in enumerate(etalon_lists):

        res = sum ([ (vector_sign[j] - list_[j]) ** 2 for j in range (len(list_))])
        res = res**0.5

        st.write (res)

        if (index == -1 or res < min_elem):

            index = i
            min_elem = res
    
    return (index, min_elem)

def draw_elements(grid_dim = 6):

    
    # завантаження і показ еталонних зображень ================================================================================

    all_columns = st.columns(3)

    etalon_files = st.file_uploader ("Pick a files", type=["BMP"],  accept_multiple_files=True)

    etalon_image_list = []

    for i, image in enumerate(etalon_files):
        
        etalon_bytes = image.read()
        etalon_image = Image.open (io.BytesIO(etalon_bytes))

        etalon_image_list.append(etalon_image)

        with all_columns[i % 3]:

            st.image (etalon_image, caption=f"{i + 1} etalon image")
    
    etalonResults = calcVectorSignForEtalon(etalon_image_list, grid_dim) ### Важлива змінна з еталонами нормалізованими ###

    st.session_state["etalonResults"] = copy.deepcopy(etalonResults)

    for i, elem in enumerate(etalonResults):

        with all_columns[i % 3]:

            st.write (np.array(elem).reshape(grid_dim, grid_dim))
    
    # Робота з головною фотографією ================================================================================

    uploaded_file = st.file_uploader ("Pick a file", type=["BMP"])
    image_bytes = uploaded_file.read()

    orig_image = Image.open (io.BytesIO(image_bytes))
    image = Image.open (io.BytesIO(image_bytes)) # обгортає данні (байти) у 'файл' і далі воно відкривається
    
    net (image, grid_dim)
    st.image (image, caption="uploaded Image", use_column_width=True) # use_column_width - визначає властивість , яка автоматично пропорційно розтягує або стискує зображення

    col1, col2= st.columns(2)

    vector_sign = []
    vector_sign_norm = []
    
    # вектори ознак та нормалізовані вектори ================================================================================

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
            

            vector_sign_norm = normalize (vector_sign)

            # if "vector_sign_norm" not in st.session_state:

            st.session_state["vector_sign_norm"] = vector_sign_norm.copy()

            st.write (np.array(vector_sign_norm).reshape(grid_dim, grid_dim))

    # create classification

    if st.button('Classificate'):

        # if len(etalonResults) != 0 and len(vector_sign_norm) != 0:    
        if "etalonResults" in st.session_state and "vector_sign_norm" in st.session_state:
            # resultClasification = classification(etalonResults, vector_sign_norm)

            resultClasification = classification(st.session_state["etalonResults"], st.session_state["vector_sign_norm"])

            st.write(f"image is similar to the {resultClasification[0]+1} image with counted similarity\n{resultClasification[1]}")

            st.session_state.pop("etalonResults", None)
            st.session_state.pop("vector_sign_norm", None)


# def draw_elements(grid_dim=6):

#     # 1. Еталонні зображення ========================================================================================
#     all_columns = st.columns(3)

#     etalon_files = st.file_uploader("Pick a files", type=["BMP"], accept_multiple_files=True)

#     etalon_image_list = []

#     for i, image in enumerate(etalon_files):
#         etalon_bytes = image.read()
#         etalon_image = Image.open(io.BytesIO(etalon_bytes))
#         etalon_image_list.append(etalon_image)

#         with all_columns[i % 3]:
#             st.image(etalon_image, caption=f"{i + 1} etalon image")

#     if etalon_image_list:
#         st.session_state["etalonResults"] = calcVectorSignForEtalon(etalon_image_list)

#         for i, elem in enumerate(st.session_state["etalonResults"]):
#             with all_columns[i % 3]:
#                 st.write(np.array(elem).reshape(grid_dim, grid_dim))

#     # 2. Завантаження головної картинки ==============================================================================
#     uploaded_file = st.file_uploader("Pick a file", type=["BMP"])
#     if uploaded_file:
#         image_bytes = uploaded_file.read()
#         orig_image = Image.open(io.BytesIO(image_bytes))
#         image = Image.open(io.BytesIO(image_bytes))

#         net(image, grid_dim)
#         st.image(image, caption="uploaded Image", use_column_width=True)

#         col1, col2 = st.columns(2)

#         # Вектор ознак
#         with col1:
#             if st.button("Calculate vector", type="primary"):
#                 st.session_state["vector_sign"] = calc_vector_sign(orig_image, grid_dim)
#                 st.write(np.array(st.session_state["vector_sign"]).reshape(grid_dim, grid_dim))

#         # Нормалізація
#         with col2:
#             if st.button("Normalize"):
#                 if "vector_sign" not in st.session_state:
#                     st.session_state["vector_sign"] = calc_vector_sign(orig_image, grid_dim)
#                     col1.write(np.array(st.session_state["vector_sign"]).reshape(grid_dim, grid_dim))

#                 st.session_state["vector_sign_norm"] = normalize(st.session_state["vector_sign"])
                # st.write(np.array(st.session_state["vector_sign_norm"]).reshape(grid_dim, grid_dim))

#         # 3. Класифікація ==========================================================================================
#         if st.button("Classificate"):
#             if "etalonResults" in st.session_state and "vector_sign_norm" in st.session_state:
#                 resultClasification = classification(
#                     st.session_state["etalonResults"], st.session_state["vector_sign_norm"]
#                 )
#                 st.write(
#                     f"Image is similar to the {resultClasification[0]+1} image "
#                     f"with counted similarity\n{resultClasification[1]}"
#                 )
