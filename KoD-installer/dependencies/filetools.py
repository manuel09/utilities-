# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# filetools
# Gestion de archivos con discriminación samba/local
# ------------------------------------------------------------

import os
import traceback

from dependencies import platformtools, logger

try:
    from lib.sambatools import libsmb as samba
except:
    samba = None
    # Python 2.4 No compatible con modulo samba, hay que revisar

# Windows es "mbcs" linux, osx, android es "utf8"
if os.name == "nt":
    fs_encoding = ""
else:
    fs_encoding = "utf8"


def validate_path(path):
    """
    Elimina cáracteres no permitidos
    @param path: cadena a validar
    @type path: str
    @rtype: str
    @return: devuelve la cadena sin los caracteres no permitidos
    """
    chars = ":*?<>|"
    if path.lower().startswith("smb://"):
        import re
        parts = re.split(r'smb://(.+?)/(.+)', path)[1:3]
        return "smb://" + parts[0] + "/" + ''.join([c for c in parts[1] if c not in chars])

    else:
        if path.find(":\\") == 1:
            unidad = path[0:3]
            path = path[2:]
        else:
            unidad = ""

        return unidad + ''.join([c for c in path if c not in chars])


def encode(path, _samba=False):
    """
    Codifica una ruta según el sistema operativo que estemos utilizando.
    El argumento path tiene que estar codificado en utf-8
    @type path unicode o str con codificación utf-8
    @param path parámetro a codificar
    @type _samba bool
    @para _samba si la ruta es samba o no
    @rtype: str
    @return ruta codificada en juego de caracteres del sistema o utf-8 si samba
    """
    if not type(path) == unicode:
        path = unicode(path, "utf-8", "ignore")

    if path.lower().startswith("smb://") or _samba:
        path = path.encode("utf-8", "ignore")
    else:
        if fs_encoding:
            path = path.encode(fs_encoding, "ignore")

    return path


def rename(path, new_name):
    """
    Renombra un archivo o carpeta
    @param path: ruta del fichero o carpeta a renombrar
    @type path: str
    @param new_name: nuevo nombre
    @type new_name: str
    @rtype: bool
    @return: devuelve False en caso de error
    """
    path = encode(path)
    try:
        if path.lower().startswith("smb://"):
            new_name = encode(new_name, True)
            samba.rename(path, join(dirname(path), new_name))
        else:
            new_name = encode(new_name, False)
            os.rename(path, os.path.join(os.path.dirname(path), new_name))
    except:
        logger.error("ERROR al renombrar el archivo: %s" % path)
        logger.error(traceback.format_exc())
        platformtools.dialog_notification("Error al renombrar", path)
        return False
    else:
        return True

def remove(path):
    """
    Elimina un archivo
    @param path: ruta del fichero a eliminar
    @type path: str
    @rtype: bool
    @return: devuelve False en caso de error
    """
    path = encode(path)
    try:
        if path.lower().startswith("smb://"):
            samba.remove(path)
        else:
            os.remove(path)
    except:
        logger.error("ERROR al eliminar el archivo: %s" % path)
        logger.error(traceback.format_exc())
        platformtools.dialog_notification("Error al eliminar el archivo", path)
        return False
    else:
        return True

def join(*paths):
    """
    Junta varios directorios
    Corrige las barras "/" o "\" segun el sistema operativo y si es o no smaba
    @rytpe: str
    @return: la ruta concatenada
    """
    list_path = []
    if paths[0].startswith("/"):
        list_path.append("")

    for path in paths:
        if path:
            list_path += path.replace("\\", "/").strip("/").split("/")

    if list_path[0].lower() == "smb:":
        return "/".join(list_path)
    else:
        return os.sep.join(list_path)


def dirname(path):
    """
    Devuelve el directorio de una ruta
    @param path: ruta
    @type path: str
    @return: directorio de la ruta
    @rtype: str
    """
    return split(path)[0]


