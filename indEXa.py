#!/usr/bin/env python3
# -*- coding: UTF-8 -*-


#Icono por https://www.freepik.com/

import wx, sqlite3, math, os, sys, psutil, datetime
from pathlib import Path

import wx.lib.agw.hypertreelist as HTL
from wx.lib.embeddedimage import PyEmbeddedImage

if sys.platform=='win32':
    import win32api
    #Sólo en Windows. Se instala con pip install pypiwin32

nombre_app = "indEXa 0.33β"
metadatos = False


if metadatos:
    from tinytag import TinyTag
    import mimetypes

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

carpeta_win = PyEmbeddedImage(
    b'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAMAAAAoLQ9TAAAABGdBTUEAALGPC/xhBQAAACBj'
    b'SFJNAAB6JgAAgIQAAPoAAACA6AAAdTAAAOpgAAA6mAAAF3CculE8AAABv1BMVEUAAAD6twP2'
    b'tQP1sgb0sgf0sQnvrwj2tAP0sgjzsQvxsA3vrxD1swbzsgnxsA3qrBfqrhjzsQr+1mz+2G7/'
    b'yjnqqRvpqh3kpyTipSjhpSnhpCzhpCv2swX1sgX1sgf0sgjysAr0sgf0sgnysAvxsAzwrw/v'
    b'rhDvrhHurRLtrRPtrRXsrBXzsQrysAzxrw3wrw7wshf4zV7/5Jb/4pH/4o3/34f/3oH/3Hz/'
    b'23f+5aD/67H/6q3/6an/56T/5qD/5Zn/4o7/34P/3n//3Xv/23j/23X/2nH/2W3/12n/5Zr/'
    b'5JT/45H/4Yr/4If/3oD/3Xz/3Xn/2nL/2W7/2Gr/12f/1mP/4Yv/34T/3X3/3Hn/23b/2nP/'
    b'2nD/2Wz/12j/1mT/1WD/1Fv/4Ij/34X/34L/3n7/3Hr/3Hj/2Gz/12X/1WH/1F3/01j/0lT/'
    b'34b/2XD/12r/12b/1F7/01r/0lb/0VL/0E7/2Gv/0lf/z0r/zkf/23P/1V//1Fz/0VT/0VD/'
    b'z0v/zkj/zUT/zED/1mX/0lX/0VH/z03/zkn/zEH/yz3nqR3nqB7nqSDmpyHlpyLkpiPjpibi'
    b'pSjgpCv///98hD39AAAAHHRSTlMAX+7+/t8g3/7+3xD+/v7fX/7v799f3/7+/u5f1BZOrQAA'
    b'AAFiS0dElH9nShUAAAAHdElNRQfmAwYLKAOmA2fCAAAAAW9yTlQBz6J3mgAAANpJREFUGNNj'
    b'YEAHjEwysswsrGxwAXZZOXkOBU4ubpgAj6ISr7IKn6qauoamlja/AIO8jqCunr6BoZGxiamZ'
    b'uYUQg6WVtY2tnb2Do5Ozi6ubuweDp5e3g4+vo59/gGtgUHBIKIO3Q5hvuF9EZFR0TGxcfEIi'
    b'Q1hSckpqWnp0TEZcZlZ2Ti5DXgpIc35QQWFWUXFJaRmDn396VGBQeUhoUXFFaVllFUNaVHV+'
    b'Rlx8TW1OXX1DY1Mzg3B+hkcLUHNrW3tHU2eXCIOoWHdPb1//BPGJkyQkJ0tJMxAEADrdOlzH'
    b'l346AAAAJXRFWHRkYXRlOmNyZWF0ZQAyMDIyLTAzLTA2VDExOjQwOjAzKzAwOjAwE6MR0wAA'
    b'ACV0RVh0ZGF0ZTptb2RpZnkAMjAyMi0wMy0wNlQxMTo0MDowMyswMDowMGL+qW8AAAAASUVO'
    b'RK5CYII=')

#----------------------------------------------------------------------
carpeta_mac = PyEmbeddedImage(
    b'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAAXNSR0IArs4c6QAAAJBlWElm'
    b'TU0AKgAAAAgABgEGAAMAAAABAAIAAAESAAMAAAABAAEAAAEaAAUAAAABAAAAVgEbAAUAAAAB'
    b'AAAAXgEoAAMAAAABAAIAAIdpAAQAAAABAAAAZgAAAAAAAABIAAAAAQAAAEgAAAABAAOgAQAD'
    b'AAAAAQABAACgAgAEAAAAAQAAABCgAwAEAAAAAQAAABAAAAAAjw+h1QAAAAlwSFlzAAALEwAA'
    b'CxMBAJqcGAAAAgtpVFh0WE1MOmNvbS5hZG9iZS54bXAAAAAAADx4OnhtcG1ldGEgeG1sbnM6'
    b'eD0iYWRvYmU6bnM6bWV0YS8iIHg6eG1wdGs9IlhNUCBDb3JlIDUuNC4wIj4KICAgPHJkZjpS'
    b'REYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgt'
    b'bnMjIj4KICAgICAgPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIKICAgICAgICAgICAg'
    b'eG1sbnM6dGlmZj0iaHR0cDovL25zLmFkb2JlLmNvbS90aWZmLzEuMC8iPgogICAgICAgICA8'
    b'dGlmZjpPcmllbnRhdGlvbj4xPC90aWZmOk9yaWVudGF0aW9uPgogICAgICAgICA8dGlmZjpQ'
    b'aG90b21ldHJpY0ludGVycHJldGF0aW9uPjI8L3RpZmY6UGhvdG9tZXRyaWNJbnRlcnByZXRh'
    b'dGlvbj4KICAgICAgICAgPHRpZmY6UmVzb2x1dGlvblVuaXQ+MjwvdGlmZjpSZXNvbHV0aW9u'
    b'VW5pdD4KICAgICAgICAgPHRpZmY6Q29tcHJlc3Npb24+MTwvdGlmZjpDb21wcmVzc2lvbj4K'
    b'ICAgICAgPC9yZGY6RGVzY3JpcHRpb24+CiAgIDwvcmRmOlJERj4KPC94OnhtcG1ldGE+CqZd'
    b'9jAAAAHtSURBVDgRpZI/S11BEMVndvfeF5AEJE2wEITkS2hlaWnh5xDBNl1AP41VQEiaVOkC'
    b'qWy0ehIwaBoF/7y9u5vf2fBaA8m8d5nZnTlnzs6u2X+aH378flJmr3bNqzV+gwdrDX/388PR'
    b'7tb7v/H7wefz9m7jrU1UupvVZjZatcubG6uXZ9vHe9tfniPx/U8XLQWHwG2kcwsqdwvExZuF'
    b'wjIE81gs50BIB1SytDzdn6a7x2zjm3WbWrQnwFM1G/DgLROnSIyPeNnEvlTOWrGn6/lOijFQ'
    b'FOlIIwppBgIAPnEkCdBMvLq2LWmtGosQgZ1oGUmqQQbAv5MUxXwiBG4VP5BbKA+T6hqzCrlC'
    b'oEIYRugdr+QIYEbgTFd71FpjPapWBVhXxDy6XElemsi0RFiXO+AdcgEiRMKrpjGQZNMfukR2'
    b'oSTLBFpHiELgRTYQ9/kA1JXrGBpomsgOnIF3ZIEuUitKYTVEDWw5uE5KXb8lfAWUSuEFUqhz'
    b'jmx2AyRCtZYykelaO7MUkRNxQX2oXKo21FUkPId+z7p33lGXrVlInQYoIh1Tptq0tvrCNl5C'
    b'J4NI9740ATILzUKCpFSVEiPSh5XR0vzq+uuPX7ebjUrXaKmutfD6kMdh2eHJFnLEoDP7OpZk'
    b'l7z4JjGv+WZ8/2KL3yVaw1QrN60UAAAAAElFTkSuQmCC')

