# -*- coding: utf-8 -*-
import io

import xbmc, os, shutil
from dependencies import platformtools, logger, filetools
from dependencies import xbmc_videolibrary, config
from threading import Thread

branch = 'stable'
user = 'kodiondemand'
repo = 'addon'
addonDir = os.path.dirname(os.path.abspath(__file__)) + '/'
maxPage = 5  # le api restituiscono 30 commit per volta, quindi se si è rimasti troppo indietro c'è bisogno di andare avanti con le pagine
trackingFile = "last_commit.txt"


def updateFromZip():
    dp = platformtools.dialog_progress_bg('Kodi on Demand', 'Installazione in corso...')
    dp.update(0)

    remotefilename = 'https://github.com/' + user + "/" + repo + "/archive/" + branch + ".zip"
    localfilename = (xbmc.translatePath("special://home/addons/") + "plugin.video.kod.update.zip").encode('utf-8')
    destpathname = xbmc.translatePath("special://home/addons/")

    logger.info("remotefilename=%s" % remotefilename)
    logger.info("localfilename=%s" % localfilename)

    # pulizia preliminare
    remove(localfilename)
    removeTree(destpathname + "addon-" + branch)

    import urllib
    urllib.urlretrieve(remotefilename, localfilename,
                       lambda nb, bs, fs, url=remotefilename: _pbhook(nb, bs, fs, url, dp))

    # Lo descomprime
    logger.info("decompressione...")
    logger.info("destpathname=%s" % destpathname)

    try:
        hash = fixZipGetHash(localfilename)
        import zipfile
        with zipfile.ZipFile(localfilename, "r") as zip_ref:
            zip_ref.extractall(destpathname)
    except Exception as e:
        logger.info('Non sono riuscito ad estrarre il file zip')
        logger.info(e)
        return False

    dp.update(95)

    # puliamo tutto
    removeTree(addonDir)

    rename(destpathname + "addon-" + branch, addonDir)

    logger.info("Cancellando il file zip...")
    remove(localfilename)

    dp.update(100)
    dp.close()
    xbmc.executebuiltin("UpdateLocalAddons")

    return hash


def remove(file):
    if os.path.isfile(file):
        removed = False
        while not removed:
            try:
                os.remove(file)
                removed = True
            except:
                logger.info('File ' + file + ' NON eliminato')


def removeTree(dir):
    if os.path.isdir(dir):
        removed = False
        while not removed:
            try:
                shutil.rmtree(dir)
                removed = True
            except:
                logger.info('Cartella ' + dir + ' NON eliminato')


def rename(dir1, dir2):
    renamed = False
    while not renamed:
        try:
            filetools.rename(dir1, dir2)
            renamed = True
        except:
            logger.info('cartella ' + dir1 + ' NON rinominata')


def fixZipGetHash(zipFile):
    f = io.FileIO(zipFile, 'r+b')
    data = f.read()
    pos = data.find(b'\x50\x4b\x05\x06')  # End of central directory signature
    hash = ''
    if pos > 0:
        f.seek(pos + 20)  # +20: see secion V.I in 'ZIP format' link above.
        hash = f.read()[2:]
        f.seek(pos + 20)
        f.truncate()
        f.write(
            b'\x00\x00')  # Zip file comment length: 0 byte length; tell zip applications to stop reading.
        f.seek(0)

    f.close()

    return str(hash)


def _pbhook(numblocks, blocksize, filesize, url, dp):
    try:
        percent = min((numblocks*blocksize*90)/filesize, 100)
        dp.update(percent)
    except:
        percent = 90
        dp.update(percent)


def download():
    hash = updateFromZip()
    # se ha scaricato lo zip si trova di sicuro all'ultimo commit
    localCommitFile = open(addonDir + trackingFile, 'w')
    localCommitFile.write(hash)
    localCommitFile.close()


def run():
    t = Thread(target=download)
    t.start()

    xbmc_videolibrary.ask_set_content(1, config.get_setting('videolibrary_kodi_force'))
    config.set_setting('show_once', True)

    t.join()


if __name__ == "__main__":
    run()
