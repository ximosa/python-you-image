import streamlit as st
import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageDraw, ImageFont, ImageTk
import io
import math
import os

# Función para convertir imágenes PIL a Tkinter
def pil_to_tk(image):
    return ImageTk.PhotoImage(image)


# Clase para gestionar el cuadro de texto interactivo
class DraggableText:
    def __init__(self, canvas, text, x, y, font_size, color, font_file):
        self.canvas = canvas
        self.text = text
        self.x = x
        self.y = y
        self.font_size = font_size
        self.color = color
        self.font_file = font_file
        self.is_dragging = False
        self.resize_corner = None
        self.font = ImageFont.truetype(self.font_file, size=self.font_size)
        self.rect = None
        self.text_id = None
        self.redraw()

    def redraw(self):
        """Redibuja el rectángulo y el texto."""
        if self.rect:
            self.canvas.delete(self.rect)
        if self.text_id:
            self.canvas.delete(self.text_id)
        
        # Calculamos las dimensiones del texto
        text_bbox = self.canvas.create_text((0, 0), text=self.text, font= (self.font_file,self.font_size),fill=self.color) # Usamos la misma fuente que PIL
        bbox = self.canvas.bbox(text_bbox)
        self.canvas.delete(text_bbox)

        if bbox:
          text_width = bbox[2] - bbox[0]
          text_height = bbox[3] - bbox[1]
        else:
          text_width = 100
          text_height = 50

        padding = 10
        rect_x1 = self.x - padding
        rect_y1 = self.y - padding
        rect_x2 = self.x + text_width + padding
        rect_y2 = self.y + text_height + padding

        # Dibujamos el rectángulo
        self.rect = self.canvas.create_rectangle(
          rect_x1, rect_y1, rect_x2, rect_y2, fill="black", stipple='gray12' ,outline='gray')

        # Dibujamos el texto
        self.text_id = self.canvas.create_text(self.x, self.y, text=self.text, fill=self.color, font=(self.font_file, self.font_size), anchor="nw")

    def on_press(self, event):
        """Inicia el arrastre o la redimensión."""
        # Verifica si el clic está cerca de un borde o esquina para redimensionar
        bbox = self.canvas.bbox(self.rect)
        if not bbox:
            return
        x1, y1, x2, y2 = bbox
        corner_size = 10  # Tamaño de las esquinas para redimensionar
        corners = [
            (x1, y1),
            (x2, y1),
            (x1, y2),
            (x2, y2),
        ]
        for i, (cx, cy) in enumerate(corners):
            if abs(event.x - cx) < corner_size and abs(event.y - cy) < corner_size:
                self.resize_corner = i
                return
            
            
        # Si no hay redimension, inicia el arrastre
        if x1 <= event.x <= x2 and y1 <= event.y <= y2:
          self.is_dragging = True
          self.drag_start_x = event.x
          self.drag_start_y = event.y


    def on_drag(self, event):
        """Mueve o redimensiona el cuadro de texto."""
        if self.is_dragging:
            dx = event.x - self.drag_start_x
            dy = event.y - self.drag_start_y
            self.x += dx
            self.y += dy
            self.drag_start_x = event.x
            self.drag_start_y = event.y
            self.redraw()
        elif self.resize_corner is not None:
            bbox = self.canvas.bbox(self.rect)
            if not bbox:
                return
            x1, y1, x2, y2 = bbox
            new_x = self.x
            new_y = self.y
            
            if self.resize_corner == 0:  # Top Left
                new_x = self.x + (event.x - x1)
                new_y = self.y + (event.y - y1)
                
            elif self.resize_corner == 1:  # Top Right
              new_y = self.y + (event.y - y1)
              
            elif self.resize_corner == 2:  # Bottom Left
              new_x = self.x + (event.x - x1)
              
            elif self.resize_corner == 3:  # Bottom Right
              pass

            text_bbox = self.canvas.create_text((0, 0), text=self.text, font= (self.font_file,self.font_size),fill=self.color)
            bbox_text = self.canvas.bbox(text_bbox)
            self.canvas.delete(text_bbox)

            if bbox_text:
                text_width = bbox_text[2] - bbox_text[0]
                text_height = bbox_text[3] - bbox_text[1]
            else:
                text_width = 100
                text_height = 50

            # Calculamos la nueva posicion del texto
            self.x = new_x
            self.y = new_y

            self.redraw()

    def on_release(self, event):
        """Detiene el arrastre o la redimensión."""
        self.is_dragging = False
        self.resize_corner = None
        

    def get_text_area(self):
      """Devuelve las coordenadas del rectangulo"""
      bbox = self.canvas.bbox(self.rect)
      return bbox
    

    def update_text(self, new_text):
      """Cambia el texto"""
      self.text = new_text
      self.redraw()
  

