"""Fetch official pinned dependencies; never redistribute opaque Scratch bundles."""
from pathlib import Path
import hashlib,json,urllib.request
root=Path(__file__).resolve().parent
manifest=json.loads((root/'dependencies.json').read_text())
for name,entry in manifest.items():
    with urllib.request.urlopen(entry['url']) as response:data=response.read()
    if hashlib.sha256(data).hexdigest()!=entry['sha256']:raise RuntimeError('Checksum mismatch: '+name)
    (root/'ライブラリ').mkdir(exist_ok=True)
    (root/'ライブラリ'/f'{name}.js').write_bytes(data)
    print(name,entry['version'])
font_url='https://raw.githubusercontent.com/google/fonts/66a36c8c94b1a5d992ee4e7f392fccfe4945767c/ofl/notosansjp/NotoSansJP%5Bwght%5D.ttf'
font=root/'フォント/NotoSansJP.ttf'
if not font.exists():
    with urllib.request.urlopen(font_url) as response:data=response.read()
    if hashlib.sha256(data).hexdigest()!='c2f3b4d463500a2ddcd3849cded1fceeb9fd6d1c32e6cbecd568453ba50fc68f':
        raise RuntimeError('Font changed upstream; review its revision and checksum before continuing.')
    font.write_bytes(data)
print('Dependencies downloaded. Font license: フォント/OFL.txt')
