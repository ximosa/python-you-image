import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import io

def add_text_to_image(image, text, font_size, font_color, x, y):
    """Añade texto a una imagen con opciones de personalización."""
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("DejaVuSans.ttf", size=font_size)
    # Divide el texto en líneas si es demasiado largo
    lines = []
    line = ""
    words = text.split()
    for word in words:
        test_line = line + " " + word if line else word
        text_width, text_height = draw.textbbox((0, 0), test_line, font=font)[2:]
        if text_width <= image.width - 200: # Ajusta el margen
            line = test_line
        else:
            lines.append(line)
            line = word
    lines.append(line)

    # Escribe el texto linea por linea
    y_offset = y
    for line in lines:
        draw.text((x, y_offset), line, fill=font_color, font=font)
        y_offset += text_height  # Ajusta el espaciado entre lineas
    return image

def create_thumbnail(uploaded_image, title, font_size, font_color, text_position):
    """Crea la miniatura con el texto superpuesto."""
    if uploaded_image is not None:
      try:
          image = Image.open(uploaded_image).convert("RGB")
          width, height = image.size

          # Oscurece la imagen
          enhancer = ImageEnhance.Brightness(image)
          image = enhancer.enhance(0.6)  # Oscurece la imagen, 0 es negro

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
font_color = st.color_picker("Color de la fuente:", "#FFFFFF")
text_position = st.selectbox("Posición del texto:", ["Arriba Izquierda", "Arriba Centro", "Arriba Derecha", "Centro Izquierda", "Centro", "Centro Derecha", "Abajo Izquierda", "Abajo Centro", "Abajo Derecha"])

if st.button("Generar miniatura"):
    if uploaded_image and title:
        thumbnail = create_thumbnail(uploaded_image, title, font_size, font_color, text_position)
        if thumbnail:
            st.image(thumbnail, caption="Miniatura generada", use_container_width=True) # use_container_width
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
