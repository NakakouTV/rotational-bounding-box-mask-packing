from pathlib import Path
import sys,json
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'生成'))
from workspace_paths import IMAGES,RESULTS
from PIL import Image,ImageChops,ImageDraw
results=[]
contact=Image.new('RGB',(630,450),'white')
draw=ImageDraw.Draw(contact)
for number in range(1,32):
    image=Image.open(IMAGES/f'numbered-tile-{number}.png').convert('RGB')
    reference=Image.open(IMAGES/f'numbered-tile-reference-{number}.png').convert('RGB')
    # Right-hand sprite only; the left-hand character changes independently.
    crop=(290,130,390,230)
    tile=image.crop(crop);expected=reference.crop(crop)
    changed=sum(max(p)>2 for p in ImageChops.difference(tile,expected).get_flattened_data())
    missing=sum(min(a)>250 and min(b)<245 for a,b in zip(tile.get_flattened_data(),expected.get_flattened_data()))
    assert changed==0,(number,'differentPixels',changed)
    assert missing==0,(number,'missingPixels',missing)
    assert ImageChops.difference(image.crop((115,150,165,210)),Image.new('RGB',(50,60),'white')).getbbox(),(number,'left character was erased')
    x=((number-1)%7)*90;y=((number-1)//7)*90
    contact.paste(tile.crop((10,10,90,90)),(x+5,y+5))
    results.append(dict(number=number,differentPixels=changed,missingPixels=missing))
contact.save(IMAGES/'31番号付き画像確認.png')
(RESULTS/'numbered-tiles-pixel-check.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
print('31 numbered tiles match isolated references; both sprites remain displayed.')
