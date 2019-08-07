# -*- coding: utf-8 -*-
from dependencies import platformtools
import downloader_service
if platformtools.dialog_yesno('Kodi on Demand', 'Attendi che il processo di installazione finisca.', 'Se il processo non è ancora iniziato puoi forzarlo premendo "SI"'):
    downloader_service.run()