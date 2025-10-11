import io
from math import ceil
import copy

from PIL import Image, ImageDraw
import streamlit as st
import numpy as np


def net(image, grid_dim=6):

    width, height = image.size

    draw = ImageDraw.Draw(image)

    step_x = round(width / grid_dim, 0)
    step_y = round(height / grid_dim, 0)

    x = step_x
    y = step_y

    for i in range(grid_dim):
        draw.line([(x, 0), (x, height)], fill="blue", width=1)
        x += step_x
    for i in range(grid_dim):

        draw.line([(0, y), (width, y)], fill="red", width=1)
        y += step_y


def calc_vector_sign(image, grid_dim=6):

    pixels = image.load()

    width, height = image.size

    step_x = ceil(width / grid_dim)
    step_y = ceil(height / grid_dim)

    x = 0
    y = 0

    vector = []

    iterator = 1

    while iterator <= grid_dim**2:

        black_pixels = 0  # changes
        white_pixel = 0

        for i in range(y, y + step_y):  # j - x
            # i - y

            if i >= height:

                break
            for j in range(x, x + step_x):

                if j >= width:

                    break
                # r, g, b = pixels[j, i]

                # if r == 0 and g == 0 and b == 0:

                # black_pixels += 1

                pixel = pixels[j, i]

                # changes

                if isinstance(pixel, tuple):

                    r, g, b = pixels[j, i]

                    if r == 0 and g == 0 and b == 0:

                        black_pixels += 1
                else:
                    if pixel > 128:

                        white_pixel += 1
        if white_pixel == 0:

            vector.append(black_pixels)
        else:

            vector.append(white_pixel)
        if iterator % grid_dim == 0:

            x = 0

            y += step_y
        else:

            x += step_x
        iterator += 1
    return vector


def normalize(vector):

    # max_val = max(vector)

    # return [value / max_val for value in vector]

    suma = sum(vector)
    return [value / suma for value in vector]


def calcVectorSignForEtalon(etalon_image_list, grid_dim=6):

    result_list = []

    for image_ in etalon_image_list:

        vector_sign = calc_vector_sign(image_, grid_dim)

        vector_sign = normalize(vector_sign)

        vector_sign = make_binary(vector_sign)
        # print(vector_sign)

        result_list.append(vector_sign)
    return result_list


def classification(weight_matrix, vector_sign):

    flag = True

    iterations = 0
    
    while flag and iterations < 1000:
        flag=False

        for i in range (len(vector_sign)):

            result = np.dot(weight_matrix[i], vector_sign)

            result = 1 if result > 0 else -1

            if result != vector_sign[i]:

                vector_sign[i] = result
                flag = True
        
        iterations += 1
        
    
    if iterations >= 1000:

        return []

    

    return vector_sign.copy()   

def make_binary (vector):

    new_res = []

    for i in vector:

        if i >= 0.04:
            new_res.append(1)

        elif i < 0.04:
            new_res.append(-1)
    
    return new_res

def createWeightMatrix(classDict : dict, grid_dim):

    vector_list = []
    weight_matrix = np.zeros((grid_dim**2, grid_dim**2))

    for elem in classDict.values():

        for list_ in elem:

            vector_list.append(list_)
    
    M = len(vector_list)

    for i in range(grid_dim**2):

        for j in range(grid_dim**2):

            if (i == j):
                weight_matrix[i,j] = 0
                continue
            
            suma = 0
            for k in range (M):
                suma += vector_list[k][i] * vector_list[k][j]
        
            # suma /= M
            weight_matrix[i,j] = suma
    
    return weight_matrix
   

def create_etalon_group(etalon_image_list, grid_dim):

    if len(etalon_image_list) == 0:

        return []
    conv_etalon_list = []

    for i, image in enumerate(etalon_image_list):

        image.seek(0)
        etalon_bytes = image.read()

        etalon_image = Image.open(io.BytesIO(etalon_bytes))

        conv_etalon_list.append(etalon_image)
    calculated_etalon_lists = calcVectorSignForEtalon(conv_etalon_list, grid_dim)

    # etalon_group = np.mean(calculated_etalon_lists, axis=0)

    return calculated_etalon_lists


def draw_etalon(file):

    all_columns = st.columns(3)
    for i, image in enumerate(file):

        etalon_bytes = image.read()
        etalon_image = Image.open(io.BytesIO(etalon_bytes))

        with all_columns[i % 3]:

            st.image(etalon_image, caption=f"{i + 1} etalon image")


