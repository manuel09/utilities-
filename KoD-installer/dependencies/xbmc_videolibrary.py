# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# XBMC Library Tools
# ------------------------------------------------------------

import os
import xbmc

import filetools
import config, logger
import platformtools


def set_content(content_type, silent=False):
    """
    Procedimiento para auto-configurar la videoteca de kodi con los valores por defecto
    @type content_type: str ('movie' o 'tvshow')
    @param content_type: tipo de contenido para configurar, series o peliculas
    """
    continuar = True
    msg_text = ""
    videolibrarypath = "special://profile/addon_data/plugin.video.kod/videolibrary"
    # videolibrarypath = config.get_setting("videolibrarypath")
    logger.info('video '+videolibrarypath)
    forced = config.get_setting('videolibrary_kodi_force')

    if content_type == 'movie':
        scraper = [config.get_localized_string(70093), config.get_localized_string(70096)]
        if forced:
            seleccion = 0 # tmdb
        else:
            seleccion = platformtools.dialog_select(config.get_localized_string(70094), scraper)


    # Instalar The Movie Database
        if seleccion == -1 or seleccion == 0:
            if not xbmc.getCondVisibility('System.HasAddon(metadata.themoviedb.org)'):
                if not silent:
                    # Preguntar si queremos instalar metadata.themoviedb.org
                    install = platformtools.dialog_yesno(config.get_localized_string(60046))
                else:
                    install = True

                if install:
                    try:
                        # Instalar metadata.themoviedb.org
                        xbmc.executebuiltin('xbmc.installaddon(metadata.themoviedb.org)', True)
                        logger.info("Instalado el Scraper de películas de TheMovieDB")
                    except:
                        pass

                continuar = (install and xbmc.getCondVisibility('System.HasAddon(metadata.themoviedb.org)'))
                if not continuar:
                    msg_text = config.get_localized_string(60047)

            if continuar:
                xbmc.executebuiltin('xbmc.addon.opensettings(metadata.themoviedb.org)', True)

        # Instalar Universal Movie Scraper
        elif seleccion == 1:
            if continuar and not xbmc.getCondVisibility('System.HasAddon(metadata.universal)'):
                continuar = False
                if not silent:
                    # Preguntar si queremos instalar metadata.universal
                    install = platformtools.dialog_yesno(config.get_localized_string(70095))
                else:
                    install = True

                if install:
                    try:
                        xbmc.executebuiltin('xbmc.installaddon(metadata.universal)', True)
                        if xbmc.getCondVisibility('System.HasAddon(metadata.universal)'):
                            continuar = True
                    except:
                        pass

                continuar = (install and continuar)
                if not continuar:
                    msg_text = config.get_localized_string(70097)
            if continuar:
                xbmc.executebuiltin('xbmc.addon.opensettings(metadata.universal)', True)

    else:  # SERIES
        scraper = [config.get_localized_string(70098), config.get_localized_string(70093)]
        if forced:
            seleccion = 0 # tvdb
        else:
            seleccion = platformtools.dialog_select(config.get_localized_string(70107), scraper)

        # Instalar The TVDB
        if seleccion == -1 or seleccion == 0:
            if not xbmc.getCondVisibility('System.HasAddon(metadata.tvdb.com)'):
                if not silent:
                    # Preguntar si queremos instalar metadata.tvdb.com
                    install = platformtools.dialog_yesno(config.get_localized_string(60048))
                else:
                    install = True

                if install:
                    try:
                        # Instalar metadata.tvdb.com
                        xbmc.executebuiltin('xbmc.installaddon(metadata.tvdb.com)', True)
                        logger.info("Instalado el Scraper de series de The TVDB")
                    except:
                        pass

                continuar = (install and xbmc.getCondVisibility('System.HasAddon(metadata.tvdb.com)'))
                if not continuar:
                    msg_text = config.get_localized_string(70099)
            if continuar:
                xbmc.executebuiltin('xbmc.addon.opensettings(metadata.tvdb.com)', True)

        # Instalar The Movie Database
        elif seleccion == 1:
            if continuar and not xbmc.getCondVisibility('System.HasAddon(metadata.tvshows.themoviedb.org)'):
                continuar = False
                if not silent:
                    # Preguntar si queremos instalar metadata.tvshows.themoviedb.org
                    install = platformtools.dialog_yesno(config.get_localized_string(70100))
                else:
                    install = True

                if install:
                    try:
                        # Instalar metadata.tvshows.themoviedb.org
                        xbmc.executebuiltin('xbmc.installaddon(metadata.tvshows.themoviedb.org)', True)
                        if xbmc.getCondVisibility('System.HasAddon(metadata.tvshows.themoviedb.org)'):
                            continuar = True
                    except:
                        pass

                continuar = (install and continuar)
                if not continuar:
                    msg_text = config.get_localized_string(60047)
            if continuar:
                xbmc.executebuiltin('xbmc.addon.opensettings(metadata.tvshows.themoviedb.org)', True)

    idPath = 0
    idParentPath = 0
    if continuar:
        continuar = False

        # Buscamos el idPath
        sql = 'SELECT MAX(idPath) FROM path'
        nun_records, records = execute_sql_kodi(sql)
        if nun_records == 1:
            idPath = records[0][0] + 1

        sql_videolibrarypath = videolibrarypath
        if sql_videolibrarypath.startswith("special://"):
            sql_videolibrarypath = sql_videolibrarypath.replace('/profile/', '/%/').replace('/home/userdata/', '/%/')
            sep = '/'
        elif sql_videolibrarypath.startswith("smb://"):
            sep = '/'
        else:
            sep = os.sep

        if not sql_videolibrarypath.endswith(sep):
            sql_videolibrarypath += sep

        # Buscamos el idParentPath
        sql = 'SELECT idPath, strPath FROM path where strPath LIKE "%s"' % sql_videolibrarypath
        nun_records, records = execute_sql_kodi(sql)
        if nun_records == 1:
            idParentPath = records[0][0]
            videolibrarypath = records[0][1][:-1]
            continuar = True
        else:
            # No existe videolibrarypath en la BD: la insertamos
            sql_videolibrarypath = videolibrarypath
            if not sql_videolibrarypath.endswith(sep):
                sql_videolibrarypath += sep

            sql = 'INSERT INTO path (idPath, strPath,  scanRecursive, useFolderNames, noUpdate, exclude) VALUES ' \
                  '(%s, "%s", 0, 0, 0, 0)' % (idPath, sql_videolibrarypath)
            nun_records, records = execute_sql_kodi(sql)
            if nun_records == 1:
                continuar = True
                idParentPath = idPath
                idPath += 1
            else:
                msg_text = config.get_localized_string(70101)

    if continuar:
        continuar = False

        # Fijamos strContent, strScraper, scanRecursive y strSettings
        if content_type == 'movie':
            strContent = 'movies'
            scanRecursive = 2147483647
            if seleccion == -1 or seleccion == 0:
                strScraper = 'metadata.themoviedb.org'
                path_settings = xbmc.translatePath("special://profile/addon_data/metadata.themoviedb.org/settings.xml")
            elif seleccion == 1: 
                strScraper = 'metadata.universal'
                path_settings = xbmc.translatePath("special://profile/addon_data/metadata.universal/settings.xml")
            settings_data = filetools.read(path_settings)
            strSettings = ' '.join(settings_data.split()).replace("> <", "><")
            strSettings = strSettings.replace("\"","\'")
            strActualizar = "¿Desea configurar este Scraper en español como opción por defecto para películas?"
            if not videolibrarypath.endswith(sep):
                videolibrarypath += sep
            strPath = videolibrarypath + config.get_setting("folder_movies") + sep
        else:
            strContent = 'tvshows'
            scanRecursive = 0
            if seleccion == -1 or seleccion == 0:
                strScraper = 'metadata.tvdb.com'
                path_settings = xbmc.translatePath("special://profile/addon_data/metadata.tvdb.com/settings.xml")
            elif seleccion == 1: 
                strScraper = 'metadata.tvshows.themoviedb.org'
                path_settings = xbmc.translatePath("special://profile/addon_data/metadata.tvshows.themoviedb.org/settings.xml")
            settings_data = filetools.read(path_settings)
            strSettings = ' '.join(settings_data.split()).replace("> <", "><")
            strSettings = strSettings.replace("\"","\'")
            strActualizar = "¿Desea configurar este Scraper en español como opción por defecto para series?"
            if not videolibrarypath.endswith(sep):
                videolibrarypath += sep
            strPath = videolibrarypath + config.get_setting("folder_tvshows") + sep

        logger.info("%s: %s" % (content_type, strPath))
        # Comprobamos si ya existe strPath en la BD para evitar duplicados
        sql = 'SELECT idPath FROM path where strPath="%s"' % strPath
        nun_records, records = execute_sql_kodi(sql)
        sql = ""
        if nun_records == 0:
            # Insertamos el scraper
            sql = 'INSERT INTO path (idPath, strPath, strContent, strScraper, scanRecursive, useFolderNames, ' \
                  'strSettings, noUpdate, exclude, idParentPath) VALUES (%s, "%s", "%s", "%s", %s, 0, ' \
                  '"%s", 0, 0, %s)' % (
                      idPath, strPath, strContent, strScraper, scanRecursive, strSettings, idParentPath)
        else:
            if not silent:
                # Preguntar si queremos configurar themoviedb.org como opcion por defecto
                actualizar = platformtools.dialog_yesno(config.get_localized_string(70098), strActualizar)
            else:
                actualizar = True

            if actualizar:
                # Actualizamos el scraper
                idPath = records[0][0]
                sql = 'UPDATE path SET strContent="%s", strScraper="%s", scanRecursive=%s, strSettings="%s" ' \
                      'WHERE idPath=%s' % (strContent, strScraper, scanRecursive, strSettings, idPath)

        if sql:
            nun_records, records = execute_sql_kodi(sql)
            if nun_records == 1:
                continuar = True

        if not continuar:
            msg_text = config.get_localized_string(60055)

    if not continuar:
        heading = config.get_localized_string(70102) % content_type
    elif content_type == 'SERIES' and not xbmc.getCondVisibility(
            'System.HasAddon(metadata.tvshows.themoviedb.org)'):
        heading = config.get_localized_string(70103) % content_type
        msg_text = config.get_localized_string(60058)
    else:
        heading = config.get_localized_string(70103) % content_type
        msg_text = config.get_localized_string(70104)
    platformtools.dialog_notification(heading, msg_text, icon=1, time=3000)

    logger.info("%s: %s" % (heading, msg_text))


