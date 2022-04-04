#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

#0.1 Primera versión usable. Se usa para generar los primeros ejecutables
#0.2 Se eliminan todos los prints para prevenir errores.
#0.21 Se elimina la opción de escanear metadatos. Por ahora no se van a usar, así que no es necesario incluirlos.
#0.22 Se añade la opción de ver el espacio disponible y ocupado en la unidad, así como la fecha en que se añadió a la base de datos.
#0.23 Corregido un bug en SetStatusText que hacía que el programa no cargara las carpetas
#0.24 Posible bug corregido que impide escanear algunos discos duros
#0.25 Añadida la posibilidad de indexar una carpeta
#0.26 Se añade la posibilidad de poder mostrar todas las unidades, aunque se trate de unidades de sistema. Se añaden tooltips
#0.27 Hacer que en Windows se obtenga la etiqueta de la unidad y se escriba como sugerencia
#0.28 Se añade una nueva opción para buscar archivos duplicados
#0.29 Cambios en la forma de listar unidades. Se puede establecer el valor True para que muestre TODAS las particiones
#0.3 Se comprime la base de datos al eliminar una unidad. 
#0.31 Se muestra el tamaño total de las carpetas
#0.32 Añadir opción para renombrar unidades
#0.33 Añadir opción para ver o ocultar archivos ocultos
#0.34 Ahora se pueden abrir los archivos listados haciendo click izquierdo sobre el ítem
#0.4 Cambio completo del programa. Se divide el script entre código e interfaz y se comentan todas las funciones. También se limpia un poco el código
#0.41 Se cambia la forma en que los metadatos se guardan en los items del árbol de carpetas. Ahora existe coherencia.

#Icono por https://www.freepik.com/

'''
Módulos que se cargan:
wx para obtener las funciones que dibujan la interfaz
sqlite3 para las funciones de la base de datos
math para la conversión entre unidades
os, sys y subprocess para las funciones de carga de programas y acceso a archivos
psutil para obtener el acceso a las particiones y a su tamaño
pathlib para obtener información de las carpetas y de los archivos que cuelgan de ellas
'''
import wx, sqlite3, math, os, sys, psutil, datetime,subprocess
from pathlib import Path

#Se cargan los módulos de la interfaz, generados desde wxGlade
from UIPrincipal import *
from DialogoNuevaUnidad import *
#Y las imágenes generadas por el script obtenido en
#https://github.com/svn2github/wxPython/blob/master/3rdParty/XRCed/encode_bitmaps.py
from imagenes import *


if sys.platform=='win32': #Se carga esta librería para obtener la etiqueta de la unidad seleccionada
    import win32api
    #Sólo en Windows. Se instala con pip install pypiwin32

nombre_app = "indEXa 0.41β"

#En las primeras versiones añadí la posibilidad de guardar los metadatos de los archivos MP3 (álbum, artista, nombre)
#Era útil, pero significaba añadir un campo extra con etiquetas a la interfaz principal, complicándola. Y por eso lo quité
#La función de la añadir datos a la base de datos aun tiene esta opción, pero puede deshabilitarse mediante el flag "metadatos"
metadatos = False


if metadatos: #Sólo si se activa metadatos se cargan estos dos módulos
    from tinytag import TinyTag #Este sirve para obtener metadados de los mp3
    import mimetypes #Y este para identificar el tipo de archivo y devolver su mimetype



def devuelve_tamano(tamano):
    #Convierte un tamano dado en bits a uno algo más legible.
    tamano = int(tamano)
    if tamano == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB") #Escalera de tamaño. Cada 1024 hay un salto al siguiente
    i = int(math.floor(math.log(tamano, 1024)))
    p = math.pow(1024, i)
    s = round(tamano / p, 2)
    return "%s %s" % (s, size_name[i])

def imagen_arbol(tipo):
    #Esta función devuelve una imagen para mostrarla en el árbol de directorios
    #Dependiendo del tipo de entrada (archivo/carpeta) se devolverá una imagen distinta
    #He creado esta función para que dependiendo del sistema operativo se cargue una imagen distinta
    il = wx.ImageList(16, 16)
    graficos_carpeta = {
        #Dependendiendo del OS se carga o bien la imagen por defecto o bien alguna de las almacenadas en imagenes.py
        'win32': carpeta_win.GetBitmap(),
        'linux': wx.ArtProvider.GetBitmap(wx.ART_FOLDER, wx.ART_MENU, (16,16)),
        'darwin': carpeta_mac.GetBitmap()
        }
    carpeta = graficos_carpeta[sys.platform]
    fldropenidx = fldridx =il.Add(carpeta)
    imgarchivo = wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE, wx.ART_MENU, (16,16))
    fileidx = il.Add(imgarchivo)
    app.frame.tArbol.SetImageList(il)
    
    if tipo == "archivo":
        respuesta = fileidx
    else:
        respuesta = fldridx
    return respuesta



