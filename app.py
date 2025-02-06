import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import io
import math

st.set_page_config(
    page_title="mini-youtube",
    layout="wide"
)

def add_rich_text_to_image(image, text_configs, x, y, shadow_offset_size):
    """Añade texto formateado (múltiples colores, tamaños) a una imagen."""
    # Convertimos la imagen al modo RGBA
    try:
      image = image.convert("RGBA")
    except Exception as e:
      st.error(f"Error al convertir la imagen a RGBA: {e}")
      return image # or raise e, dependiendo de cómo quieras manejar el error
    draw = ImageDraw.Draw(image)  # Inicializar draw *después* de la conversión
    shadow_color = (0, 0, 0, 100)
    shadow_offset = (shadow_offset_size, shadow_offset_size)
    line_spacing = 15
    y_offset = y

    for line_config in text_configs:
        line_text = line_config["text"]
        font_size = line_config["font_size"]
        font_color = line_config["font_color"]
        font = ImageFont.truetype("DejaVuSans.ttf", size=font_size)

        lines = []
        line = ""
        words = line_text.split()

        # Verifica si hay texto que procesar
        if line_text:  # Agrega esta condición
            for word in words:
                test_line = line + " " + word if line else word
                try:
                    text_width, text_height = draw.textbbox((0, 0), test_line, font=font)[2:]
                except Exception as e:
                    st.error(f"Error al calcular el tamaño del texto: {e}")
                    return image # or raise e

                if text_width <= image.width - 150:
                    line = test_line
                else:
                    lines.append(line)
                    line = word
            lines.append(line)

            for line in lines:
                try:
                  line_width, _ = draw.textbbox((0, 0), line, font=font)[2:]
                except Exception as e:
                  st.error(f"Error al calcular el ancho de la línea: {e}")
                  return image

                text_x = x - line_width // 2

                # Sombra
                draw.text((text_x + shadow_offset[0], y_offset + shadow_offset[1]), line, font=font, fill=shadow_color)

                # Texto
                draw.text((text_x, y_offset), line, fill=font_color, font=font)
                y_offset += text_height + line_spacing
        else:
            text_height = 0  # Define text_height si no hay texto

    return image.convert("RGB")

def create_thumbnail(uploaded_image, text_configs, text_x_position_factor, text_y_position_factor, shadow_offset_size, container_color="#000000", image_position="center"):
    """Crea la miniatura con el texto formateado superpuesto."""
    if uploaded_image is not None:
        try:
            image = Image.open(uploaded_image)
            if image.mode != "RGB":
                image = image.convert("RGB")

            width, height = image.size

            # 1. Crea el lienzo con el color de fondo
            thumbnail = Image.new("RGB", (1280, 720), color=container_color)

            # 2. Redimensionar la imagen (opcional, para ajustarla al contenedor)
            max_width = 1280
            max_height = 720
            image_ratio = width / height
            if width > max_width or height > max_height:
              if width / max_width > height / max_height:
                new_width = max_width
                new_height = int(new_width / image_ratio)
              else:
                new_height = max_height
                new_width = int(new_height * image_ratio)
              image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
              width, height = image.size # Actualiza width y height

            # 3. Calcular la posición para pegar la imagen
            if image_position == "center":
                x = (1280 - width) // 2  # Centrar horizontalmente
                y = (720 - height) // 2  # Centrar verticalmente
            elif image_position == "top-left":
                x = 0
                y = 0
            # Puedes agregar más opciones de posicionamiento aquí
            else:
                x = 0
                y = 0

            # 4. Pegar la imagen en el lienzo
            thumbnail.paste(image, (x, y))

            # Calcula la posición del texto centrada, más arriba
            text_x = int(1280 * text_x_position_factor)
            text_y = int(720 * text_y_position_factor)

            thumbnail = add_rich_text_to_image(thumbnail, text_configs, text_x, text_y, shadow_offset_size)

            return thumbnail
        except Exception as e:
            st.error(f"Error al procesar la imagen: {e}")
            return None
    return None

def compress_image(image, max_size_mb):
    """Comprime la imagen."""
    img_byte_arr = io.BytesIO()
    quality = 95
    image.save(img_byte_arr, format="JPEG", quality=quality)

    while img_byte_arr.getbuffer().nbytes > max_size_mb * 1024 * 1024 and quality > 0:
        quality -= 5
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format="JPEG", quality=quality)

    if quality == 0:
        st.warning(f"Warning: la imagen comprimida sigue siendo mayor que {max_size_mb} MB")

    img_byte_arr = img_byte_arr.getvalue()
    return img_byte_arr

st.title("Creador de Miniaturas para Videos")

uploaded_image = st.file_uploader("Sube la imagen base:")
max_size_mb = st.number_input("Tamaño máximo de la imagen (MB):", min_value=0.1, max_value=10.0, value=2.0)

if 'uploaded_image' not in st.session_state:
    st.session_state['uploaded_image'] = None

if uploaded_image:
    st.session_state['uploaded_image'] = uploaded_image

if st.session_state['uploaded_image'] is not None:
    # Controles de la UI
    container_color = st.color_picker("Color de fondo del contenedor:", value="#000000")
    image_position = st.selectbox("Posición de la imagen:", ["center", "top-left"])

    num_text_parts = st.number_input("Número de partes del texto:", min_value=1, max_value=5, value=1, step=1)
    text_configs = []

    for i in range(num_text_parts):
        st.subheader(f"Parte del texto {i+1}")
        text = st.text_area(f"Texto {i+1}:", height=68)  # Altura mínima de 68
        font_size = st.slider(f"Tamaño de la fuente {i+1}:", 10, 100, 55)
        font_color = st.color_picker(f"Color del texto {i+1}:", "#D4AC0D")
        text_configs.append({"text": text, "font_size": font_size, "font_color": font_color})

    shadow_offset_size = st.slider("Grosor del texto:", 0, 10, 2)
    text_x_position_factor = st.slider("Posición Horizontal del texto:", 0.0, 1.0, 0.5)
    text_y_position_factor = st.slider("Posición Vertical del texto:", 0.0, 1.0, 0.25)

    # Creación de la miniatura
    thumbnail = create_thumbnail(st.session_state['uploaded_image'], text_configs, text_x_position_factor, text_y_position_factor, shadow_offset_size, container_color, image_position)

    if thumbnail:
        st.image(thumbnail, caption="Previsualización de la miniatura", use_container_width=True)

        if st.button("Descargar miniatura"):
            img_byte_arr = compress_image(thumbnail, max_size_mb)
            st.download_button(
                label="Descargar miniatura",
                data=img_byte_arr,
                file_name="miniatura.jpg",
                mime="image/jpeg"
            )

else:
    st.warning("Por favor, sube una imagen.")