def execute_sql_kodi(sql):
    """
    Ejecuta la consulta sql contra la base de datos de kodi
    @param sql: Consulta sql valida
    @type sql: str
    @return: Numero de registros modificados o devueltos por la consulta
    @rtype nun_records: int
    @return: lista con el resultado de la consulta
    @rtype records: list of tuples
    """
    logger.info()
    file_db = ""
    nun_records = 0
    records = None

    # Buscamos el archivo de la BBDD de videos segun la version de kodi
    video_db = config.get_platform(True)['video_db']
    if video_db:
        file_db = filetools.join(xbmc.translatePath("special://userdata/Database"), video_db)

    # metodo alternativo para localizar la BBDD
    if not file_db or not filetools.exists(file_db):
        file_db = ""
        for f in filetools.listdir(xbmc.translatePath("special://userdata/Database")):
            path_f = filetools.join(xbmc.translatePath("special://userdata/Database"), f)

            if filetools.isfile(path_f) and f.lower().startswith('myvideos') and f.lower().endswith('.db'):
                file_db = path_f
                break

    if file_db:
        logger.info("Archivo de BD: %s" % file_db)
        conn = None
        try:
            import sqlite3
            conn = sqlite3.connect(file_db)
            cursor = conn.cursor()

            logger.info("Ejecutando sql: %s" % sql)
            cursor.execute(sql)
            conn.commit()

            records = cursor.fetchall()
            if sql.lower().startswith("select"):
                nun_records = len(records)
                if nun_records == 1 and records[0][0] is None:
                    nun_records = 0
                    records = []
            else:
                nun_records = conn.total_changes

            conn.close()
            logger.info("Consulta ejecutada. Registros: %s" % nun_records)

        except:
            logger.error("Error al ejecutar la consulta sql")
            if conn:
                conn.close()

    else:
        logger.debug("Base de datos no encontrada")

    return nun_records, records


