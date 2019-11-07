# utilities
repo per script vari

<b>KoD-Installer</b><br>
Un installer per kod, una volta installato si auto-avvia e scarica lo zip da github, mentre ti mostra la schermata di configurazione iniziale<br>

<b>newVer</b><br>
Tool interno (scritto per python 3) per pubblicare una nuova major release velocemente, procedura
  1) clona il repo e assicurati di essere su master
  2) modifica addon.xml cambiando la versione e inserendo le novità
  3) python newVer.py cartellaGit
  4) recati in cartellaGit e controlla, poi fai il push

<b>m3uToCommunity</b><br>
Tool per convertire una o più liste m3u in un file per canali community, basta spostare il file in una cartella contenente file .m3u ed esegure lo script.
Verrà creato un file chiamato canali.json, quando il nome coincide i link vengono accorpati (se 2 liste offrono rai1, apparirà un solo rai1 ma che al suo interno ha 2 link diretti).<br>
Questo file dovrà poi essere integrato seguendo la <a href="https://telegra.ph/Guida-Community-Channel-KoD-07-06">guida</a>