extraible_mac = PyEmbeddedImage(
    b'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAAAXNSR0IArs4c6QAAAJBlWElm'
    b'TU0AKgAAAAgABgEGAAMAAAABAAIAAAESAAMAAAABAAEAAAEaAAUAAAABAAAAVgEbAAUAAAAB'
    b'AAAAXgEoAAMAAAABAAIAAIdpAAQAAAABAAAAZgAAAAAAAACQAAAAAQAAAJAAAAABAAOgAQAD'
    b'AAAAAQABAACgAgAEAAAAAQAAACCgAwAEAAAAAQAAACAAAAAA9t4+QgAAAAlwSFlzAAAWJQAA'
    b'FiUBSVIk8AAAAgtpVFh0WE1MOmNvbS5hZG9iZS54bXAAAAAAADx4OnhtcG1ldGEgeG1sbnM6'
    b'eD0iYWRvYmU6bnM6bWV0YS8iIHg6eG1wdGs9IlhNUCBDb3JlIDUuNC4wIj4KICAgPHJkZjpS'
    b'REYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgt'
    b'bnMjIj4KICAgICAgPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIKICAgICAgICAgICAg'
    b'eG1sbnM6dGlmZj0iaHR0cDovL25zLmFkb2JlLmNvbS90aWZmLzEuMC8iPgogICAgICAgICA8'
    b'dGlmZjpPcmllbnRhdGlvbj4xPC90aWZmOk9yaWVudGF0aW9uPgogICAgICAgICA8dGlmZjpQ'
    b'aG90b21ldHJpY0ludGVycHJldGF0aW9uPjI8L3RpZmY6UGhvdG9tZXRyaWNJbnRlcnByZXRh'
    b'dGlvbj4KICAgICAgICAgPHRpZmY6UmVzb2x1dGlvblVuaXQ+MjwvdGlmZjpSZXNvbHV0aW9u'
    b'VW5pdD4KICAgICAgICAgPHRpZmY6Q29tcHJlc3Npb24+MTwvdGlmZjpDb21wcmVzc2lvbj4K'
    b'ICAgICAgPC9yZGY6RGVzY3JpcHRpb24+CiAgIDwvcmRmOlJERj4KPC94OnhtcG1ldGE+CqZd'
    b'9jAAAATcSURBVFgJrVfLbiNFFL39brttd6dtJ5MQCRKxg1mChkiAkIBd2CD+gOV8Ap/CHyA2'
    b'zAfALNAskNCM2AFK0IhMwiQIYjtO2v3inKouY2tmVumSy9VdXT733HNv3Wpbst4s3LLbTedT'
    b'3t+m1c2PK4zsvDdz4jYPOSjDh4eHr332+RdfW5a1Xdf1bY0reGABqj797ttvvnzw4MGfjU1F'
    b'YpUA553tnd37Bx9/+kmzqM3h7Z8ePboPwK/QcwO8SoDeuul4dADGsrsxkF4YmHW3Gmc3mZz8'
    b'M5F0ODqgDfQC/QUFVAiSNN2uqlKiwBfIdivD5sfEKoEZD9NtzDG/lqFdVYDr7UGcbElVt2ac'
    b'oKoBM47jO7gmgWUzBMjI2tvb64zHm5HUlVQVE7bFBszReLNLG8fHx3Mg02a9ysba3d0dRv0e'
    b'7FdKAYagtQ7MXr8vOzs7o8a48s4ooG7CsDfudLtSl2XrChCzE3Wl3++PYexXZRBfawSCrj/2'
    b'fR/CaAXMolZGYBLbDQIqsGyrBCzPdkeObSvv284BhpXYnm2/MgSWFwRpnhcSeG7rIaBDeZ5D'
    b'hXAI91/Yhpyww9DfXGQ3Ip2g/W2IEGRZJmG3s0lbDYl6LQSDeGOYL1AlsWfbDgExC2AjCdNX'
    b'KpBsxGlR5PC+/TpATGIn6ZAEjAJru8D2vCAtiwIBar8SEpPYnucyB5b1x4RAVcLBoK8I8Jho'
    b'PQTAJIH+YLDRhEAlIgmYjLR7URSXJQ8qlIKWDiIF1nwRu9frJbg1ClirCth+GCYVKhZO49YJ'
    b'EJPYYRDEDQHluGEi+/v7ke+6ARednDyT84sLRaKNs4BY5+cXioCHRKMto8xSgeHwTsrTnxXr'
    b'38tL1c2iNkfLsoW2jo6OzohrcsBOkmjouS62is6BlxnF3hCLr4lKvJetMHN0BYtMHkF//oSz'
    b'DmzEcZflWKlvFHCiaLBJ7xkCNp0H6lIb5K/RmkHfNDOE1/P8/p+dMarirxbU6jzoxTFPRIeL'
    b'jQJOksQjbhOSYKO3q3D62kCqJfo50FlkdNPXfKfUCBj4XD3WCFQ46cdUYI2Am45G+Izk9PQZ'
    b'fKBHirIC0OBLyDUZNFFDlSNmMGgK/K6WeLwbb21JMkpZDZXzRgF5fnbWKR1X7r3/gURdJCnf'
    b'hkiC5wKvOMIVDU5DaGrQc3xOJUz9sHD0Oo6jYu65nnJkNp/L0fEfcvH8oqMBdAgIUxfFoppO'
    b'JjKZzcV2fVksMllcX6MilpIjL/K8lILhoZ5goVTGvcobyFpiDUPIke67ePnwww6c6UqSbEgY'
    b'dmV2dS2T6QSHUsagKLtUQF1kWY78gxF1GNXyy5MncjWbqcf0elkPOKMnlCIkw7KtetkcYiSA'
    b'bPf9QI0o8fLOu/fU+wBJZvnCEFgeRuV0On16A4+vruZ4eczkrbt3tXf0DH1RgBxGfUbUag+p'
    b'5KPxFQWoGCVwPA8KhBJFEcpvX7LFQuYIwTVsTC+nT7FIkTAKFI8f//zwjR9e//29Dz96cz6/'
    b'0knUSFxiLOBdQXB6r0zovLAQEm5dGq6whn9A2BzE3UMYQoQh7ISYseX07Ex+fPj9b7SFCfXv'
    b'iInJTiIDdP5xYIYySZZlGtdtNHqM1y35G/0v9Ev0gsbZaAypKl100jW7wzzH1K2ayjMgUJ5r'
    b'dP4x4R/U6j8Osc4sO+rmLAAAAABJRU5ErkJggg==')

