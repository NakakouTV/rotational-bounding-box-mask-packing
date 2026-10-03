from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/"生成"))
from workspace_paths import ASSETS,RESULTS,IMAGES
from PIL import Image,ImageDraw,ImageChops
import json
config=json.load(open(ASSETS/'optimized-config.json',encoding='utf-8'))
keys='123456789abcdefghijklmnopqrstuvwxyz'[:len(config['items'])]
out=Image.new('RGB',(560,350),'white');draw=ImageDraw.Draw(out);results=[]
for i,key in enumerate(keys):
    im=Image.open(IMAGES/('optimized-'+key+'.png')).convert('RGB')
    bounds=ImageChops.difference(im,Image.new('RGB',im.size,'white')).getbbox()
    assert bounds is not None,key
    assert bounds[0]>=218 and bounds[1]>=158 and bounds[2]<=263 and bounds[3]<=203,(key,bounds)
    reference=Image.open(IMAGES/('unmasked-'+str(i+1)+'.png')).convert('RGB')
    # Same source paths, scale, texture resolution and position. Compare all
    # pixels against a normally displayed isolated glyph without mask clipping.
    diff=ImageChops.difference(im,reference)
    changed=sum(1 for pixel in diff.get_flattened_data() if max(pixel)>2)
    missing=sum(1 for a,b in zip(im.get_flattened_data(),reference.get_flattened_data()) if min(a)>250 and min(b)<245)
    assert missing==0,(key,'missing pixels',missing)
    assert changed==0,(key,'different pixels',changed)
    x=(i%7)*80;y=(i//7)*70
    out.paste(im.crop((210,150,270,210)),(x+15,y+10));draw.text((x+2,y+2),key,fill='black')
    results.append(dict(key=key,char=config['items'][i]['char'],bounds=bounds,differentPixels=changed,missingPixels=missing))
out.save(IMAGES/'16x8_31文字確認.png')
open(RESULTS/'optimized-pixel-check.json','w',encoding='utf-8').write(json.dumps(results,ensure_ascii=False,indent=2))
print(f"{len(results)} glyphs: no extra or missing pixels; match unmasked isolated references")
