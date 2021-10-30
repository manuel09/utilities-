# -*- coding: utf-8 -*-
import io
import xbmc, os, shutil, json
# functions that on kodi 19 moved to xbmcvfs
try:
    import xbmcvfs
    xbmc.translatePath = xbmcvfs.translatePath
    xbmc.validatePath = xbmcvfs.validatePath
    xbmc.makeLegalFilename = xbmcvfs.makeLegalFilename
except:
    pass
from dependencies import platformtools, logger, filetools
from dependencies import xbmc_videolibrary, config
from threading import Thread
try:
    import urllib.request as urllib
except ImportError:
    import urllib

branch = 'stable'
user = 'kodiondemand'
repo = 'addon'
addonDir = os.path.dirname(os.path.abspath(__file__)) + '/'
maxPage = 5  # le api restituiscono 30 commit per volta, quindi se si è rimasti troppo indietro c'è bisogno di andare avanti con le pagine
trackingFile = "last_commit.txt"


def chooseBranch():
    global branch
    apiLink = 'https://api.github.com/repos/' + user + '/' + repo + '/branches'
    try:
        branches = urllib.urlopen(apiLink).read()
    except Exception as e:
        platformtools.dialog_ok(config.get_localized_string(20000), config.get_localized_string(80031))
        logger.info(e)
        return False
    branches = json.loads(branches)
    chDesc = [config.get_localized_string(80034), config.get_localized_string(80035)]
    chDesc.extend([b['name'] for b in branches if b['name'] not in ['stable', 'master']])
    chName = ['stable', 'master']
    chName.extend([b['name'] for b in branches if b['name'] not in ['stable', 'master']])
    sel = platformtools.dialog_select(config.get_localized_string(80033), chDesc)
    if sel == -1:
        return False
    branch = chName[sel]
    return True


def updateFromZip(message=config.get_localized_string(80050)):
    dp = platformtools.dialog_progress_bg(config.get_localized_string(20000), message)
    dp.update(0)

    remotefilename = 'https://github.com/' + user + "/" + repo + "/archive/" + branch + ".zip"
    localfilename = filetools.join(xbmc.translatePath("special://home/addons/"), "plugin.video.kod.update.zip")
    destpathname = xbmc.translatePath("special://home/addons/")
    extractedDir = filetools.join(destpathname, "addon-" + branch)

    logger.info("remotefilename=%s" % remotefilename)
    logger.info("localfilename=%s" % localfilename)
    logger.info('extract dir: ' + extractedDir)

    # pulizia preliminare
    remove(localfilename)
    removeTree(extractedDir)

    try:
        urllib.urlretrieve(remotefilename, localfilename,
                           lambda nb, bs, fs, url=remotefilename: _pbhook(nb, bs, fs, url, dp))
    except Exception as e:
        platformtools.dialog_ok(config.get_localized_string(20000), config.get_localized_string(80031))
        logger.info('Non sono riuscito a scaricare il file zip')
        logger.info(e)
        dp.close()
        return False

    # Lo descomprime
    logger.info("decompressione...")
    logger.info("destpathname=%s" % destpathname)

    if os.path.isfile(localfilename):
        logger.info('il file esiste')

    dp.update(80, config.get_localized_string(20000), config.get_localized_string(80032))

    import zipfile
    try:
        hash = fixZipGetHash(localfilename)
        logger.info(hash)

        with zipfile.ZipFile(fOpen(localfilename, 'rb')) as zip:
            size = sum([zinfo.file_size for zinfo in zip.filelist])
            cur_size = 0
            for member in zip.infolist():
                zip.extract(member, destpathname)
                cur_size += member.file_size
                dp.update(int(80 + cur_size * 15 / size))

    except Exception as e:
        logger.info('Non sono riuscito ad estrarre il file zip')
        logger.error(e)
        import traceback
        logger.error(traceback.print_exc())
        dp.close()
        remove(localfilename)

        return False

    dp.update(95)

    # puliamo tutto
    global addonDir
    if extractedDir != addonDir:
        removeTree(addonDir)
    xbmc.sleep(1000)

    rename(extractedDir, 'plugin.video.kod')
    addonDir = filetools.join(destpathname, 'plugin.video.kod')

    logger.info("Cancellando il file zip...")
    remove(localfilename)

    dp.update(100)
    xbmc.sleep(1000)
    dp.close()
    xbmc.executebuiltin("UpdateLocalAddons")

    # in run()
    # refreshLang()

    return hash