#----------------------------------------------------------------------
extraible_win = PyEmbeddedImage(
    b'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAMAAABEpIrGAAAABGdBTUEAALGPC/xhBQAAACBj'
    b'SFJNAAB6JgAAgIQAAPoAAACA6AAAdTAAAOpgAAA6mAAAF3CculE8AAAA1VBMVEUAAADX19nU'
    b'2dnU19fU1NfP1NTc3eDU1NTPz9Ta3N7Z297Pz8/Y2t3W2dzHz8/Hx8/W2NrHx8d6enqgoKCs'
    b'rKyvr6+tra3d3+Lh4+bc3uHa3d7h4uXg4uVFRUVGRkZ5eXk0NDQzMzN4eHiCgoI6Ojo5OTmK'
    b'iopBQUE5ZjkmxSYyZzJCQkKLi4uSkpJJSUlAtEB2+3YgryBKSkqXl5dSUlJRUVFHZ0cpoylC'
    b'bUJQUFCYmJicnJxZWVlYWFidnZ2fn59paWlhYWFiYmKwsLCurq6xsbH///83beHdAAAAF3RS'
    b'TlMAX19fXzDvMDDv7yDf7yAg3yDf/t/+38DzZXIAAAABYktHREYXuvntAAAAB3RJTUUH5gMG'
    b'CywapgQKBgAAAAFvck5UAc+id5oAAADQSURBVDjL7ZLHFoIwEEXtvWCPihoVxAZW7IUg/v8v'
    b'mUxEVNi40oX3TPIm591lfL4/H+GvoBcqgdc+WEVvVEPPfbiGXESiTh+LIw8SYbtPpupeAkpn'
    b'eJ8VRM8eiUIOhHzjQdPOJt/zILQwbuM2HZbYCXp3QOhKFFm6I7OVjyR3QegpitIfDBWbETsU'
    b'GmMQVE3TJtMZvefaGyoIi6Wur9YbnbGEgW1Llx0I+4ObIzvHwwmEs0EIMYlpsuBpsiTEKIBQ'
    b'vFickmU5G3tcy9/+ZL/DDUxqOdBRCymhAAAAJXRFWHRkYXRlOmNyZWF0ZQAyMDIyLTAzLTA2'
    b'VDExOjQ0OjI2KzAwOjAwClWZcwAAACV0RVh0ZGF0ZTptb2RpZnkAMjAyMi0wMy0wNlQxMTo0'
    b'NDoyNSswMDowMErgO1IAAAAASUVORK5CYII=')


def devuelve_tamano(tamano):
    tamano = int(tamano)
    if tamano == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(tamano, 1024)))
    p = math.pow(1024, i)
    s = round(tamano / p, 2)
    return "%s %s" % (s, size_name[i])

def iniciadb():
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


            instruccion_sql = """ CREATE INDEX IF NOT EXISTS ZSTORAGEITEM_ZPARENT_INDEX ON ZSTORAGEITEM (ZPARENT); """
            cursorObj.execute(instruccion_sql)

            instruccion_sql = """ CREATE INDEX IF NOT EXISTS ZSTORAGEITEM_ZPARTOFCATALOG_INDEX ON ZSTORAGEITEM (ZPARTOFCATALOG); """
            cursorObj.execute(instruccion_sql)

            instruccion_sql = """ CREATE INDEX IF NOT EXISTS ZSTORAGEITEM_ZENT_INDEX ON ZSTORAGEITEM (ZENT); """
            cursorObj.execute(instruccion_sql)

            instruccion_sql = "PRAGMA auto_vacuum = INCREMENTAL"
            cursorObj.execute(instruccion_sql)
            instruccion_sql = "VACUUM"
            cursorObj.execute(instruccion_sql)
            con.commit()
        

    return con

