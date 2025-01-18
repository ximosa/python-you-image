import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import io
import math
st.set_page_config(
    page_title="mini-youtube",
    layout="wide"
)

st.title("mini-youtube")
def add_text_to_image(image, text, font_size, font_color, x, y, shadow_offset_size):
    """Añade texto a una imagen con ajuste de línea dinámico."""
    # Convertimos la imagen al modo RGBA
    image = image.convert("RGBA")
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("DejaVuSans.ttf", size=font_size)

    y_offset = y
    shadow_color = (0, 0, 0, 100)
    shadow_offset = (shadow_offset_size, shadow_offset_size)
    line_spacing = 15  # Ajusta el espacio entre líneas

    for line_text in text.splitlines():
        # Divide el texto en líneas, priorizando el ancho
        lines = []
        line = ""
        words = line_text.split()
        for word in words:
            test_line = line + " " + word if line else word
            text_width, text_height = draw.textbbox((0, 0), test_line, font=font)[2:]
            if text_width <= image.width - 150:  # Mayor espacio para texto ancho (ajustado)
                line = test_line
            else:
                lines.append(line)
                line = word
        lines.append(line)
        
         # Escribe el texto línea por línea centrado con sombra
        for line in lines:
            line_width, _ = draw.textbbox((0, 0), line, font=font)[2:]
            text_x = x - line_width // 2  # Centra cada línea
            
            # Sombra del texto
            draw.text((text_x + shadow_offset[0], y_offset + shadow_offset[1]), line, font=font, fill=shadow_color)
            
            # Texto principal
            draw.text((text_x, y_offset), line, fill=font_color, font=font)
            y_offset += text_height + line_spacing
            
    return image.convert("RGB")

def create_thumbnail(uploaded_image, title, font_size, font_color, text_x_position_factor, text_y_position_factor, shadow_offset_size):
    """Crea la miniatura con el texto superpuesto."""
    if uploaded_image is not None:
        try:
            # Abre la imagen con PIL
            image = Image.open(uploaded_image)
            
            # Convierte a RGB si es necesario
            if image.mode != "RGB":
              image = image.convert("RGB")
            
            width, height = image.size
            
            # Redimensiona la imagen a 1280x720 manteniendo las proporciones
            target_width = 1280
            target_height = 720
            image_ratio = width / height
            target_ratio = target_width / target_height

            if image_ratio > target_ratio:
                new_height = target_height
                new_width = int(new_height * image_ratio)
            else:
                new_width = target_width
                new_height = int(new_width / image_ratio)

            image = image.resize((new_width,new_height), Image.Resampling.LANCZOS)

            # Corta la imagen para que quede en 1280x720
            if new_width > target_width:
                left = (new_width - target_width) / 2
                right = (new_width + target_width) / 2
                image = image.crop((left, 0, right, target_height))
            if new_height > target_height:
                top = (new_height - target_height) / 2
                bottom = (new_height + target_height) / 2
                image = image.crop((0, top, target_width, bottom))

            width, height = image.size

            # Oscurece la imagen
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(0.4)  # Aumentamos el oscurecimiento
            
            # Ajusta el tamaño de la fuente según el tamaño de la imagen
            
            # Calcula la posición del texto centrada, más arriba
            x = int(width * text_x_position_factor)
            y = int(height * text_y_position_factor)

            thumbnail = add_text_to_image(image, title, font_size, font_color, x, y, shadow_offset_size)
            return thumbnail
        except Exception as e:
            st.error(f"Error al procesar la imagen: {e}")
            return None
    return None

def compress_image(image, max_size_mb):
    """Comprime la imagen para que no sobrepase el tamaño maximo"""
    img_byte_arr = io.BytesIO()
    quality = 95
    image.save(img_byte_arr, format="JPEG", quality=quality)
    
    while img_byte_arr.getbuffer().nbytes > max_size_mb * 1024 * 1024 and quality > 0:
      quality -= 5 # Reduce la calidad en cada iteración
      img_byte_arr = io.BytesIO()
      image.save(img_byte_arr, format="JPEG", quality=quality)
    
    if quality == 0:
        st.warning(f"Warning: la imagen comprimida sigue siendo mayor que {max_size_mb} MB, puede ser necesario usar una imagen de menor tamaño para evitar esto")
    
    img_byte_arr = img_byte_arr.getvalue()
    return img_byte_arr

st.title("Creador de Miniaturas para Videos")

uploaded_image = st.file_uploader("Sube la imagen base:") # Elimina el tipo de archivo
title = st.text_area("Introduce el título:", height=150)
font_color = st.color_picker("Color del texto:", "#D4AC0D")
max_size_mb = st.number_input("Tamaño maximo de la imagen (MB):", min_value=0.1, max_value=10.0, value=2.0)

if 'uploaded_image' not in st.session_state:
    st.session_state['uploaded_image'] = None

if uploaded_image:
    st.session_state['uploaded_image'] = uploaded_image
    
if st.session_state['uploaded_image'] is not None:
    font_size = st.slider("Tamaño de la fuente:", 10, 100, 55)
    shadow_offset_size = st.slider("Grosor del texto:", 0, 10, 2)
    text_x_position_factor = st.slider("Posición Horizontal del texto:", 0.0, 1.0, 0.5)
    text_y_position_factor = st.slider("Posición Vertical del texto:", 0.0, 1.0, 0.25)

    thumbnail = create_thumbnail(st.session_state['uploaded_image'], title, font_size, font_color, text_x_position_factor, text_y_position_factor, shadow_offset_size)
    if thumbnail:
        st.image(thumbnail, caption="Previsualización de la miniatura", use_container_width=True)

        if st.button("Descargar miniatura"):
            # Comprime y descarga la imagen
            img_byte_arr = compress_image(thumbnail, max_size_mb)
            st.download_button(
                label="Descargar miniatura",
                data=img_byte_arr,
                file_name="miniatura.jpg",
                mime="image/jpeg"
            )

else:
  st.warning("Por favor, sube una imagen e introduce un título.")