def add_sources(path):
    logger.info()
    from xml.dom import minidom

    SOURCES_PATH = xbmc.translatePath("special://userdata/sources.xml")

    if os.path.exists(SOURCES_PATH):
        xmldoc = minidom.parse(SOURCES_PATH)
    else:
        # Crear documento
        xmldoc = minidom.Document()
        nodo_sources = xmldoc.createElement("sources")

        for type in ['programs', 'video', 'music', 'picture', 'files']:
            nodo_type = xmldoc.createElement(type)
            element_default = xmldoc.createElement("default")
            element_default.setAttribute("pathversion", "1")
            nodo_type.appendChild(element_default)
            nodo_sources.appendChild(nodo_type)
        xmldoc.appendChild(nodo_sources)

    # Buscamos el nodo video
    nodo_video = xmldoc.childNodes[0].getElementsByTagName("video")[0]

    # Buscamos el path dentro de los nodos_path incluidos en el nodo_video
    nodos_paths = nodo_video.getElementsByTagName("path")
    list_path = [p.firstChild.data for p in nodos_paths]
    logger.debug(list_path)
    if path in list_path:
        logger.debug("La ruta %s ya esta en sources.xml" % path)
        return
    logger.debug("La ruta %s NO esta en sources.xml" % path)

    # Si llegamos aqui es por q el path no esta en sources.xml, asi q lo incluimos
    nodo_source = xmldoc.createElement("source")

    # Nodo <name>
    nodo_name = xmldoc.createElement("name")
    sep = os.sep
    if path.startswith("special://") or path.startswith("smb://"):
        sep = "/"
    name = path
    if path.endswith(sep):
        name = path[:-1]
    nodo_name.appendChild(xmldoc.createTextNode(name.rsplit(sep)[-1]))
    nodo_source.appendChild(nodo_name)

    # Nodo <path>
    nodo_path = xmldoc.createElement("path")
    nodo_path.setAttribute("pathversion", "1")
    nodo_path.appendChild(xmldoc.createTextNode(path))
    nodo_source.appendChild(nodo_path)

    # Nodo <allowsharing>
    nodo_allowsharing = xmldoc.createElement("allowsharing")
    nodo_allowsharing.appendChild(xmldoc.createTextNode('true'))
    nodo_source.appendChild(nodo_allowsharing)

    # Añadimos <source>  a <video>
    nodo_video.appendChild(nodo_source)

    # Guardamos los cambios
    filetools.write(SOURCES_PATH,
                    '\n'.join([x for x in xmldoc.toprettyxml().encode("utf-8").splitlines() if x.strip()]))


def ask_set_content(flag, silent=False):
    logger.info()
    logger.debug("videolibrary_kodi_flag %s" % config.get_setting("videolibrary_kodi_flag"))
    logger.debug("videolibrary_kodi %s" % config.get_setting("videolibrary_kodi"))

    def do_config():
        logger.debug("hemos aceptado")
        config.set_setting("videolibrary_kodi", True)
        set_content("movie", silent=True)
        set_content("tvshow", silent=True)
        add_sources("special://profile/addon_data/plugin.video.kod/videolibrary")
        add_sources("special://profile/addon_data/plugin.video.kod/downloads")

    if not silent:
        heading = config.get_localized_string(59971)
        linea1 = config.get_localized_string(70105)
        linea2 = config.get_localized_string(70106)
        if platformtools.dialog_yesno(heading, linea1, linea2):
            do_config()
        else:
            # no hemos aceptado
            config.set_setting("videolibrary_kodi", False)

    else:
        do_config()

    config.set_setting("videolibrary_kodi_flag", flag)
