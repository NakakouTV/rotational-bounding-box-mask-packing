from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/"生成"))
from workspace_paths import ASSETS,RESULTS,IMAGES
from PIL import Image,ImageDraw,ImageChops
import json
out=Image.new('RGB',(400,210),'white');draw=ImageDraw.Draw(out);results=[]
for i,key in enumerate('123456789abcdef'):
    im=Image.open(IMAGES/('dense-'+key+'.png')).convert('RGB')
    bounds=ImageChops.difference(im,Image.new('RGB',im.size,'white')).getbbox()
    assert bounds is not None,key
    assert bounds[0]>=218 and bounds[1]>=158 and bounds[2]<=263 and bounds[3]<=203,(key,bounds)
    x=(i%5)*80;y=(i//5)*70
    out.paste(im.crop((210,150,270,210)),(x+15,y+10));draw.text((x+2,y+2),key,fill='black')
    results.append(dict(key=key,bounds=bounds))
out.save(IMAGES/'15文字単字確認.png')
open(RESULTS/'dense-pixel-check.json','w').write(json.dumps(results,indent=2))
print('15 single glyphs: all non-white pixels within selected glyph region')