def refreshLang():
    language = config.get_localized_string(20001)
    if language == 'eng':
        xbmc.executebuiltin("SetGUILanguage(resource.language.it_it)")
        xbmc.executebuiltin("SetGUILanguage(resource.language.en_en)")
    else:
        xbmc.executebuiltin("SetGUILanguage(resource.language.en_en)")
        xbmc.executebuiltin("SetGUILanguage(resource.language.it_it)")


def remove(file):
    if os.path.isfile(file):
        try:
            os.remove(file)
        except:
            logger.info('File ' + file + ' NON eliminato')


def onerror(func, path, exc_info):
    """
    Error handler for ``shutil.rmtree``.

    If the error is due to an access error (read only file)
    it attempts to add write permission and then retries.

    If the error is for another reason it re-raises the error.

    Usage : ``shutil.rmtree(path, onerror=onerror)``
    """
    import stat
    if not os.access(path, os.W_OK):
        # Is the error an access error ?
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        raise

def removeTree(dir):
    if os.path.isdir(dir):
        try:
            shutil.rmtree(dir, ignore_errors=False, onerror=onerror)
        except Exception as e:
            logger.info('Cartella ' + dir + ' NON eliminata')
            logger.error(e)


def rename(dir1, dir2):
    try:
        filetools.rename(dir1, dir2, silent=True, vfs=False)
    except:
        logger.info('cartella ' + dir1 + ' NON rinominata')


def fixZipGetHash(zipFile):
    hash = ''
    with fOpen(zipFile, 'r+b') as f:
        data = f.read()
        pos = data.find(b'\x50\x4b\x05\x06')  # End of central directory signature
        if pos > 0:
            f.seek(pos + 20)  # +20: see secion V.I in 'ZIP format' link above.
            hash = f.read()[2:]
            f.seek(pos + 20)
            f.truncate()
            f.write(
                b'\x00\x00')  # Zip file comment length: 0 byte length; tell zip applications to stop reading.

    return hash.decode('utf-8')

def _pbhook(numblocks, blocksize, filesize, url, dp):
    try:
        percent = min((numblocks*blocksize*80)/filesize, 80)
        dp.update(int(percent))
    except Exception as e:
        logger.error(e)
        percent = 80
        dp.update(percent)


def download():
    hash = updateFromZip()
    # se ha scaricato lo zip si trova di sicuro all'ultimo commit
    localCommitFile = fOpen(os.path.join(addonDir, trackingFile), 'wb')
    localCommitFile.write(hash.encode('utf-8'))
    localCommitFile.close()


def run():
    if chooseBranch():
        t = Thread(target=download)
        t.start()

        if not config.get_setting('show_once'):
            xbmc_videolibrary.ask_set_content(silent=False)
            config.set_setting('show_once', True)

        t.join()
        refreshLang()

        xbmc.executebuiltin("RunScript(special://home/addons/plugin.video.kod/service.py)")


def fOpen(file, mode = 'r'):
    # per android è necessario, su kodi 18, usare FileIO
    # https://forum.kodi.tv/showthread.php?tid=330124
    # per xbox invece, è necessario usare open perchè _io è rotto :(
    # https://github.com/jellyfin/jellyfin-kodi/issues/115#issuecomment-538811017
    if xbmc.getCondVisibility('system.platform.linux') and xbmc.getCondVisibility('system.platform.android'):
        logger.info('android, uso FileIO per leggere')
        return io.FileIO(file, mode)
    else:
        return open(file, mode)

if __name__ == "__main__":
    run()
