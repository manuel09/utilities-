#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Fai partire lo script da konsole
    ti chiederà il percorso del file channels.json
    inseriscilo con lo / finale
    il file finale sarà: channels-redirect.json
    nel file sono mantenuti i codici assieme agli url
    Cosi si vedono subito quelli che hanno problemi e che tipo di problemi
"""
import json
import requests

def rqst(lst_urls):
    """
        url deve iniziare con http(s):'
        return : (esito, sito, url, code, reurl)
    """
    rslt_final = []

    for sito in lst_urls:
        rslt = {}
        try: 
            r = requests.head(sito, allow_redirects = True)
            if r.url.endswith('/'):
                r.url = r.url[:-1]
            if str(sito) != str(r.url):
                is_redirect = True
            else:
                is_redirect = False

            rslt['code'] = r.status_code
            rslt['url'] = str(sito)
            rslt['rdrcturl'] = str(r.url)
            rslt['isRedirect'] = is_redirect
            rslt['history'] = r.history
            
        except requests.exceptions.HTTPError as http_err:
            # 522 Server Error: Origin Connection Time-out for url: https://italiafilm.info/
            # Errore : 404 Client Error: NOT FOUND for url: http://httpbin.org/status/404
            rslt['code'] = r.status_code
            rslt['url'] = str(sito)
            rslt['http_err'] = http_err
            rslt['history'] = r.history
            
        except requests.exceptions.ConnectionError as conn_errr:
            # HTTPSConnectionPool(host='www.yahoo.minkia', port=443): Max retries
            # exceeded with url: /(Caused by NewConnectionError
            # ('<urllib3.connection.VerifiedHTTPSConnection object at 0x7f96f7506d50>:
            # Failed to establish a new connection: [Errno -2] Name or service not known',))                
            if '[Errno -2]' in str(conn_errr):
                # il sito non esiste!!!
                rslt['code'] = '-2'
                rslt['url'] = str(sito)
                rslt['http_err'] = 'unknown host'

            elif '[Errno 110]' in str(conn_errr):
                # nei casi in cui vogliamo raggiungere certi siti...
                rslt['code'] = '110'
                rslt['url'] = str(sito)
                rslt['http_err'] = 'Connection timed out'
                
            # Errno 10061 per s.o. win
            elif '[Errno 111]' in str(conn_errr) or 'Errno 10061' in str(conn_errr):
                # nei casi in cui vogliamo raggiungere certi siti...
                rslt['code'] = '111'
                rslt['url'] = str(sito)
                rslt['http_err'] = 'Connection refused'
                
            else:
                rslt['code'] = conn_errr
                rslt['url'] = str(sito)
                rslt['http_err'] = 'Connection refused'
##                    rslt['history'] = r.history
                
        except requests.exceptions.RequestException as other_err:
            rslt['code'] = other_err
            rslt['url'] = str(sito)
            rslt['history'] = r.history                

        rslt_final.append(rslt)

    return rslt_final 

def check(folder_file = ''):

    fileJson = 'channels.json'    

    with open(folder_file+fileJson) as f:
        data = json.load(f)
    print("DATA :%s" % data)
    risultato = {}
    
    for chann, host in sorted(data.items()):
        ris = []
        print("channel - host :%s - %s " % (chann, host))
        
        lst_host = []
        lst_host.append(host)
        
        rslt = rqst(lst_urls = lst_host)
        print("rslt :%s  " % (rslt))
        rslt = rslt[0]
        # tutto ok
        if rslt['code'] == 200 and rslt['isRedirect'] == False:
            risultato[chann] = host
        # redirect
        elif rslt['code'] == 200 and rslt['isRedirect'] == True: 
            risultato[chann] = str(rslt['code']) +' - '+ rslt['rdrcturl']
        # sito inesistente
        elif rslt['code'] == -2:
            risultato[chann] = 'Host Sconosciuto - '+ str(rslt['code']) +' - '+ host
        else:
            # altri tipi di errore
            risultato[chann] = str(rslt['code']) +' - '+ host

    fileJson_test = 'channels-redirect.json'
    # scrivo il file aggiornato
    with open(folder_file+fileJson_test, 'w') as f:
        data = json.dump(risultato, f, sort_keys=True, indent=4)
        print(data)

if __name__ == "__main__":

    folder_file = raw_input('Inserisci il percorso, con / finale, del file channels.json\nPer default lo script è considerato\nnella root di .kodi/addons/plugin.video.s4me/ premi Enter')
    check(folder_file)