conector = iniciadb()


class NuevaUnidadDialog(wx.Dialog):
    def __init__(
            self, parent, id, title, size=wx.DefaultSize, pos=wx.DefaultPosition,
            style=wx.DEFAULT_DIALOG_STYLE, name='dialog'
            ):

        wx.Dialog.__init__(self)
        self.Create(parent, id, title, pos, size, style, name)


        sizer = wx.BoxSizer(wx.VERTICAL)

        label = wx.StaticText(self, -1, "Añadir nueva unidad")
        sizer.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        label.SetToolTip("Unidad a escanear. Puedes seleccionar una carpeta utilizando el primer ítem de la lista (Añadir ubicación...)")


        box = wx.BoxSizer(wx.HORIZONTAL)

        self.selUnidades = wx.ListCtrl(self, wx.ID_ANY, style=wx.LC_HRULES | wx.LC_REPORT | wx.LC_VRULES)
        self.selUnidades.AppendColumn("Unidades", format=wx.LIST_FORMAT_LEFT, width=-1)
        self.selUnidades.Bind(wx.EVT_LIST_ITEM_SELECTED, self.unidad_seleccionada)


        box.Add(self.selUnidades, 1, wx.ALIGN_CENTRE|wx.ALL, 5)

        sizer.Add(box, 0, wx.EXPAND|wx.ALL, 5)

        box = wx.BoxSizer(wx.HORIZONTAL)

        label = wx.StaticText(self, -1, "Nombre:")
        box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)

        self.etiquetaUnidad = wx.TextCtrl(self, -1, "", size=(80,-1))
        box.Add(self.etiquetaUnidad, 1, wx.ALIGN_CENTRE|wx.ALL, 5)
        self.etiquetaUnidad.SetToolTip("Escribe el nombre/etiqueta de la unidad seleccionada")


        sizer.Add(box, 0, wx.EXPAND|wx.ALL, 5)

        line = wx.StaticLine(self, -1, size=(20,-1), style=wx.LI_HORIZONTAL)
        sizer.Add(line, 0, wx.EXPAND|wx.RIGHT|wx.TOP, 5)
        
        self.chkunidades = wx.CheckBox(self, -1, "Mostrar todas las unidades")
        sizer.Add(self.chkunidades, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        self.chkunidades.Bind(wx.EVT_CHECKBOX, self.eventocheckbox)
        self.chkunidades.SetToolTip("Actívalo para mostrar unidades de sistema u ocultas")
        


        line2 = wx.StaticLine(self, -1, size=(20,-1), style=wx.LI_HORIZONTAL)
        sizer.Add(line2, 0, wx.EXPAND|wx.RIGHT|wx.TOP, 5)

        btnsizer = wx.StdDialogButtonSizer()



        self.btnAdd = wx.Button(self, wx.ID_APPLY, "Añadir")
        btnsizer.AddButton(self.btnAdd)
        self.btnAdd.Bind(wx.EVT_BUTTON, self.btnAnadir)


        btn = wx.Button(self, wx.ID_CANCEL)
        btnsizer.AddButton(btn)
        btnsizer.Realize()
        
        

        sizer.Add(btnsizer, 0, wx.ALL, 5)
        wx.Button.Disable(self.btnAdd)



        self.SetSizer(sizer)
        sizer.Fit(self)
        self.lista_unidades(False)
        
    def lista_unidades(self,todas):
        if todas:
            discos = psutil.disk_partitions(all=True)
        else:
            discos = psutil.disk_partitions(all=False)
            
        self.selUnidades.ClearAll()

        self.selUnidades.InsertColumn(0, "Unidades",width = 150)
        self.selUnidades.Append(("Añadir ubicación...",))
        
        self.selUnidades.SetItemData(0,0)
        for disco in discos:
            if (("rootfs" in disco[3]) or ("dontbrowse" in disco[3]) or ("fixed" in disco[3])) and not(todas):
                pass
            else:
                try:
                    espacio = psutil.disk_usage(disco[1])
                    usado = espacio[1]
                    self.selUnidades.Append((disco[1],))
                    self.selUnidades.SetItemData(self.selUnidades.GetItemCount()-1,usado)
                except:
                    pass

    def unidad_seleccionada(self, evt):
        ind = self.selUnidades.GetFirstSelected()
        if ind >=0:
            item = self.selUnidades.GetItem(ind,0)
            unidad = item.GetText()
            if unidad == "Añadir ubicación...":
                dlg = wx.DirDialog (None, "Selecciona una carpeta", "",wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)
                if dlg.ShowModal() == wx.ID_OK:
                    dirname = dlg.GetPath()
                    unidad = str(Path(dirname).name)
                    self.selUnidades.SetItemText(0,dirname)
                    self.etiquetaUnidad.Clear()
                    self.etiquetaUnidad.write(unidad)
                    wx.Button.Enable(self.btnAdd)
                else:
                    pass
                dlg.Destroy()
            else:
                wx.Button.Enable(self.btnAdd)
                self.etiquetaUnidad.Clear()
                if sys.platform=='win32':
                    etiquetawindows = win32api.GetVolumeInformation(unidad)[0]
                    if len(etiquetawindows)>0:
                        self.etiquetaUnidad.write(etiquetawindows)
                    else:
                        self.etiquetaUnidad.write(unidad)
                else:
                    self.etiquetaUnidad.write(str(Path(unidad).name))
            
    def btnAnadir(self, evt):
        ind = self.selUnidades.GetFirstSelected()
        if ind >=0 and self.etiquetaUnidad.GetLineText(0):
            item = self.selUnidades.GetItem(ind,0)
            ruta = item.GetText()
            ruta = Path(ruta).as_posix()
            tamano = psutil.disk_usage(ruta)
            unidad = self.etiquetaUnidad.GetLineText(0)
            self.add_to_db(ruta, unidad,tamano)
            self.Destroy()
            
    def eventocheckbox(self, evt):
        if self.chkunidades.GetValue():
            self.lista_unidades(True)
        else:
            self.lista_unidades(False)
        
            
    def tamano_carpeta(self, carpeta):
        cursorObj = conector.cursor()
        datos = (carpeta,)
        tamano_total = 0
        cursorObj.execute('SELECT * FROM ZSTORAGEITEM WHERE ZPARENT=?',datos)
        rows = cursorObj.fetchall()
        for row in rows:
            tipo = row[6]
            id_carpeta = row[0]
            if tipo == 1:
                tamano = self.tamano_carpeta(id_carpeta)
                datos_update = (tamano, id_carpeta,)
                cursorObj.execute('UPDATE ZSTORAGEITEM SET ZTOTALBYTES=? WHERE ZPK=?',datos_update)
            else:
                tamano = row[2]            
            tamano_total = tamano_total + tamano
        return tamano_total        
            
            
    def add_to_db(self, ruta, unidad,tamano):
        
        cursorObj = conector.cursor()
    
        max = 100
        dlg = wx.ProgressDialog("Añadiendo datos a la base de datos",
                               "Este proceso puede durar unos minutos",
                               maximum = max,
                               parent=self,
                               style = 0
                                | wx.PD_APP_MODAL
                                #| wx.PD_CAN_ABORT
                                #| wx.PD_CAN_SKIP
                                #| wx.PD_ELAPSED_TIME
                                #| wx.PD_ESTIMATED_TIME
                                #| wx.PD_REMAINING_TIME
                                | wx.PD_AUTO_HIDE
                                )
        try:

            todas_las_carpetas={}
            tamano_total = tamano[1]
            tamano_sumado = 0

            #OJO, eliminar la línea de abajo, que si no se borra la DB en cada ejecución
            #cursorObj.execute('DELETE FROM ZSTORAGEITEM')
            #cursorObj.execute('DELETE FROM ZTOTALES')
            cursorObj.execute('SELECT * FROM ZTOTALES WHERE ZPK=1')
            rows = cursorObj.fetchall()

            if rows:
                valor_id = rows[0][2]+1
            else:
                valor_id = 1

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


            for path in Path(ruta).rglob('*'):  
                ruta_corregida = path.parent.as_posix()
                size = 0
                size_int = 0
                try:
                    size = str(path.stat().st_size)
                    size_int = path.stat().st_size
                except:
                    pass
            
                valor_id += 1
                tamano_sumado = tamano_sumado+size_int
                #Si se actualizaran los valores en cada iteración el programa iría lento. Por eso se actualiza cada 50 búsquedas 
                if ((ficheros_analizados%50) == 0):
            
                    wx.Yield()
                    try:
                    
                        valor_porciento = int((tamano_sumado/tamano_total)*100)
                        cadena = "Procesando "+devuelve_tamano(tamano_sumado)+" de "+devuelve_tamano(tamano_total)+"\n"+str(ficheros_analizados)+" ficheros analizados."
                        #dlg.Update(0,path.name)            
                    
                        dlg.Update(valor_porciento, cadena)
                    except:
                        pass
            

                #Si se encuentra un archivo de música, se añaden los metadatos a la base de datos
                album = ""
                artista = ""
                titulo = ""
                if metadatos:    
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
                    if metadatos:
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
            cursorObj.execute('DELETE FROM ZTOTALES')
            cursorObj.execute('''INSERT INTO ZTOTALES(ZPK, ZNAME, ZITEMS) VALUES(?, ?, ?)''', datos)
        
            # --= Se terminan de añadir archivos =--
            # --= Ahora se añade lo que ocupa cada carpeta =--
            self.tamano_carpeta(valor_id_unidad)
        
            conector.commit()
            dlg.Destroy()
   
        except Exception as e: 
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            a = str(exc_type) + " " + str(fname) + " " + str(exc_tb.tb_lineno)
            wx.MessageBox(a, 'Warning', wx.OK | wx.CANCEL | wx.ICON_WARNING)
            dlg.Update(0,str(e))            
 
class Buscador(wx.Frame):
    def __init__(self, *args, **kwds):
        
        self.cursorObj = conector.cursor()
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.SetSize((800, 450))
        self.SetTitle(nombre_app)

        menubar = wx.MenuBar()
        
        fileMenu = wx.Menu()
        self.menuocultos = fileMenu.Append(-1, '&Mostrar archivos ocultos', 'Muestra archivos de sistema que suelen estar ocultos', kind=wx.ITEM_CHECK)
        menubar.Append(fileMenu, '&Opciones')
        self.Bind(wx.EVT_MENU, self.MuestraArchivosOcultos, self.menuocultos)
        
        self.SetMenuBar(menubar)

        self.barraestado = wx.StatusBar(self, style=wx.STB_SIZEGRIP | wx.STB_ELLIPSIZE_MIDDLE | wx.STB_SHOW_TIPS)
        self.SetStatusBar(self.barraestado)

        self.pPrincipal = wx.Panel(self, wx.ID_ANY)

        primerDivisior = wx.BoxSizer(wx.HORIZONTAL)

        dUnidades = wx.BoxSizer(wx.VERTICAL)
        primerDivisior.Add(dUnidades, 2, wx.EXPAND, 0)

        self.lUnidades = wx.ListCtrl(self.pPrincipal, wx.ID_ANY, style=wx.LC_HRULES | wx.LC_REPORT)
        
        self.lUnidades.AppendColumn("Unidades", format=wx.LIST_FORMAT_LEFT, width=-1)
        
        #sizer_1 = wx.BoxSizer(wx.HORIZONTAL)
        #dUnidades.Add(sizer_1, 1, wx.EXPAND, 0)
        
        self.eBuscar = wx.SearchCtrl(self.pPrincipal, wx.ID_ANY, "", style=wx.TE_PROCESS_ENTER)
        self.eBuscar.ShowCancelButton(True)
        self.eBuscar.Bind(wx.EVT_SEARCH, self.OnKeyDown)
        self.eBuscar.SetToolTip("Escribe el texto a buscar y pulsa Intro para iniciar la búsqueda.")
        
        sBotones = wx.BoxSizer(wx.HORIZONTAL)
        
        dUnidades.Add(self.eBuscar, 0, wx.ALL | wx.EXPAND, 6)
        
        dUnidades.Add(self.lUnidades, 1, wx.ALL | wx.EXPAND, 6)
        dUnidades.Add(sBotones, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 6)


        self.btnGestionar = wx.Button(self.pPrincipal, wx.ID_ANY, "Gestionar")
        sBotones.Add(self.btnGestionar, 1, wx.ALL | wx.EXPAND, 3)
        self.btnGestionar.Bind(wx.EVT_BUTTON, self.boton_modal)
        self.btnGestionar.SetToolTip("Muestra la herramienta para añadir unidades a la base de datos.")

        self.btnDuplicados = wx.Button(self.pPrincipal, wx.ID_ANY, "Duplicados")
        sBotones.Add(self.btnDuplicados, 1, wx.ALL | wx.EXPAND, 3)
        self.btnDuplicados.Bind(wx.EVT_BUTTON, self.buscar_duplicados)
        self.btnDuplicados.SetToolTip("Busca archivos duplicados mayores de 100 megas.")
        

        
        self.Bind(wx.EVT_WINDOW_MODAL_DIALOG_CLOSED, self.OnWindowModalDialogClosed)



        dArbol = wx.BoxSizer(wx.VERTICAL)
        primerDivisior.Add(dArbol,7, wx.EXPAND, 0)

        self.tArbol = HTL.HyperTreeList(self.pPrincipal, agwStyle=wx.TR_DEFAULT_STYLE | HTL.TR_ELLIPSIZE_LONG_ITEMS)
        
        colorfondo = wx.SystemSettings.GetColour(wx.SYS_COLOUR_LISTBOX)
        self.tArbol.SetBackgroundColour(colorfondo)
   
        

        #self.tArbol = wx.TreeCtrl(self.pPrincipal, wx.ID_ANY)
        dArbol.Add(self.tArbol, 1, wx.ALL | wx.EXPAND, 6)

        self.lArbol = wx.ListCtrl(self.pPrincipal, wx.ID_ANY, style=wx.LC_HRULES | wx.LC_REPORT | wx.LC_VRULES)
        self.lArbol.AppendColumn("Archivo", format=wx.LIST_FORMAT_LEFT, width=380)
        self.lArbol.AppendColumn("Tamaño", format=wx.LIST_FORMAT_LEFT, width=80)
        self.lArbol.AppendColumn("Unidad", format=wx.LIST_FORMAT_LEFT, width=90)
        self.lArbol.AppendColumn("Ruta", format=wx.LIST_FORMAT_LEFT, width=0)

        


        dArbol.Add(self.lArbol, 1, wx.ALL | wx.EXPAND, 6)
        self.lArbol.Show(False)





        
        #dArbol.Add(self.eBuscar, 0, wx.ALL | wx.EXPAND, 6 )




        il = wx.ImageList(16, 16)

        graficos_carpeta = {
            'win32': carpeta_win.GetBitmap(),
            'linux': wx.ArtProvider.GetBitmap(wx.ART_FOLDER, wx.ART_MENU, (16,16)),
            'darwin': carpeta_mac.GetBitmap()
            }
            
        carpeta = graficos_carpeta[sys.platform]
        self.fldropenidx = self.fldridx =il.Add(carpeta)
        imgarchivo = wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE, wx.ART_MENU, (16,16))
        self.fileidx = il.Add(imgarchivo)

        self.tArbol.SetImageList(il)
        self.il = il
        # create some columns
        self.tArbol.AddColumn("Nombre")
        self.tArbol.AddColumn("Tamaño")
        self.tArbol.SetMainColumn(0) # the one with the tree in it...
        self.tArbol.SetColumnWidth(0, 400)
  
  
        self.tArbol.GetMainWindow().Bind(wx.EVT_LEFT_UP, self.AlPulsar)
        self.tArbol.Bind(wx.EVT_TREE_ITEM_EXPANDED, self.AlAbrir)
        self.lArbol.Bind(wx.EVT_LIST_ITEM_SELECTED, self.pulsa_en_item)
        
        self.lUnidades.Bind(wx.EVT_LIST_ITEM_SELECTED, self.seleccion_unidades)
        self.lUnidades.Bind(wx.EVT_RIGHT_DOWN, self.renombra_lista)

        self.pPrincipal.SetSizer(primerDivisior)

        self.Layout()
        # end wxGlade
        #self.seleccion_arbol('WD Red')
        
        self.carga_tUnidades()
        
    def MuestraArchivosOcultos(self, event):
        self.tArbol.DeleteAllItems()
        ind = self.lUnidades.GetFirstSelected()
        if ind >=0:
            item = self.lUnidades.GetItem(ind,0)
            self.seleccion_arbol(item.GetText())

        
    def renombra_lista(self, event):
        ind = self.lUnidades.GetFirstSelected()
        if ind >=0:
            item = self.lUnidades.GetItem(ind,0)
            x = event.GetX()
            y = event.GetY()
            ind = self.lUnidades.HitTest((x, y))[0]
            if ind >=0:
                item = self.lUnidades.GetItemText(ind)
                self.popupmenu = wx.Menu()
                menuItemRenombrar = self.popupmenu.Append(1, 'Renombrar...')
                menuSeparador = self.popupmenu.Append(-1, "","",wx.ITEM_SEPARATOR)
                menuItemBorrar = self.popupmenu.Append(2, 'Borrar...')
            
                self.popupmenu.Bind(wx.EVT_MENU, self.renombra_unidades, menuItemRenombrar)
                self.popupmenu.Bind(wx.EVT_MENU, self.borra_unidades, menuItemBorrar)
            
                self.PopupMenu(self.popupmenu, event.GetPosition())
        



        
    def OnKeyDown(self,evt):
        self.lArbol.Show(True)
        
        self.tArbol.Show(False)
        self.lArbol.DeleteAllItems()
        self.lArbol.Append(("Buscando...",))
        self.lArbol.Append(("",))
        self.lArbol.Append(("Por favor, espera...",))
        
        self.pPrincipal.Layout()
        wx.Yield()
        
        valor_a_buscar = ("%"+evt.GetString()+"%",)
        self.cursorObj.execute('SELECT * FROM ZSTORAGEITEM WHERE ZNAME LIKE ?',valor_a_buscar)
        rows = self.cursorObj.fetchall()
        self.lArbol.DeleteAllItems()
        
        for row in rows:
            if row[11]:
                try:
                    valor_a_buscar = (row[9],)
                    self.cursorObj.execute('SELECT * FROM ZSTORAGEITEM WHERE ZPK=?',valor_a_buscar)
                    rows = self.cursorObj.fetchall()
                    unidad = rows[0][11]
                except:
                    unidad = ""
                
                datos = (row[11],devuelve_tamano(row[2]),unidad, row[10])
                self.lArbol.Append(datos)
        
        
        
        
        
        
    def boton_modal(self, evt):
        dlg = NuevaUnidadDialog(self, -1, "Añadir nueva unidad", size=(400, 200),
                         style=wx.DEFAULT_DIALOG_STYLE)
        dlg.ShowWindowModal()   
        
    def OnWindowModalDialogClosed(self, evt):
        dialog = evt.GetDialog()
        val = evt.GetReturnCode()
        try:
            btnTxt = { wx.ID_OK : "OK",
                       wx.ID_CANCEL: "Cancel" }[val]
        except KeyError:
            btnTxt = '<unknown>'
        self.carga_tUnidades()        


        dialog.Destroy()
        
    def buscar_duplicados(self, evt):
        self.lArbol.Show(True)
        
        self.tArbol.Show(False)
        self.lArbol.DeleteAllItems()
        self.lArbol.Append(("Buscando...",))
        self.lArbol.Append(("",))
        self.lArbol.Append(("Por favor, espera...",))
        
        self.pPrincipal.Layout()
        wx.Yield()
        self.cursorObj.execute("""
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
        rows = self.cursorObj.fetchall()
        self.lArbol.DeleteAllItems()
        
        for row in rows:
            valor_a_buscar = (row[4],)
            self.cursorObj.execute('SELECT * FROM ZSTORAGEITEM WHERE ZPK=?',valor_a_buscar)
            rows = self.cursorObj.fetchall()
            unidad = rows[0][11]
            datos = (row[3],devuelve_tamano(row[1]),unidad, row[2])
            self.lArbol.Append(datos)
        

    def seleccion_unidades(self, evt):
        ind = self.lUnidades.GetFirstSelected()
        if ind >=0:
            item = self.lUnidades.GetItem(ind,0)
            self.seleccion_arbol(item.GetText())
            self.eBuscar.SetValue("")
            
            
    def pulsa_en_item(self, evt):
        ind = self.lArbol.GetFirstSelected()
        if ind >=0:
            item = self.lArbol.GetItem(ind,3)
            
            texto = item.GetText().replace("/"," ▸ ")
            self.barraestado.SetStatusText(texto)
            

    def AlPulsar(self, evt):    
        try:
            pos = evt.GetPosition()
            item, flags, col = self.tArbol.HitTest(pos)
            self.extraer_datos_tvResultados(item)
        except:
            pass
        
    def AlAbrir(self, evt):
                
        
        item = evt.GetItem()
        self.extraer_datos_tvResultados(item)


    def seleccion_arbol(self,unidad):
        self.lArbol.Show(False)
        self.tArbol.Show(True)
        self.pPrincipal.Layout()
        self.tArbol.DeleteAllItems()
        self.root = self.tArbol.AddRoot(unidad)
        self.tArbol.SetPyData(self.root ,"Principal") 
        valor_a_buscar = (0,unidad,)
        self.cursorObj.execute('SELECT * FROM ZSTORAGEITEM WHERE ZENT=? AND ZNAME=?',valor_a_buscar)
        rows = self.cursorObj.fetchall()
        ruta=rows[0][0]
        fecha_creacion = rows[0][8]
        espacio_total = rows[0][2]
        espacio_usado = rows[0][3]
        try:
            fecha_creacion = datetime.datetime.fromtimestamp(fecha_creacion).strftime('%d-%m-%Y a las %H:%M:%S')
            porciento = str(round((espacio_usado/espacio_total)*100,2))
            texto = "Creado el " + fecha_creacion + ". Utilizados "+devuelve_tamano(espacio_usado)+ " de "+devuelve_tamano(espacio_total) + " (" +porciento+"%)"
        except:
            texto = "Utilizados "+devuelve_tamano(espacio_usado)+ " de "+devuelve_tamano(espacio_total)

        self.barraestado.SetStatusText(texto)
        start_path = os.path.expanduser(r"")
        start_dir_entries = self.lista_carpeta(ruta)
        self.new_folder(start_dir_entries,self.root)
        self.tArbol.Expand(self.root)
        

                        
    
    def carga_tUnidades(self):
        self.lUnidades.ClearAll()

        self._il = wx.ImageList(32, 32)


        graficos_extraible = {
            'win32': extraible_win.GetBitmap(),
            'linux': wx.ArtProvider.GetBitmap(wx.ART_HARDDISK, wx.ART_MENU, (32,32)),
            'darwin': extraible_mac.GetBitmap()
            }
        extraible = graficos_extraible[sys.platform]
        
        img_idx = self._il.Add(extraible)
        self.lUnidades.SetImageList(self._il, wx.IMAGE_LIST_SMALL)
        valores = []
        
        self.cursorObj.execute('SELECT * FROM ZSTORAGEITEM WHERE ZENT=0')
        rows = self.cursorObj.fetchall()
        
        self.lUnidades.InsertColumn(0, "Unidades",width = 150)

        for row in rows:  
            self.lUnidades.Append((row[11],))
            self.lUnidades.SetItemData(self.lUnidades.GetItemCount()-1,row[0]) 
            self.lUnidades.SetItemImage(self.lUnidades.GetItemCount() - 1, img_idx)

    def renombra_unidades(self, event):
        ind = self.lUnidades.GetFirstSelected()
        item = self.lUnidades.GetItem(ind,0)
        ZPK_item = self.lUnidades.GetItemData(ind)
        texto_item = item.GetText()
        r = wx.TextEntryDialog(None, 'Introduce el nuevo nombre', caption='Renombrar unidad',value=texto_item)
        if r.ShowModal() != wx.ID_OK:
            return
        datos_update = (r.GetValue(),ZPK_item,)
        self.cursorObj.execute('UPDATE ZSTORAGEITEM SET ZNAME=? WHERE ZPK=?',datos_update)
        conector.commit()
        self.carga_tUnidades()
        self.tArbol.DeleteAllItems()
        
    def borra_unidades(self, evt):
        r = wx.MessageDialog(None,'Atención. Te dispones a eliminar una unidad de la base de datos.\nEste proceso no se puede deshacer. ¿Quieres continuar?','¿Eliminar?',wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION).ShowModal()

        if r != wx.ID_YES:
            return
            
        ind = self.lUnidades.GetFirstSelected()
        if ind >=0:
            item = self.lUnidades.GetItemData(ind)
            valor = (item,)
            self.cursorObj.execute('DELETE FROM ZSTORAGEITEM WHERE ZPARTOFCATALOG=?',valor)
            self.cursorObj.execute('DELETE FROM ZSTORAGEITEM WHERE ZPK=?',valor)
            conector.commit()
            self.cursorObj.execute('VACUUM')
            conector.commit()
            
            self.carga_tUnidades()
            self.tArbol.DeleteAllItems()


    def lista_carpeta(self,ruta):
        valores = []
        valores2=[]
        valor_a_buscar = (ruta,)
        self.cursorObj.execute('SELECT * FROM ZSTORAGEITEM WHERE ZPARENT=?',valor_a_buscar)
        rows = self.cursorObj.fetchall()
        for row in rows:
            
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
            valores.append(fila)
        return valores



    def new_folder(self, directory_entries, parent_iid):
        for datos in directory_entries:
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
            MuestraOcultos = self.menuocultos.IsChecked()
            if (nombre[0:1]=='.' or nombre in prohibidas) and not(MuestraOcultos):  #Se usa para no mostrar archivos ocultos
                pass
            else:
                if (carpeta == 1):
                    subdir_iid = self.tArbol.AppendItem(parent_iid,nombre)
                    self.tArbol.SetItemText(subdir_iid, devuelve_tamano(tamano), 1)
                    self.tArbol.SetPyData(subdir_iid,(carpeta, subdir_iid,"FALSE",id))  
                    self.tArbol.SetItemImage(subdir_iid, self.fldridx, which = wx.TreeItemIcon_Normal)
                    self.tArbol.SetItemImage(subdir_iid, self.fldropenidx, which = wx.TreeItemIcon_Expanded)
                    self.tArbol.AppendItem(subdir_iid, "Cargando...")
                    colorletras = wx.SystemSettings.GetColour(wx.SYS_COLOUR_LISTBOXTEXT)
                    self.tArbol.SetItemTextColour(subdir_iid,colorletras)
                    #tvResultados.item(subdir_iid, tags=(subdir_iid,item_path))
                else:
                    item = self.tArbol.AppendItem(parent_iid,nombre)
                    self.tArbol.SetItemText(item, devuelve_tamano(tamano), 1)
                    self.tArbol.SetItemImage(item, self.fileidx, which = wx.TreeItemIcon_Normal)
                    self.tArbol.SetPyData(item,(carpeta,id,nombre,tamano,zparent,tipo,ruta_completa)) 
                    colorletras = wx.SystemSettings.GetColour(wx.SYS_COLOUR_LISTBOXTEXT)
                    self.tArbol.SetItemTextColour(item,colorletras)

    def devuelve_ubicacion(self, item):
        valor = (item,)
        self.cursorObj.execute('SELECT * FROM ZSTORAGEITEM WHERE ZPK=?',valor)
        rows = self.cursorObj.fetchall()
        
        return rows[0][10]

    def extraer_datos_tvResultados(self, item):
        valor = self.tArbol.GetPyData(item)
        if (valor!="Principal"):
            if (valor[0]==1):
                valor_ZPK = valor[3]  
            else:
                valor_ZPK = valor[1]            
            valor_a_buscar = (valor_ZPK,)
            self.cursorObj.execute('SELECT * FROM ZSTORAGEITEM WHERE ZPK=?',valor_a_buscar)
            rows = self.cursorObj.fetchall()
            rows = rows[0]
            texto = rows[10].replace("/"," ▸ ")
            self.barraestado.SetStatusText(texto)
        if (valor[0]==1) and (valor[2]=="FALSE"):
            idd = valor[1]
            self.tArbol.DeleteChildren(idd)
            ruta = valor[3]
            start_dir_entries = self.lista_carpeta(ruta)
            self.new_folder(start_dir_entries,idd)
            self.tArbol.SetPyData(idd,(valor[0],valor[1], "TRUE",valor[3])) 

            
        if (valor[0]==0):
            valor_ZPK = valor[1]            
            valor_a_buscar = (valor_ZPK,)
            self.cursorObj.execute('SELECT * FROM ZSTORAGEITEM WHERE ZPK=?',valor_a_buscar)
            rows = self.cursorObj.fetchall()
            rows = rows[0]

            


# end of class Buscador



class MyApp(wx.App):
    def OnInit(self):
        self.frame = Buscador(None, wx.ID_ANY, "")
        self.SetTopWindow(self.frame)
        self.frame.Centre()
        if os.path.exists('icono.ico'):
            ico = wx.Icon('icono.ico', wx.BITMAP_TYPE_ICO)
            self.frame.SetIcon(ico)
        self.frame.Show()
        return True

# end of class MyApp


if __name__ == "__main__":
    app = MyApp(0)
    app.MainLoop()