def inicia_db():
    '''
    Esta función se usa para iniciar la base de datos y devolver el puntero de conexión se será global para toda la ejecución
    El código está algo sucio y seguro que se puede optimizar, pero es el resultado de distintas ideas, 
    añadidas en forma de parche al código existente
    En primer lugar se define la carpeta donde se inicia el programa y el nombre de la base de datos
    Esto es importante para facilitar la depuración, dado que si se encuentra un archivo "database.db" en la misma ruta del
    ejecutable, se cargará ese archivo. En caso contrario, se cargará desde la ubicación por defecto (que varía dependiendo del sistema operativo)
    '''
    home = Path.home()
    nombre_db = "database.db"
    global datapath
    ruta_db = {
        'win32': home / 'AppData/Roaming/indEXa',
        'linux': home / '.local/share/indEXa',
        'darwin': home / 'Library/Application Support/indEXa'
        }
    if sys.platform not in ruta_db:
        data_path = "."
    else:
        data_path = str(ruta_db[sys.platform])
    if not(Path(data_path).is_dir()):
        os.makedirs(data_path)
    if os.path.exists(nombre_db):
        con = sqlite3.connect(nombre_db)
    else:
        if os.path.exists(data_path+'/'+nombre_db):
            con = sqlite3.connect(data_path+'/'+nombre_db)
        else:
            con = sqlite3.connect(data_path+'/'+nombre_db)        
            cursorObj = con.cursor()
            #Se usa el CREATE TABLE IF NOT EXISTS para crear la tabla al inicio, siempre que no haya sido creada ya
            instruccion_sql = """ CREATE TABLE IF NOT EXISTS ZSTORAGEITEM (
                                                	ZPK	INTEGER,
                                                	ZENT	INTEGER,
                                                	ZTOTALBYTES	INTEGER,
                                                    ZUSEDBYTES INTEGER,
                                                	ZFILECOUNT	INTEGER,
                                                	ZFOLDERCOUNT	INTEGER,
                                                	ZISFOLDER	INTEGER,
                                                	ZPARENT	INTEGER,
                                                	ZCREACION	INTEGER,
                                                	ZPARTOFCATALOG	INTEGER,
                                                	ZFULLPATH	VARCHAR,
                                                	ZNAME	VARCHAR,
                                                	ZKIND	VARCHAR,
                                                	ZTITULO	VARCHAR,
                                                	ZARTISTA	VARCHAR,
                                                	ZALBUM	VARCHAR,
                                                	PRIMARY KEY(ZPK)
                                                ); """
                                                   
            cursorObj.execute(instruccion_sql)
            instruccion_sql = """ CREATE TABLE IF NOT EXISTS ZTOTALES (
                                                	ZPK	INTEGER,
                                                	ZNAME	VARCHAR,
                                                	ZITEMS	INTEGER,
                                                	PRIMARY KEY(ZPK)
                                                ); """
            cursorObj.execute(instruccion_sql)

            #Ahora se crean los índices. 
            #Las primeras versiones del programa no usaban índices y la búsqueda de los datos era increiblemente lenta
            #En las nuevas versiones los índices aplicados sobre ciertas variables mejoran la usabilidad.
            instruccion_sql = """ CREATE INDEX IF NOT EXISTS ZSTORAGEITEM_ZPARENT_INDEX ON ZSTORAGEITEM (ZPARENT); """
            cursorObj.execute(instruccion_sql)

            instruccion_sql = """ CREATE INDEX IF NOT EXISTS ZSTORAGEITEM_ZPARTOFCATALOG_INDEX ON ZSTORAGEITEM (ZPARTOFCATALOG); """
            cursorObj.execute(instruccion_sql)

            instruccion_sql = """ CREATE INDEX IF NOT EXISTS ZSTORAGEITEM_ZENT_INDEX ON ZSTORAGEITEM (ZENT); """
            cursorObj.execute(instruccion_sql)

            #Para terminar con la creación de la base de datos se incluye un auto_vacuum para que se optimicen las tablas
            #tras cada commit. De todas formas algo no debo hacer bien porque no siempre funciona. De hecho, he tenido que 
            #meter un Vacuum manual tras borrar una "Ubicación" porque de forma automática la tabla no se optimizaba.
            instruccion_sql = "PRAGMA auto_vacuum = INCREMENTAL"
            cursorObj.execute(instruccion_sql)
            instruccion_sql = "VACUUM"
            cursorObj.execute(instruccion_sql)
            con.commit()
    return con
    
    
