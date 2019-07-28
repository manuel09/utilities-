import re, json, os


m3uLi = []
for file in os.listdir('.'):
    if file.split('.')[-1] == 'm3u':
        m3uLi.append(open(file).read())
regex = '#EXTINF:.*?(?:tvg-logo="([^"]+)")?,([^\n]+).*\n(.+)'
out = {
    "movies_list": []
}

for m3u in m3uLi:
    for logo, name, url in re.findall(regex, m3u):
        quality = 'HD' if 'hd' in name.lower() else 'SD'
        link = {
            "url": url,
            "quality": quality
        }

        for n, channel in enumerate(out["movies_list"]):
            if channel['title'] == name:  # esiste già
                out["movies_list"][n]["links"].append(link)
                break
        else:
            dictChannel = {
                "title": name,
                "year": "",
                "thumbnail": logo,
                "links": [
                    link
                ]
            }
            out["movies_list"].append(dictChannel)

json.dump(out, open('canali.json', 'w'), indent=4)