def draw_elements(grid_dim=6):

    if "uploaders" not in st.session_state:
        st.session_state.uploaders = {0: []}  # {індекс: список файлів}

    indices = sorted(st.session_state.uploaders.keys())
    for i in indices:
        files = st.file_uploader(
            f"Файли категорії {i+1}",
            type=["bmp"],
            key=f"uploader_{i}",
            accept_multiple_files=True,
        )

        draw_etalon(files)

        # Оновлюємо значення

        st.session_state.uploaders[i] = files or []

        # Якщо у цьому uploader зʼявився файл і ще немає наступного поля → додаємо і робимо rerun

        if files and (i + 1) not in st.session_state.uploaders:
            st.session_state.uploaders[i + 1] = []
            st.rerun()
    # --- Логіка очищення ---

    uploaded_file = st.file_uploader("Pick a file", type=["BMP"], key="main_image")
    empty_keys = [k for k, v in st.session_state.uploaders.items() if not v]
    if len(empty_keys) > 1:
        for k in empty_keys[:-1]:
            del st.session_state.uploaders[k]
        st.rerun()
    list_keys = list(st.session_state.uploaders.keys())

    # etalonResults = []

    # створення масиву вагових коефіцієнтів

    etalon_vectors = {}
    
    print(list_keys)

    for i in range(len(list_keys)):

        group_etalon = create_etalon_group(st.session_state.uploaders[list_keys[i]], grid_dim)
        group_etalon = np.array(group_etalon)

        if len(group_etalon) != 0:
            # etalonResults.append(group_etalon)

            etalon_vectors[list_keys[i]] = group_etalon

    

    if (len(etalon_vectors) == 3):

        weight_matrix = createWeightMatrix(etalon_vectors, grid_dim)


        st.session_state["weightMatrix"] = copy.deepcopy(weight_matrix)

    # завантаження і показ еталонних зображень ================================================================================

    # Робота з головною фотографією ================================================================================

    image_bytes = uploaded_file.read()

    orig_image = Image.open(io.BytesIO(image_bytes))
    image = Image.open(
        io.BytesIO(image_bytes)
    )  # обгортає данні (байти) у 'файл' і далі воно відкривається

    net(image, grid_dim)
    st.image(
        image, caption="uploaded Image", use_column_width=True
    )  # use_column_width - визначає властивість , яка автоматично пропорційно розтягує або стискує зображення

    col1, col2 = st.columns(2)

    vector_sign = []
    vector_sign_norm = []

    # вектори ознак та нормалізовані вектори ================================================================================

    with col1:

        button_calc = st.button("Calculate vector", type="primary")

        if button_calc:

            vector_sign = calc_vector_sign(orig_image, grid_dim)

            st.write(np.array(vector_sign).reshape(grid_dim, grid_dim))
    with col2:

        button_normalize = st.button("normalize")

        if button_normalize:

            if len(vector_sign) == 0:

                vector_sign = calc_vector_sign(
                    orig_image, grid_dim
                )  # main part of prog

                col1.write(np.array(vector_sign).reshape(grid_dim, grid_dim))
            vector_sign_norm = normalize(vector_sign)

            # print(np.mean(vector_sign_norm))
            # print(min(vector_sign_norm))

            vector_sign_norm = make_binary(vector_sign_norm)

            # if "vector_sign_norm" not in st.session_state:

            st.session_state["vector_sign_norm"] = vector_sign_norm.copy()

            st.write(np.array(vector_sign_norm).reshape(grid_dim, grid_dim))
    # create classification

    if st.button("Classificate"):

        # if len(etalonResults) != 0 and len(vector_sign_norm) != 0:
        

        if (
            "weightMatrix" in st.session_state
            and "vector_sign_norm" in st.session_state
        ):
            

            resultClasification = classification(
                st.session_state["weightMatrix"], st.session_state["vector_sign_norm"].copy()
            )

            # print(resultClasification)
            resultClasification = check_result(etalon_vectors, resultClasification)

            
            st.write(
                f"image is similar to the {resultClasification + 1} class"
            )

            st.session_state.pop("weightMatrix", None)
            st.session_state.pop("vector_sign_norm", None)

def check_result(all_examples : dict, result_class):

    # print(result_class)
    
    # for i, matrix in all_examples.items():

    #     for array in matrix:
            
    #         # print(np.shape(array))
    #         # print(np.shape(result_class))
    #         # print('\n\n')

    #         if (np.array_equal(array, result_class)):

    #             return i

    min_dist = float('inf')
    best_class = None
    
    # Перетворення result_class на NumPy-масив для порівняння
    result_class_np = np.array(result_class)

    for class_key, matrix in all_examples.items():
        # matrix містить еталонні вектори цього класу
        for array in matrix:
            # Обчислення відстані Хеммінга (кількість відмінностей)
            # np.sum(array != result_class_np) працює для NumPy-масивів
            dist = np.sum(array != result_class_np) 

            
            # print(best_class)
            
            if dist < min_dist:
                min_dist = dist
                best_class = class_key
                
    # Якщо мінімальна відстань дорівнює нулю, то співпадіння ідеальне.
    # Навіть якщо dist > 0, ви повернете найближчий клас.
    
    print(best_class)
    
    return best_class