def split(path):
    """
    Devuelve una tupla formada por el directorio y el nombre del fichero de una ruta
    @param path: ruta
    @type path: str
    @return: (dirname, basename)
    @rtype: tuple
    """
    if path.lower().startswith("smb://"):
        if '/' not in path[6:]:
            path = path.replace("smb://", "smb:///", 1)
        return path.rsplit('/', 1)
    else:
        return os.path.split(path)


def write(path, data):
    """
    Guarda los datos en un archivo
    @param path: ruta del archivo a guardar
    @type path: str
    @param data: datos a guardar
    @type data: str
    @rtype: bool
    @return: devuelve True si se ha escrito correctamente o False si ha dado un error
    """
    path = encode(path)
    try:
        if path.lower().startswith("smb://"):
            f = samba.smb_open(path, "wb")
        else:
            f = open(path, "wb")

        f.write(data)
        f.close()
    except:
        logger.error("ERROR al guardar el archivo: %s" % path)
        logger.error(traceback.format_exc())
        return False
    else:
        return True


def read(path, linea_inicio=0, total_lineas=None):
    """
    Lee el contenido de un archivo y devuelve los datos
    @param path: ruta del fichero
    @type path: str
    @param linea_inicio: primera linea a leer del fichero
    @type linea_inicio: int positivo
    @param total_lineas: numero maximo de lineas a leer. Si es None o superior al total de lineas se leera el
        fichero hasta el final.
    @type total_lineas: int positivo
    @rtype: str
    @return: datos que contiene el fichero
    """
    path = encode(path)
    try:
        if path.lower().startswith("smb://"):
            f = samba.smb_open(path, "rb")
        else:
            f = open(path, "rb")

        data = []
        for x, line in enumerate(f):
            if x < linea_inicio: continue
            if len(data) == total_lineas: break
            data.append(line)
        f.close()
    except:
        logger.error("ERROR al leer el archivo: %s" % path)
        logger.error(traceback.format_exc())
        return False

    else:
        return "".join(data)


def decode(path):
    """
    Convierte una cadena de texto al juego de caracteres utf-8
    eliminando los caracteres que no estén permitidos en utf-8
    @type: str, unicode, list de str o unicode
    @param path: puede ser una ruta o un list() con varias rutas
    @rtype: str
    @return: ruta codificado en UTF-8
    """
    if type(path) == list:
        for x in range(len(path)):
            if not type(path[x]) == unicode:
                path[x] = path[x].decode(fs_encoding, "ignore")
            path[x] = path[x].encode("utf-8", "ignore")
    else:
        if not type(path) == unicode:
            path = path.decode(fs_encoding, "ignore")
        path = path.encode("utf-8", "ignore")
    return path


def listdir(path):
    """
    Lista un directorio
    @param path: Directorio a listar, debe ser un str "UTF-8"
    @type path: str
    @rtype: str
    @return: contenido de un directorio
    """

    path = encode(path)
    try:
        if path.lower().startswith("smb://"):
            return decode(samba.listdir(path))
        else:
            return decode(os.listdir(path))
    except:
        logger.error("ERROR al leer el directorio: %s" % path)
        logger.error(traceback.format_exc())
        return False


def isfile(path):
    """
    Comprueba si la ruta es un fichero
    @param path: ruta
    @type path: str
    @rtype: bool
    @return: Retorna True si la ruta existe y es un archivo
    """
    path = encode(path)
    try:
        if path.lower().startswith("smb://"):
            return samba.isfile(path)
        else:
            return os.path.isfile(path)
    except:
        logger.error("ERROR al comprobar el archivo: %s" % path)
        logger.error(traceback.format_exc())
        return False


def exists(path):
    """
    Comprueba si existe una carpeta o fichero
    @param path: ruta
    @type path: str
    @rtype: bool
    @return: Retorna True si la ruta existe, tanto si es una carpeta como un archivo
    """
    path = encode(path)
    try:
        if path.lower().startswith("smb://"):
            return samba.exists(path)
        else:
            return os.path.exists(path)
    except:
        logger.error("ERROR al comprobar la ruta: %s" % path)
        logger.error(traceback.format_exc())
        return False