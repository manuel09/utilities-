import codecs
import os, sys
from xml.dom.minidom import parse

dep_blacklist = ['script.module.web-pdb']

os.chdir(sys.argv[1])

dom = parse('addon.xml')
version = dom.getElementsByTagName('addon')[0].getAttribute('version')
news = dom.getElementsByTagName('news')[0].childNodes[0]._get_wholeText()

# commit nuova versione su master
os.system('git add addon.xml')
os.system('git commit -m "S4Me ' + version + '"')
os.system('git push')

# fa il """merge"""
os.system('git checkout stable')
os.system('git rm -rf .')
os.system('git checkout master -- .')

# patch per il ramo stabile
dom = parse('addon.xml').getElementsByTagName('addon')[0]
dom.setAttribute('name', 'Stream4Me')
req = dom.getElementsByTagName('requires')[0]
for dip in req.getElementsByTagName('import'):
    if dip.getAttribute('addon') in dep_blacklist:
        dip.parentNode.removeChild(dip)
dom.writexml(codecs.open('addon.xml', 'wb', 'utf-8'))

updater = open('platformcode/updater.py', 'r+')
code = updater.read().replace("branch = 'master'", "branch = 'stable'")
updater.seek(0)
updater.write(code)
updater.close()

os.system('git add .')
newsStripped = ''
for n in news.split('\n'):
    newsStripped += n.strip() + '\\n'
commit = 'git commit -m "S4Me ' + version + '"' + ' -m "$(echo "' + newsStripped + '")"'
os.system(commit)

print('tutto pronto, fai un ultimo controllo e poi dai il push')
