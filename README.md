# indEXa

**Programa para indexar discos unidades externas. Funciona en Linux, Mac y Windows.**

Este script es una prueba de concepto para aprender a manejar *wxPython* y *PyInstaller*. Por esa razón he tratado de comentar el código de la mejor forma posible. Así me servirá a mi en un futuro para recordar conceptos y también puede ayudar a las personas que quieran aprender a manejar scripts con wxPython.

El programa se compone de 4 módulos principales:

- **indEXa.py**: El código principal. En este módulo están todas las funciones que se usarán, así como el código de inicio del programa. Cada función está comentada explicando su funcionamiento y las particularidades que pueda presentar. 

- **imagenes.py**: Módulo creado con https://github.com/svn2github/wxPython/blob/master/3rdParty/XRCed/encode_bitmaps.py. Se han convertido imágenes PNG en código que wxPython pueda importar como imágenes. Se usa para mostrar pequeños iconos en el árbol de directorios y en el listado de unidades.

- **DialogoNuevaUnidad.py**: Módulo de interfaz. Es la ventana que permite añadir unidades a la base de datos. Está generado a partir de un archivo wxg de WxGlade contenido en la carpeta Maquetas.

- **UIPrincipal.py**: El módulo de interfaz principal. Generado con WxGlade como el anterior. En la versión inicial del programa tanto las funciones como el código de la interfaz estaban en un mismo archivo. Para mejorar la lectura del código he preferido separarlos.

Para poder usar el script es necesario instalar una serie de librerías que puedes encontrar en requeriments.txt.

- **TinyTag**: Actualmente no se usa para nada, ya que por defecto la extracción de metadatos está deshabilitada. Permite extraer las IDTags de archivos MP3. Se instala para mantener la compatibilidad y por si en versiones posteriores se vuelve a recuperar la opción de extraer IDTags.

- **psutil**: Librería para manejar unidades y particiones (entre otras cosas). Permite indexar las unidades conectadas al equipo, obtener su tamaño y varias cosas más.

- **wxPython**: Imprescindible. Es la librería que dibuja la UI del programa.

- **pypiwin32**: Sólo se carga si se usa Windows. En Mac o Linux dará error al tratar de instalarla. Permite obtener la etiqueta (label) de una unidad.

La forma más sencilla para instalar las librerías es ejecutar esta orden: `pip install -r requeriments.txt`
En Linux y Mac debes editar el archivo requeriments.txt para eliminar la última línea.