def anade_a_la_base_de_datos(ruta, unidad,tamano, ventana):
    
    cursorObj = conector.cursor()
    max = 100
    dlg = wx.ProgressDialog("Añadiendo datos a la base de datos",
                           "Este proceso puede durar unos minutos",
                           maximum = max,
                           parent=ventana,
                           style = 0
                            | wx.PD_APP_MODAL
                            #| wx.PD_CAN_ABORT
                            #| wx.PD_CAN_SKIP
                            #| wx.PD_ELAPSED_TIME
                            #| wx.PD_ESTIMATED_TIME
                            #| wx.PD_REMAINING_TIME
                            | wx.PD_AUTO_HIDE
                            )
    try: #Toda la función de añadir se ejecuta en un try. Si falla, se muestra un mensaje de error reconocible
        todas_las_carpetas={}
        tamano_total = tamano[1]
        tamano_sumado = 0
        #OJO, eliminar la línea de abajo, que si no se borra la DB en cada ejecución. Sólo para depuración
        #cursorObj.execute('DELETE FROM ZSTORAGEITEM')
        #cursorObj.execute('DELETE FROM ZTOTALES')
        cursorObj.execute('SELECT * FROM ZTOTALES WHERE ZPK=1')
        rows = cursorObj.fetchall()
        if rows:
            valor_id = rows[0][2]+1
        else:
            valor_id = 1
        '''
        Explico lo de arriba. 
            valor_id se usa para saber en qué punto de la base de datos se empiezan a añadir nuevos datos.
            Si cuando se hace la búsqueda SQL rows está vacío (es decir, no hay ningún dato), el valor se establece a 1
            En caso contrario, se usa la posición del último dato añadido + 1 para empezar a añadir datos nuevos.
            Este valor se actualizará cuando se terminen de añadir los nuevos datos a la base de datos. 
        '''        
        valor_zent = 0
        valor_totalbytes = tamano[0]
        valor_bytesusados = tamano[1]
        valor_isfolder = 0
        valor_id_unidad = valor_id
        fecha_creacion = datetime.datetime.now().timestamp()
        datos = (valor_id, valor_zent, valor_totalbytes, valor_bytesusados, valor_isfolder, fecha_creacion, ruta, unidad)
        cursorObj.execute('''INSERT INTO ZSTORAGEITEM(ZPK, ZENT, ZTOTALBYTES, ZUSEDBYTES ,ZISFOLDER, ZCREACION, ZFULLPATH, ZNAME) VALUES( ?, ?, ?, ?, ?, ?, ?, ?)''', datos)
        album = ""
        artista = ""
        titulo = ""
        ficheros_analizados = 0
        #Se establece que la ruta principal tiene el valor 0. De ahí colgaran todas las ramas del árbol de carpetas
        todas_las_carpetas[ruta]=valor_id
        for path in Path(ruta).rglob('*'):  #Se obtienen todos los datos de la carpeta
            ruta_corregida = path.parent.as_posix()
            size = 0
            size_int = 0
            try: #Tratamos de obtener el tamaño del archivo. Si no es posible (porque no se tiene permiso), se obvia el dato
                size = str(path.stat().st_size)
                size_int = path.stat().st_size
            except:
                pass
        
            valor_id += 1
            tamano_sumado = tamano_sumado+size_int
            #Si se actualizaran los valores en cada iteración el programa iría lento. Por eso se actualiza cada 50 búsquedas 
            if ((ficheros_analizados%50) == 0):
                wx.Yield() #Forzamos el dibujado
                try:
                    valor_porciento = int((tamano_sumado/tamano_total)*100)
                    cadena = "Procesando "+devuelve_tamano(tamano_sumado)+" de "+devuelve_tamano(tamano_total)+"\n"+str(ficheros_analizados)+" ficheros analizados."                
                    dlg.Update(valor_porciento, cadena)
                except:
                    pass

            #Si se encuentra un archivo de música, se añaden los metadatos a la base de datos
            album = ""
            artista = ""
            titulo = ""
            if metadatos: #Sólo si el flag metadatos está en True
                if ((path.suffix) == '.mp3' or (path.suffix) == '.flac'):
                    try:
                        tag = TinyTag.get(path)
                        album = tag.album
                        artista = tag.artist
                        titulo = tag.title
                    except:
                        pass

            valor_parent = todas_las_carpetas[path.parent.as_posix()]
            valor_partofcatalog = valor_id_unidad
            valor_zent = 1
            if not(path.is_dir()):
                valor_isfolder = 0
                ficheros_analizados += 1    
                valor_zkind = 'archivo'            
                if metadatos: #De nuevo, si metadatos está activado, se obtiene el valor
                    try:
                        valor_zkind = mimetypes.MimeTypes().guess_type(path)[0]
                    except:
                        pass
            else:
                valor_zkind = 'carpeta'
                valor_isfolder = 1
                todas_las_carpetas[path.as_posix()]=valor_id
            datos = (valor_id, valor_zent, size, valor_isfolder, valor_parent, valor_partofcatalog, str(path.as_posix()), str(path.name), valor_zkind, titulo, artista, album)
            cursorObj.execute('''INSERT INTO ZSTORAGEITEM(ZPK, ZENT, ZTOTALBYTES, ZISFOLDER, ZPARENT, ZPARTOFCATALOG, ZFULLPATH, ZNAME, ZKIND, ZTITULO, ZARTISTA, ZALBUM) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', datos)
        datos = (1,"StorageItem", valor_id)
        #La orden de abajo actualiza el total de items de la base de datos. Este valor se usará en futuras adiciones como punto de entrada
        cursorObj.execute('DELETE FROM ZTOTALES')
        cursorObj.execute('''INSERT INTO ZTOTALES(ZPK, ZNAME, ZITEMS) VALUES(?, ?, ?)''', datos)
        # --= Se terminan de añadir archivos =--
        # --= Ahora se añade lo que ocupa cada carpeta =--
        tamano_carpeta(valor_id_unidad)
        conector.commit()
        dlg.Destroy()

    except Exception as e: 
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        a = str(exc_type) + " " + str(fname) + " " + str(exc_tb.tb_lineno)
        wx.MessageBox(a, 'Warning', wx.OK | wx.CANCEL | wx.ICON_WARNING)
        dlg.Update(0,str(e))    
    

def carga_tUnidades():
    #Esta función inicia la ejecución visual del programa. Se encarga listar todas las "Ubicaciones/Unidades" (no se como llamarlo)
    #y añadirlas a la lista de la izquierda. Antes de todo, y al igual que en una función definida anteriormente, se crean
    #imágenes que varian según el sistema operativo que se esté ejcutando.
    cursorObj = conector.cursor()
    app.frame.lUnidades.ClearAll()
    app.frame._il = wx.ImageList(32, 32)
    graficos_extraible = {
        'win32': extraible_win.GetBitmap(),
        'linux': wx.ArtProvider.GetBitmap(wx.ART_HARDDISK, wx.ART_MENU, (32,32)),
        'darwin': extraible_mac.GetBitmap()
        }
    extraible = graficos_extraible[sys.platform]
    img_idx = app.frame._il.Add(extraible)
    app.frame.lUnidades.SetImageList(app.frame._il, wx.IMAGE_LIST_SMALL)
    valores = []
    #Se buscan los valores donde ZENT sea 0 (ZENT define si se trata de una unidad principal o de otro dato)
    cursorObj.execute('SELECT * FROM ZSTORAGEITEM WHERE ZENT=0')
    rows = cursorObj.fetchall()
    app.frame.lUnidades.InsertColumn(0, "Unidades",width = 150)
    for row in rows:  
        #Se recorren los resultados y se añaden las distintas unidades a la lista
        app.frame.lUnidades.Append((row[11],))
        app.frame.lUnidades.SetItemData(app.frame.lUnidades.GetItemCount()-1,row[0]) 
        app.frame.lUnidades.SetItemImage(app.frame.lUnidades.GetItemCount() - 1, img_idx) 

def seleccion_unidades(evt):
    #Es la rutina que se ejecuta cuando se selecciona una unidad en el listado de la izquierda. En primer lugar se comprueba
    #que en verdad hay un valor seleccionado (con ind>=0). Si esto es así, se obtiene el valor del item y se llama a la función
    #carga_arbol con este valor. La función carga_arbol se encargará de dibujar el arbol de carpetas.
    ind = app.frame.lUnidades.GetFirstSelected()
    if ind >=0:
        item = app.frame.lUnidades.GetItem(ind,0)
        carga_arbol(item.GetText())
        app.frame.eBuscar.SetValue("")

def carga_arbol(unidad):
    #Esta fué la primera función que creé. Al igual que alguna otra, ha ido cambiando y creciendo mediante parches, por lo que
    #el código no es del todo limpio. Así y todo, funciona tal y como quería y de forma rápida. 
    cursorObj = conector.cursor() # Se crea el objeto cursor, para llamar a la base de datos. 
    #¿Es mejor hacerlo en cada función o crear uno en general? Ni idea, pero lo dejo así
    app.frame.lArbol.Show(False)
    app.frame.tArbol.Show(True)
    #Se oculta el listado de resultados y se muestra el árbol de carpetas
    app.frame.pPrincipal.Layout()
    app.frame.tArbol.DeleteAllItems()    #Se borra cualquier item que existiera
    app.frame.root = app.frame.tArbol.AddRoot(unidad) #Se nombra la primera rama con el nombre de la unidad.
    app.frame.tArbol.SetPyData(app.frame.root ,"Principal") 
    valor_a_buscar = (0,unidad,)
    cursorObj.execute('SELECT * FROM ZSTORAGEITEM WHERE ZENT=? AND ZNAME=?',valor_a_buscar)
    #La orden de arriba busca la unidad en la base de datos para a continuación sacar los datos de la fecha de creación
    #y del espacio libre/total
    rows = cursorObj.fetchall()
    ruta=rows[0][0]
    fecha_creacion = rows[0][8]
    espacio_total = rows[0][2]
    espacio_usado = rows[0][3]
    #En las primeras versiones existían registros que no tenían aun añadida la fecha de creación. Por eso añadí este try.
    #Actualmente todas las bases de datos nuevas se generan con esta información, pero mantengo el try por compatibilidad.
    try:
        fecha_creacion = datetime.datetime.fromtimestamp(fecha_creacion).strftime('%d-%m-%Y a las %H:%M:%S')
        porciento = str(round((espacio_usado/espacio_total)*100,2))
        texto = "Creado el " + fecha_creacion + ". Utilizados "+devuelve_tamano(espacio_usado)+ " de "+devuelve_tamano(espacio_total) + " (" +porciento+"%)"
    except:
        texto = "Utilizados "+devuelve_tamano(espacio_usado)+ " de "+devuelve_tamano(espacio_total)
    #Se añaden los datos a la barra de estado
    app.frame.barraestado.SetStatusText(texto)
    #OJO, aquí se ejecutan las dos funciones que forman el corazón de todo esto. "lista_carpeta" y "nueva_carpeta". 
    #A continuación explicaré qué hacen pero para resumir lista_carpeta general el contenido de una "carpeta" de la base de datos
    #y nueva_carpeta pinta su contenido en el arbol de directorios de la derecha (llamado tArbol)
    carpetas_inicio = lista_carpeta(ruta)
    nueva_carpeta(carpetas_inicio,app.frame.root)
    #Una vez extraidos los datos y pintados, se "abre" la carpeta.
    app.frame.tArbol.Expand(app.frame.root)

def lista_carpeta(ruta):
    '''
    Esta función es vital pero a la vez es realmente sencilla. La base de datos tiene todos los registros de forma contígua,
    pero identificados como carpetas o como archivos. Asimismo cada registro tiene los datos sobre "a quién pertenece".
    Por ejemplo, si el archivo "datos.txt" cuelga de la carpeta "cosas", el registro de "datos.txt" tiene un campo que 
    indica que es un archivo y que además su "parent" o carpeta contenedora es "cosas". 
    Esta función facilita este tipo de búsquedas. Se proporcia una ruta (o carpeta "parent") y se devuelve una variable que contiene
    todos los archivos de esa carpeta, junto con sus valores añadidos (tamaño, tipo, nombre, etc)
    '''
    cursorObj = conector.cursor()
    valores = []
    valor_a_buscar = (ruta,)
    #Se hace la búsqueda de todos los archivos que pertenezcan a la carpeta pasada como "ruta".
    cursorObj.execute('SELECT * FROM ZSTORAGEITEM WHERE ZPARENT=?',valor_a_buscar)
    rows = cursorObj.fetchall()
    #Se recorren los valores y se genera una variable "fila" que contendrá un diccionario con todos sus datos
    for row in rows:
        #Lo que hay abajo es un hack chungo. El valor del septimo campo de la tabla puede estar vacío o con datos
        #Si tiene datos, es una carpeta, si no, un archivo. 
        #Igual en versiones más avanzadas lo arreglo, pero por ahora cumple su cometido.
        if not(row[6]):
            carpeta=0
        else:
            carpeta=1
        fila = {
          "nombre": row[11],
          "tipo": row[12],
          "ID": row[0],
          "tamano": row[2],
          "carpeta":carpeta,
          "pista": row[1],
          "artista": row[1],
          "disco": row[1],
          "zparent": row[7],
          "ruta_completa": row[10]
        }
        #Se añade el diccionario al tupple valores
        valores.append(fila)
    return valores

def nueva_carpeta(archivos, parent_iid):
    '''
    Esta es la segunda función interesante de la parte del listado.
    El origen es una función recursiva que encontré en stackoverflow, que recorría una carpeta y sacaba el resultado de todas
    sus subcarpetas. 
    Luego, usé la idea para esta parte. La función recibe una variable con los archivos contenidos en una carpeta ("archivos")
    y la "carpeta" a la que pertenecen ("parent_iid" -nombre heredado de la función original-).
    Luego, mira el contendido de dichos archivos y separa los datos del diccionario. 
    Con esos datos discrimina lo recibido; si es una carpeta, dibuja una carpeta en tArbol, le pone los iconos, el tamaño y 
    añade un valor dummy llamado "Cargando..." para que la carpeta se pinte con contenido.
    Si es un archivo, lo pinta junto con todos los datos.
    Como digo, en principio la función era recursiva, y si se trataba de una carpeta se volvía a llamar a si misma para
    seguir dibujando el árbol de directorios. El problema era que cuando habían miles de archivos la carga se demoraba varios
    segundos. Por esta razón dejé la recursividad y usé el dummy "Cargando...". Ahora la carpeta está vacía y sólo se carga el
    contenido cuando se pulsa sobre el nombre de la carpeta. De esta forma se acelera la carga de los datos.
    
    También se ha añadido una opción para ocultar archivos ocultos o carpetas de sistema. Estas carpetas se definen en la variable
    llamada "prohibidas"
    '''
    for datos in archivos:
        carpeta=datos["carpeta"]
        tipo = datos["tipo"]
        id = datos["ID"]
        tamano = datos["tamano"]
        pista = datos["pista"]
        artista = datos["artista"]
        disco = datos["disco"]
        zparent=datos["zparent"]
        nombre = datos["nombre"]
        ruta_completa = datos["ruta_completa"]
        prohibidas = ["$RECYCLE.BIN","System Volume Information"]
        muestra_ocultos = app.frame.menubar.muestra_ocultos.IsChecked()
        if (nombre[0:1]=='.' or nombre in prohibidas) and not(muestra_ocultos):  #Se usa para no mostrar archivos ocultos
            pass
        else:
            item = app.frame.tArbol.AppendItem(parent_iid,nombre)
            app.frame.tArbol.SetItemText(item, devuelve_tamano(tamano), 1)
            app.frame.tArbol.SetPyData(item,(id, False, item)) 
            colorletras = wx.SystemSettings.GetColour(wx.SYS_COLOUR_LISTBOXTEXT)
            app.frame.tArbol.SetItemTextColour(item,colorletras)
            if (carpeta == 1):
                app.frame.tArbol.SetItemImage(item, imagen_carpeta, which = wx.TreeItemIcon_Normal)
                app.frame.tArbol.SetItemImage(item, imagen_carpeta, which = wx.TreeItemIcon_Expanded)
                app.frame.tArbol.AppendItem(item, "Cargando...")
            else:
                app.frame.tArbol.SetItemImage(item, imagen_archivo, which = wx.TreeItemIcon_Normal)


def extraer_datos_tvResultados(item):
    #Esta es la función que mencionaba en el comentario anterior. Se ejecuta al pulsar sobre un item de tArbol
    #Si es un archivo extrae su información y se es una carpeta ejecuta de nuevo "nueva_carpeta" para pintar su contenido.
    cursorObj = conector.cursor()
    valor = app.frame.tArbol.GetPyData(item)
    #Se comprueba si "valor" es distinto a "Principal". Esto es así para evitar ejecutar el resto de función si lo que
    #se ha seleccionado es la rama principal del árbol de carpetas.
    if (valor!="Principal"):
        cursorObj.execute('SELECT * FROM ZSTORAGEITEM WHERE ZPK=?',(valor[0],))
        datos = cursorObj.fetchall()[0]
        #Cambio la barra por un triángulo porque queda mejor.
        texto = datos[10].replace("/"," ▸ ")
        app.frame.barraestado.SetStatusText(texto)
        if (datos[6]==1) and (valor[1]==False): #datos[6] es 1 si se trata de una carpeta o 0 si se trata de un archivo
            #El valor[1] comprueba que la función no se ha ejecutado con anterioridad. Si se ha ejecutado antes el árbol ya está
            #dibujado y no es necesario dibujarlo de nuevo.
            id_en_arbol = valor[2] 
            #En la posición 2 se guarda el valor del item dentro del arbol. De esa forma se pueden añadir dentro el resto de items
            #Con la orden que sigue se borra el item "Cargando..."
            app.frame.tArbol.DeleteChildren(id_en_arbol)
            ruta = datos[0]
            carpetas_inicio = lista_carpeta(ruta)
            nueva_carpeta(carpetas_inicio,id_en_arbol)
            #Se establece el valor[3] en TRUE para que no se vuelva a dibujar el árbol.
            app.frame.tArbol.SetPyData(id_en_arbol,(valor[0], True, id_en_arbol))         

def muestra_archivos_ocultos(event):
    #Función para mostrar archivos ocultos
    #Se borran todos los items porque se tienen que volver a dibujar
    app.frame.tArbol.DeleteAllItems()
    #Se obtiene el índice del valor seleccionado, para dibujarlo de nuevo 
    ind = app.frame.lUnidades.GetFirstSelected()
    if ind >=0:
        item = app.frame.lUnidades.GetItem(ind,0)
        #Y se vuelve a lanzar la función
        carga_arbol(item.GetText())

def iniciar_busqueda(evt):
    cursorObj = conector.cursor()
    #Debido a que esta función puede tardar un rato en ejecutarse, lo que hago es mostrar un mensaje de espera en la tabla principal
    #El proceso es ocultar tArbol, mostrar lArbol, borrar el contenido, poner el mensaje de espera y cuando termine de realizar
    #la búsqueda, borrar de nuevo y escribir el resultado.
    app.frame.lArbol.Show(True)
    app.frame.tArbol.Show(False)
    app.frame.lArbol.DeleteAllItems()
    app.frame.lArbol.Append(("Buscando...",))
    app.frame.lArbol.Append(("",))
    app.frame.lArbol.Append(("Por favor, espera...",))
    #Con estas dos ordenes se fuerza el dibujado aunque no se haya salido del loop principal
    app.frame.pPrincipal.Layout()
    wx.Yield()
    
    #El símbolo "%" delante del valor a buscar equivale a un "*". Es decir, se busca el término independientemente de lo que tenga
    #por delante o por detrás.
    valor_a_buscar = ("%"+evt.GetString()+"%",)
    cursorObj.execute('SELECT * FROM ZSTORAGEITEM WHERE ZNAME LIKE ?',valor_a_buscar)
    rows = cursorObj.fetchall()
    app.frame.lArbol.DeleteAllItems()
    #Esta parte no tiene mucho misterio. Se recorre el resultado y se pintan los datos en lArbol.
    for row in rows:
        if row[11]:
            try:
                valor_a_buscar = (row[9],)
                cursorObj.execute('SELECT * FROM ZSTORAGEITEM WHERE ZPK=?',valor_a_buscar)
                rows = cursorObj.fetchall()
                unidad = rows[0][11]
            except:
                unidad = ""
            datos = (row[11],devuelve_tamano(row[2]),unidad, row[10])
            app.frame.lArbol.Append(datos)

def tamano_carpeta(carpeta):
    #Esta función devuelve el tamaño de una carpeta. Cuando se añade una unidad a la base de datos, antes de ejecutar el commit
    #se llama a esta función. Esta suma el contenido de cada carpeta de forma recursiva, devolviendo el tamaño total de la carpeta
    cursorObj = conector.cursor()
    datos = (carpeta,)
    tamano_total = 0
    cursorObj.execute('SELECT * FROM ZSTORAGEITEM WHERE ZPARENT=?',datos) #Se buscan todos los archivos que pertenecen a la carpeta
    rows = cursorObj.fetchall()
    for row in rows:
        tipo = row[6]
        id_carpeta = row[0]
        if tipo == 1:
            tamano = tamano_carpeta(id_carpeta) #Si se trata de una carpeta (tipo 1), se vuelve a llamar a la función
            datos_update = (tamano, id_carpeta,)
            cursorObj.execute('UPDATE ZSTORAGEITEM SET ZTOTALBYTES=? WHERE ZPK=?',datos_update)
        else:
            tamano = row[2]            
        tamano_total = tamano_total + tamano #Y se suma el tamaño al tamaño total
    return tamano_total  


def gestionar_unidad_seleccionada(evt, ventana):
    #Esta función discrimina entre dos tipos de acciones. Si se selecciona una partición, se coge el nombre y se añade a etiquetaUnidad
    #Por contra, si se selecciona "Añadir ubicación..." se muestra un cuadro de diálogo para seleccionar cualquier carpeta. Luego
    #se actua igual.
    ind = ventana.selUnidades.GetFirstSelected()
    if ind >=0:
        item = ventana.selUnidades.GetItem(ind,0)
        unidad = item.GetText()
        if unidad == "Añadir ubicación...":
            dlg = wx.DirDialog (None, "Selecciona una carpeta", "",wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)
            if dlg.ShowModal() == wx.ID_OK:
                dirname = dlg.GetPath()
                unidad = str(Path(dirname).name)
                ventana.selUnidades.SetItemText(0,dirname)
                ventana.etiquetaUnidad.Clear()
                ventana.etiquetaUnidad.write(unidad)
                wx.Button.Enable(ventana.btnAnadir)
            else:
                pass
            dlg.Destroy()
        else:
            wx.Button.Enable(ventana.btnAnadir)
            ventana.etiquetaUnidad.Clear()
            '''
            Si el sistema es Windows ("win32"), se usa la función win32api.GetVolumeInformation, para obtener la etiqueta de la unidad
            Hago esto porque en Linux/Mac es fácil obtener este dato, dado que la partición en Volumes/mnt ya lleva ese dato.
            En Windows esto no ocurre.
            Al inicio de la carga del programa se identifica también el sistema, para discriminar la carga de win32api (dado que este
            módulo no existe en Linux/Mac)
            '''
            if sys.platform=='win32': 
                etiquetawindows = win32api.GetVolumeInformation(unidad)[0]
                if len(etiquetawindows)>0:
                    ventana.etiquetaUnidad.write(etiquetawindows)
                else:
                    ventana.etiquetaUnidad.write(unidad)
            else:
                ventana.etiquetaUnidad.write(str(Path(unidad).name))
                

def gestionar_lista_unidades(ventana,todas):
    #Si todas es True se muestran todas las particiones, incluso las de sistema. No es recomendado, pero lo dejo por si alguien
    #lo quiere usar.
    if todas:
        discos = psutil.disk_partitions(all=True)
    else:
        discos = psutil.disk_partitions(all=False)
        
    ventana.selUnidades.ClearAll()
    ventana.selUnidades.InsertColumn(0, "Unidades",width = 150)
    ventana.selUnidades.Append(("Añadir ubicación...",))
    ventana.selUnidades.SetItemData(0,0)
    #Se revisan todas las particiones, y dependiendo de si se ha seleccionado mostrar todas o no, se muestran en la lista.
    for disco in discos:
        #Si el disco tiene alguna característica especial y se ha seleccionado no mostrar unidades especiales, no se dibuja.
        if (("rootfs" in disco[3]) or ("dontbrowse" in disco[3]) or ("fixed" in disco[3])) and not(todas):
            pass
        else:
            try:
                espacio = psutil.disk_usage(disco[1])
                usado = espacio[1]
                ventana.selUnidades.Append((disco[1],))
                ventana.selUnidades.SetItemData(self.selUnidades.GetItemCount()-1,usado)
            except:
                pass

def gestionar_boton_anadir(evt, ventana):
    ind = ventana.selUnidades.GetFirstSelected()
    if ind >=0 and ventana.etiquetaUnidad.GetLineText(0):
        item = ventana.selUnidades.GetItem(ind,0)
        ruta = item.GetText() #Se obtiene la ruta que se usará
        ruta = Path(ruta).as_posix() #Se pasa a formato estandar (Windows usa \ y Linux usa /)
        tamano = psutil.disk_usage(ruta) #Se obtiene el tamaño de la unidad
        unidad = ventana.etiquetaUnidad.GetLineText(0) #Y la etiqueta que le hemos dado a la unidad
        anade_a_la_base_de_datos(ruta, unidad,tamano, ventana) #Con esos datos, se llama a la función que añade los datos a la base de datos
        ventana.Destroy() #Y destruimos la ventana para volver a la ventana principal

def gestionar_checkbox(evt, ventana):
    #Se borra el contenido de etiquetaUnidad (si había algo) y se vuelve a dejar el botón de añadir como no disponible
    ventana.etiquetaUnidad.Clear()
    wx.Button.Disable(ventana.btnAnadir)
    if ventana.chkunidades.GetValue():
        gestionar_lista_unidades(ventana, True)
    else:
        gestionar_lista_unidades(ventana, False)


def abrir_ventana_gestionar(evt):
    dlg = NuevaUnidadDialog(app.frame, -1, "Añadir nueva unidad", size=(400, 200),style=wx.DEFAULT_DIALOG_STYLE)

    #Se establecen los lanzadores de la ventana de gestión. En el código original al llamar a una clase se usaba el self para
    #añadir la ventana de destino. Como estoy usando el código de la UI en módulos separados uso lambda para pasar la ventana
    #como objeto a la función. Estoy seguro de que no se debe hacer así, pero no conozco un método mejor.
    
    dlg.chkunidades.Bind(wx.EVT_CHECKBOX, lambda evt, ventana=dlg: gestionar_checkbox(evt, ventana))
    dlg.selUnidades.Bind(wx.EVT_LIST_ITEM_SELECTED, lambda evt, ventana=dlg: gestionar_unidad_seleccionada(evt, ventana))
    dlg.btnAnadir.Bind(wx.EVT_BUTTON, lambda evt, ventana=dlg: gestionar_boton_anadir(evt, ventana))
    gestionar_lista_unidades(dlg, False)
    
    dlg.ShowWindowModal()   
    
def al_cerrar_ventana_gestionar(evt):
    #En verdad todo esto no hace falta. Está sacado de un ejemplo y lo mantuve por si más adelante era necesario.
    #Lo único de verdad necesario es cargar las unidades al cerrar la ventana y destruir la ventana "Gestionar"
    dialog = evt.GetDialog()
    val = evt.GetReturnCode()
    try:
        btnTxt = { wx.ID_OK : "OK",
                   wx.ID_CANCEL: "Cancel" }[val]
    except KeyError:
        btnTxt = '<unknown>'
    carga_tUnidades()        
    dialog.Destroy()
    
def buscar_duplicados(evt):
    cursorObj = conector.cursor()
    
    #Se hace el mismo proceso que en la función de búsqueda para mostrar el mensaje de "Buscando..."
    app.frame.lArbol.Show(True)
    app.frame.tArbol.Show(False)
    app.frame.lArbol.DeleteAllItems()
    app.frame.lArbol.Append(("Buscando...",))
    app.frame.lArbol.Append(("",))
    app.frame.lArbol.Append(("Por favor, espera...",))
    app.frame.pPrincipal.Layout()
    wx.Yield()
    
    #Esta es quizás la búsqueda SQL más complicada del programa. Se genera una tabla nueva que junte los items con el mismo nombre
    #y el mismo tamaño (ZNAME y ZTOTALBYTES). Luego, de esa tabla se eliminan las carpetas y sólo se muestran archivos mayores a 
    #100 Mb. Y por último se muestran los resultados ordenados por tamaño.
    cursorObj.execute("""
        SELECT a.ZPK, a.ZTOTALBYTES, a.ZFULLPATH, a.ZNAME, a.ZPARTOFCATALOG
        FROM ZSTORAGEITEM a
        JOIN (SELECT ZTOTALBYTES, ZNAME, COUNT(*)
        FROM ZSTORAGEITEM 
        WHERE ZISFOLDER = 0 AND ZTOTALBYTES>100000000
        GROUP BY ZTOTALBYTES, ZNAME
        HAVING count(*) > 1 ) b
        ON a.ZTOTALBYTES = b.ZTOTALBYTES
        AND a.ZNAME = b.ZNAME
        ORDER BY a.ZTOTALBYTES DESC
    """)
    rows = cursorObj.fetchall()
    app.frame.lArbol.DeleteAllItems()
    
    #Esto simplemente recorre el resultado y lo pinta en el lArbol.
    for row in rows:
        valor_a_buscar = (row[4],)
        cursorObj.execute('SELECT * FROM ZSTORAGEITEM WHERE ZPK=?',valor_a_buscar)
        rows = cursorObj.fetchall()
        unidad = rows[0][11]
        datos = (row[3],devuelve_tamano(row[1]),unidad, row[2])
        app.frame.lArbol.Append(datos)



#Las dos funciones de abajo (al_abrir y al_pulsar se ejecutan al pulsar con el ratón o usar el teclado sobre tArbol)
def al_pulsar(evt):    
    try:
        pos = evt.GetPosition()
        item, flags, col = app.frame.tArbol.HitTest(pos)
        extraer_datos_tvResultados(item)
    except:
        pass

def al_abrir(evt):
    item = evt.GetItem()
    extraer_datos_tvResultados(item)
    
#Esta función es similar a las anteriores, pero se ejecuta al pulsar sobre un item en lArbol.
#Simplemente muestra la ruta del archivo en la barra de estado.
def pulsa_en_item(evt):
    ind = app.frame.lArbol.GetFirstSelected()
    if ind >=0:
        item = app.frame.lArbol.GetItem(ind,3)
        texto = item.GetText().replace("/"," ▸ ")
        app.frame.barraestado.SetStatusText(texto)

def boton_secundario_lArbol(evt):
    #Es una función similar a la de abajo. Al pulsar con el botón derecho sobre un ítem de lArbol permite abrir el archivo o su
    #ubicación.
    
    #Comprueba si se ha pulsado sobre un ítem y no sobre la parte vacía de la tabla.
    ind = app.frame.lArbol.GetFirstSelected()
    if ind >=0:
        ruta = app.frame.lArbol.GetItem(ind,3).GetText()

    #Este menú es igual al que usaré en la función que viene a continuación.
    app.frame.popupmenucarpeta = wx.Menu()
    menuAbrir = app.frame.popupmenucarpeta.Append(1, 'Abrir')
    menuSeparador = app.frame.popupmenucarpeta.Append(-1, "","",wx.ITEM_SEPARATOR)
    menuAbrirCarpetaContenedora = app.frame.popupmenucarpeta.Append(2, 'Abrir carpeta contenedora')
    app.frame.popupmenucarpeta.Bind(wx.EVT_MENU, lambda evt, ruta=ruta: abrir_desde_menu(evt, ruta, 0), menuAbrirCarpetaContenedora)
    app.frame.popupmenucarpeta.Bind(wx.EVT_MENU, lambda evt, ruta=ruta: abrir_desde_menu(evt, ruta, 1), menuAbrir)
    app.frame.PopupMenu(app.frame.popupmenucarpeta, evt.GetPoint())


def boton_secundario_tArbol(evt):
    #Esta función y la siguiente funcionan en paralelo. 
    #La función "boton_secundario_tArbol" se ejecuta cuando se hace clic derecho sobre un item de tArbol. Muestra dos opciones:
    #Abrir el item o Abrir su carpeta contenedora. Cuando se selecciona una de estas dos opciones, se llama a "abrir_desde_menu"
    cursorObj = conector.cursor()
    item = evt.GetItem()
    valor = app.frame.tArbol.GetPyData(item)
    #El if de abajo impide que se abra el menú si lo que se selecciona es el tronco del árbol de carpetas
    if valor!='Principal':
        valor_a_buscar = (valor[0],)
        #Con la siguiente búsqueda se obtiene la ruta del archivo o carpeta (ya que si no sólo tendríamos el nombre)
        cursorObj.execute('SELECT * FROM ZSTORAGEITEM WHERE ZPK=?',valor_a_buscar)
        ruta = cursorObj.fetchall()[0][10]
        #Se genera un menú con las opciones y se muestra al usuario.
        app.frame.popupmenucarpeta = wx.Menu()
        menuAbrir = app.frame.popupmenucarpeta.Append(1, 'Abrir')
        menuSeparador = app.frame.popupmenucarpeta.Append(-1, "","",wx.ITEM_SEPARATOR)
        menuAbrirCarpetaContenedora = app.frame.popupmenucarpeta.Append(2, 'Abrir carpeta contenedora')
        app.frame.popupmenucarpeta.Bind(wx.EVT_MENU, lambda evt, ruta=ruta: abrir_desde_menu(evt, ruta, 0), menuAbrirCarpetaContenedora)
        app.frame.popupmenucarpeta.Bind(wx.EVT_MENU, lambda evt, ruta=ruta: abrir_desde_menu(evt, ruta, 1), menuAbrir)
        app.frame.PopupMenu(app.frame.popupmenucarpeta, evt.GetPoint())

def abrir_desde_menu(evt,  dato, tipo):
    ruta = Path(dato)
    #Se comprueba si existe el archivo o carpeta. En caso contrario se muestra una advertencia
    if os.path.exists(ruta):
        if tipo == 0:
            ruta = str(ruta.parent)
            #Se debe abrir la carpeta contenedora
        else:
            ruta = str(ruta)
            #Se debe abrir el archivo/carpeta
        #En Windows se recurre a os.startfile; se trata de una función específica para el fin que necesitamos
        if sys.platform=='win32':
            os.startfile(os.path.realpath(ruta))
        else:
            #En Mac o Linux os.startfile no funciona, por lo que es necesario ejecutar un proceso llamando a open y pasando
            #la ruta como parámetro.
            subprocess.run(['open', os.path.realpath(ruta)])
    else:
        a = wx.MessageDialog(None, "Archivo no encontrado. Conecta la unidad y prueba de nuevo.", caption="Unidad no conectada",style=wx.OK|wx.ICON_WARNING|wx.CENTRE).ShowModal()



def menu_lista_unidades(event):
    #Este menú se muestra al hacer clic derecho sobre el listado izquierdo (el de unidades). Permite borrar o renombrar items.
    ind = app.frame.lUnidades.GetFirstSelected()
    if ind >=0:
        item = app.frame.lUnidades.GetItem(ind,0)
        x = event.GetX()
        y = event.GetY()
        ind = app.frame.lUnidades.HitTest((x, y))[0]
        if ind >=0:
            item = app.frame.lUnidades.GetItemText(ind)
            app.frame.popupmenu = wx.Menu()
            menuItemRenombrar = app.frame.popupmenu.Append(1, 'Renombrar...')
            menuSeparador = app.frame.popupmenu.Append(-1, "","",wx.ITEM_SEPARATOR)
            menuItemBorrar = app.frame.popupmenu.Append(2, 'Borrar...')
            app.frame.popupmenu.Bind(wx.EVT_MENU, renombra_unidades, menuItemRenombrar)
            app.frame.popupmenu.Bind(wx.EVT_MENU, borra_unidades, menuItemBorrar)
            app.frame.PopupMenu(app.frame.popupmenu, event.GetPosition())
        
def renombra_unidades(event):
    #Esta función se ejecuta cuando se selecciona "Renombrar..." en el listado de unidades. 
    cursorObj = conector.cursor()
    ind = app.frame.lUnidades.GetFirstSelected()
    item = app.frame.lUnidades.GetItem(ind,0)
    #Obtenemos el ID del item y su texto
    ZPK_item = app.frame.lUnidades.GetItemData(ind)
    texto_item = item.GetText()
    #Mostramos una ventana preguntando por el nuevo nombre y le pasamos el nombre antiguo para que se muestre por defecto
    r = wx.TextEntryDialog(None, 'Introduce el nuevo nombre', caption='Renombrar unidad',value=texto_item)
    if r.ShowModal() != wx.ID_OK:
        #Si se pulsa en cancelar se cancela el proceso
        return
    datos_update = (r.GetValue(),ZPK_item,)
    #Se ejecuta la orden para actualizar el nombre de la unidad
    cursorObj.execute('UPDATE ZSTORAGEITEM SET ZNAME=? WHERE ZPK=?',datos_update)
    conector.commit()
    #Y se vuelven a cargar las unidades en el listado de la izquierda
    carga_tUnidades()
    app.frame.tArbol.DeleteAllItems()
    
    
def borra_unidades(evt):
    #Función para borrar unidades tras seleccionar la opción en el menú contextual
    cursorObj = conector.cursor()
    #Se muestra un mensaje de advertencia
    r = wx.MessageDialog(None,'Atención. Te dispones a eliminar una unidad de la base de datos.\nEste proceso no se puede deshacer. ¿Quieres continuar?','¿Eliminar?',wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION).ShowModal()
    if r != wx.ID_YES:
        #Si cancelamos se cancela el proceso
        return
        
    ind = app.frame.lUnidades.GetFirstSelected()
    if ind >=0:
        #Obtenemos el ID del valor que queremos borrar
        item = app.frame.lUnidades.GetItemData(ind)
        valor = (item,)
        #Borramos todos los items que dependen de la unidad seleccionada
        cursorObj.execute('DELETE FROM ZSTORAGEITEM WHERE ZPARTOFCATALOG=?',valor)
        #Y la unidad seleccionada
        cursorObj.execute('DELETE FROM ZSTORAGEITEM WHERE ZPK=?',valor)
        #Se aplican los cambios
        conector.commit()
        #Y se comprime de nuevo la base de datos para optimizar su tamaño
        cursorObj.execute('VACUUM')
        conector.commit()
        #Para terminar se vuelven a cargar las unidades y se borran los items del tArbol para eliminar datos antiguos.
        carga_tUnidades()
        app.frame.tArbol.DeleteAllItems()    
    
def main(args):
    return 0

class indEXa_app(wx.App):
    def OnInit(self):
        self.frame = indEXa(None, wx.ID_ANY, "")
        self.SetTopWindow(self.frame)
        self.frame.Centre() #Se centra la ventana
        if os.path.exists('icono.ico'): #Si existe el icono en el mismo lugar que el script, se carga y se dibuja en la ventana
            ico = wx.Icon('icono.ico', wx.BITMAP_TYPE_ICO) #Sólo en Windows
            self.frame.SetIcon(ico)
        self.frame.Show()
        return True

if __name__ == '__main__':
    app = indEXa_app(0)
    app.frame.Layout()

    # --- Se definen los BINDS --- #
    app.frame.Bind(wx.EVT_MENU, muestra_archivos_ocultos, app.frame.menubar.muestra_ocultos)
    app.frame.eBuscar.Bind(wx.EVT_SEARCH, iniciar_busqueda)
    app.frame.btnGestionar.Bind(wx.EVT_BUTTON, abrir_ventana_gestionar)
    app.frame.btnDuplicados.Bind(wx.EVT_BUTTON, buscar_duplicados)
    app.frame.Bind(wx.EVT_WINDOW_MODAL_DIALOG_CLOSED, al_cerrar_ventana_gestionar)
    app.frame.tArbol.GetMainWindow().Bind(wx.EVT_LEFT_UP, al_pulsar)
    app.frame.tArbol.Bind(wx.EVT_TREE_ITEM_EXPANDED, al_abrir)
    app.frame.lArbol.Bind(wx.EVT_LIST_ITEM_SELECTED, pulsa_en_item)
    app.frame.lArbol.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, boton_secundario_lArbol)
    app.frame.tArbol.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, boton_secundario_tArbol)
    app.frame.lUnidades.Bind(wx.EVT_LIST_ITEM_SELECTED, seleccion_unidades)
    app.frame.lUnidades.Bind(wx.EVT_RIGHT_DOWN, menu_lista_unidades)
    imagen_archivo = imagen_arbol("archivo")
    imagen_carpeta = imagen_arbol("carpeta")
    conector = inicia_db() #Se inicia la base de datos
    carga_tUnidades() #Y se cargan las unidades en la barra de la izquierda
    app.frame.SetTitle(nombre_app)
    app.frame.barraestado.SetStatusText("") #Por último, se vacía la barra de estado.
    app.MainLoop()