def create_thumbnail_tkinter(image_path, title, font_size, font_color, max_size_mb):
    """Crea la ventana tkinter para la edición de la imagen."""
    # Abre la imagen con PIL
    try:
        image = Image.open(image_path)
        if image.mode != "RGB":
            image = image.convert("RGB")
    except Exception as e:
        st.error(f"Error al cargar la imagen: {e}")
        return
    
    # Redimensiona la imagen manteniendo las proporciones
    width, height = image.size
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


    # Oscurece la imagen
    enhancer = ImageEnhance.Brightness(image)
    image = enhancer.enhance(0.4)  
    
    # Creando la ventana tkinter
    root = tk.Tk()
    root.title("Editor de Miniaturas")

    # Convierte la imagen PIL a un formato compatible con Tkinter
    tk_image = pil_to_tk(image)
    
    # Canvas para dibujar la imagen y el texto
    canvas = tk.Canvas(root, width=image.width, height=image.height)
    canvas.pack()

    # Dibuja la imagen en el canvas
    canvas.create_image(0, 0, image=tk_image, anchor="nw")

    # Creamos el objeto de texto interactivo
    # Calculamos una posicion inicial para el texto
    x = image.width // 2
    y = image.height // 2 - image.height // 4 # Ajustamos la posición del texto más arriba
    draggable_text = DraggableText(canvas, title, x, y, font_size, font_color, "DejaVuSans.ttf")

    # Configurar eventos
    canvas.bind("<Button-1>", draggable_text.on_press)
    canvas.bind("<B1-Motion>", draggable_text.on_drag)
    canvas.bind("<ButtonRelease-1>", draggable_text.on_release)
    
    def save_image():
      """Guarda la imagen editada en el directorio de descarga"""
      
      # obtenemos la imagen del canvas
      canvas.update() # refrescamos el canvas para que se apliquen todos los cambios
      
      # Obtenemos las coordenadas del texto y la caja
      bbox = draggable_text.get_text_area()
      
      #Obtenemos la imagen del canvas, y la convertimos a PIL
      
      ps = canvas.postscript(colormode = 'color')
      image_tk = Image.open(io.BytesIO(ps.encode('utf-8')))
      
      # Reducimos la imagen y la guardamos
      compressed_img_bytes = compress_image(image_tk,max_size_mb)
        
      file_path = filedialog.asksaveasfilename(defaultextension=".jpg", filetypes=[("JPEG files", "*.jpg")])
      if file_path:
        with open(file_path, "wb") as f:
            f.write(compressed_img_bytes)
      
      
    def update_text_callback():
      """Cambia el texto del cuadro"""
      new_text = new_text_entry.get()
      draggable_text.update_text(new_text)

    
    # Widget para cambiar el texto
    tk.Label(root, text="Nuevo texto:").pack()
    new_text_entry = tk.Entry(root)
    new_text_entry.insert(0,title)
    new_text_entry.pack()

    update_text_button = ttk.Button(root, text="Actualizar texto", command=update_text_callback)
    update_text_button.pack()

    # Botón para guardar la imagen
    save_button = ttk.Button(root, text="Guardar imagen", command=save_image)
    save_button.pack()


    root.mainloop()

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

uploaded_image = st.file_uploader("Sube la imagen base:")
title = st.text_input("Introduce el título:")
font_size = 55 # Establecemos el tamaño de la fuente fijo a 55
font_color = st.color_picker("Color del texto:", "#D4AC0D")
max_size_mb = st.number_input("Tamaño maximo de la imagen (MB):", min_value=0.1, max_value=10.0, value=2.0)

if st.button("Abrir editor"):
  if uploaded_image and title:
    # Crea un archivo temporal de la imagen para que tkinter pueda abrirla
    with open("temp_image.jpg", "wb") as f:
      f.write(uploaded_image.read())
    
    create_thumbnail_tkinter("temp_image.jpg", title, font_size, font_color, max_size_mb) # Llamamos a tkinter
    os.remove("temp_image.jpg")
  else:
    st.warning("Por favor, sube una imagen e introduce un título.")
