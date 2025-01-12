import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io

def add_text_to_image(image, text, font_size, font_color, x, y):
    """Añade texto a una imagen con opciones de personalización."""
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("arial.ttf", size=font_size)  # Aseguramos que arial.ttf exista
    draw.text((x, y), text, fill=font_color, font=font)
    return image

def create_thumbnail(uploaded_image, title, font_size, font_color, text_position):
    """Crea la miniatura con el texto superpuesto."""
    if uploaded_image is not None:
      try:
          image = Image.open(uploaded_image).convert("RGB")  # Convierte a RGB para consistencia
          width, height = image.size

          # Ajusta la posición del texto según la selección del usuario
          if text_position == "Arriba Izquierda":
              x, y = 10, 10
          elif text_position == "Arriba Centro":
              x, y = width // 2 - 100, 10
          elif text_position == "Arriba Derecha":
               x, y = width - 250, 10
          elif text_position == "Centro Izquierda":
              x, y = 10, height // 2 - 30
          elif text_position == "Centro":
              x, y = width // 2 - 100, height // 2 - 30
          elif text_position == "Centro Derecha":
              x, y = width - 250, height // 2 - 30
          elif text_position == "Abajo Izquierda":
              x, y = 10, height - 80
          elif text_position == "Abajo Centro":
              x, y = width // 2 - 100, height - 80
          elif text_position == "Abajo Derecha":
               x, y = width - 250, height - 80

          thumbnail = add_text_to_image(image, title, font_size, font_color, x, y)
          return thumbnail
      except Exception as e:
          st.error(f"Error al procesar la imagen: {e}")
          return None
    return None

st.title("Creador de Miniaturas para Videos")

uploaded_image = st.file_uploader("Sube la imagen base:", type=["png", "jpg", "jpeg"])
title = st.text_input("Introduce el título:")
font_size = st.slider("Tamaño de la fuente:", 10, 100, 40)
font_color = st.color_picker("Color de la fuente:", "#FFFFFF")  # Blanco por defecto
text_position = st.selectbox("Posición del texto:", ["Arriba Izquierda", "Arriba Centro", "Arriba Derecha", "Centro Izquierda", "Centro", "Centro Derecha", "Abajo Izquierda", "Abajo Centro", "Abajo Derecha"])

if st.button("Generar miniatura"):
    if uploaded_image and title:
        thumbnail = create_thumbnail(uploaded_image, title, font_size, font_color, text_position)
        if thumbnail:
            st.image(thumbnail, caption="Miniatura generada", use_column_width=True)

            # Opciones de descarga
            img_byte_arr = io.BytesIO()
            thumbnail.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            st.download_button(
                label="Descargar miniatura",
                data=img_byte_arr,
                file_name="miniatura.png",
                mime="image/png"
            )
    else:
        st.warning("Por favor, sube una imagen e introduce un título.")
