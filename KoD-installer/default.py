# -*- coding: utf-8 -*-
from dependencies import platformtools
import downloader_service, os, xbmc

if os.path.isfile(xbmc.translatePath("special://home/addons/") + "plugin.video.kod.update.zip"):
    dial = None
    while os.path.isfile(xbmc.translatePath("special://home/addons/") + "plugin.video.kod.update.zip"):
        if not dial:
            dial = platformtools.dialog_progress('Kodi on Demand', 'Attendi che il processo di installazione finisca.')
        xbmc.sleep(500)
        if dial.iscanceled():
            dial.close()
            exit(0)
    dial.close()
    xbmc.executebuiltin("XBMC.RunAddon(plugin.video.kod)")
else:
    downloader_service.run()
