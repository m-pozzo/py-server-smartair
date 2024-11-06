FROM python:3.11-slim

# Instala las dependencias necesarias para OpenCV y bibliotecas gráficas
RUN apt-get update && apt-get install -y libgl1-mesa-glx libglib2.0-0

# Copia los archivos del proyecto y configura el entorno
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt

# Exponer el puerto (ajústalo según el puerto de tu aplicación)
EXPOSE 4001

# Comando para ejecutar el servidor
CMD ["python", "server.py"]
