from PIL import Image, ImageDraw
import streamlit as st
import io
from math import ceil
import numpy as np
import copy


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

        result_list.append(vector_sign)
    return result_list


def classification(etalon_lists, vector_sign):

    index = -1
    min_elem = -1

    for i, list_ in enumerate(etalon_lists):

        res = sum([(vector_sign[j] - list_[j]) ** 2 for j in range(len(list_))])
        res = res**0.5

        st.write(res)

        if index == -1 or res < min_elem:

            index = i
            min_elem = res
    return (index, min_elem)


def create_etalon_group(etalon_image_list, grid_dim=6):

    if len(etalon_image_list) == 0:

        return []
    conv_etalon_list = []

    for i, image in enumerate(etalon_image_list):

        image.seek(0)
        etalon_bytes = image.read()

        etalon_image = Image.open(io.BytesIO(etalon_bytes))

        conv_etalon_list.append(etalon_image)
    calculated_etalon_lists = calcVectorSignForEtalon(conv_etalon_list, grid_dim)

    etalon_group = np.mean(calculated_etalon_lists, axis=0)

    return etalon_group


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

    etalonResults = []

    for i in range(len(list_keys)):

        group_etalon = create_etalon_group(st.session_state.uploaders[i], grid_dim)

        if len(group_etalon) != 0:
            etalonResults.append(group_etalon)
    st.session_state["etalonResults"] = copy.deepcopy(etalonResults)

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

            # if "vector_sign_norm" not in st.session_state:

            st.session_state["vector_sign_norm"] = vector_sign_norm.copy()

            st.write(np.array(vector_sign_norm).reshape(grid_dim, grid_dim))
    # create classification

    if st.button("Classificate"):

        # if len(etalonResults) != 0 and len(vector_sign_norm) != 0:

        if (
            "etalonResults" in st.session_state
            and "vector_sign_norm" in st.session_state
        ):
            # resultClasification = classification(etalonResults, vector_sign_norm)

            resultClasification = classification(
                st.session_state["etalonResults"], st.session_state["vector_sign_norm"]
            )

            st.write(
                f"image is similar to the {list_keys[resultClasification[0]] + 1} image with counted similarity\n{resultClasification[1]}"
            )

            st.session_state.pop("etalonResults", None)
            st.session_state.pop("vector_sign_norm", None)
