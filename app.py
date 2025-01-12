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
    
    # Calcula la altura total del texto
    total_text_height = len(lines) * text_height
    
    # Calcula las coordenadas del rectángulo de fondo
    padding = 10  # Ajusta el padding para que no este pegado al borde
    rect_x0 = x - padding
    rect_y0 = y - padding
    rect_x1 = image.width - x - padding
    rect_y1 = y + total_text_height + padding
    
    # Dibuja el fondo oscuro transparente
    draw.rectangle((rect_x0, rect_y0, rect_x1, rect_y1), fill=(0, 0, 0, 128))  # Negro con 50% de transparencia

    # Escribe el texto linea por linea
    y_offset = y
    for line in lines:
        draw.text((x, y_offset), line, fill=font_color, font=font)
        y_offset += text_height  # Ajusta el espaciado entre lineas

    return image

def create_thumbnail(uploaded_image, title, font_size, font_color):
    """Crea la miniatura con el texto superpuesto."""
    if uploaded_image is not None:
      try:
          image = Image.open(uploaded_image).convert("RGB")
          width, height = image.size

          # Oscurece la imagen
          enhancer = ImageEnhance.Brightness(image)
          image = enhancer.enhance(0.6)  # Oscurece la imagen, 0 es negro

          # Ajusta la posición del texto al centro
          x = width // 2 - 100
          y = height // 2 - 30

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

if st.button("Generar miniatura"):
    if uploaded_image and title:
        thumbnail = create_thumbnail(uploaded_image, title, font_size, font_color)
        if thumbnail:
            st.image(thumbnail, caption="Miniatura generada", use_container_width=True)
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
