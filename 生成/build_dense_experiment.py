from workspace_paths import ROOT,ASSETS,RESULTS,PROJECTS,SAMPLES
import json,math,hashlib,zipfile,argparse
from pathlib import Path
from scratch_list_renderer import configure_list_renderer

parser=argparse.ArgumentParser()
parser.add_argument('--rectangular',action='store_true')
parser.add_argument('--optimized',action='store_true')
args=parser.parse_args()
if args.optimized:
    row=max((q for q in json.loads((RESULTS/'refined-combination-results.json').read_text()) if q['factor']=='finalCandidate' and q['glyphTexturePixels']==28.16 and q['marginPixels']>=2),key=lambda q:(q['count'],-q['textureWidth']*q['textureHeight']))
    positions=row['positions'];count=len(positions);suffix='optimized'
    output=f'SVG文字パッキング{count}文字_{row["width"]}x{row["height"]}.sb3'
elif args.rectangular:
    row=next(q for q in json.loads((RESULTS/'rectangular-results.json').read_text()) if q['width']==32 and q['height']==16)
    positions=row['positions'];count=len(positions);suffix='rectangular'
    output=f'SVG文字パッキング{count}文字_32x16.sb3'
else:
    row=max(json.loads((RESULTS/'square-half-dimension-results.json').read_text()),key=lambda q:q['count'])
    positions=[dict(phi=a,radius=row['radius']) for a in row['angles']];count=row['count'];suffix='dense'
    output='SVG文字パッキング15文字.sb3'
W=row['width']; H=row['height']; L=row.get('hullLength',W-1); side=row['glyphTexturePixels']/row['textureScale']; scale=33/side
origin=row.get('hullCenter',[W/2,.5]);beta=math.radians(row.get('hullAngle',0))
glyphs=json.loads((ASSETS/'glyphs-expanded.json').read_text(encoding='utf-8-sig'))
chars='日本語文字画像表示実験大小上下左右天地山川森林水火木金土月星空海石田米車花'[:count]
assert len(chars)==count
costume_name=f'{count}文字 atlas'
parts=[]; items=[]
for i,(ch,pos) in enumerate(zip(chars,positions)):
    phi=pos['phi'];a=math.radians(phi)
    if 'cx' in pos:cx=pos['cx'];cy=-pos['cy']
    else:cx=pos['radius']*math.cos(2*a);cy=-pos['radius']*math.sin(2*a)
    g=glyphs[ch];k=side/max(g['w'],g['h'])
    sx=origin[0]+cx*math.cos(beta)+cy*math.sin(beta);sy=origin[1]+cx*math.sin(beta)-cy*math.cos(beta)
    rotation=phi+math.degrees(beta)
    parts.append(f'<g transform="translate({sx} {sy}) rotate({rotation}) scale({k}) translate({-g["x"]-g["w"]/2} {-g["y"]-g["h"]/2})"><path fill="#163d70" d="{g["d"]}"/></g>')
    items.append(dict(char=ch,index=i+1,phi=phi,direction=90-rotation,offsetX=scale*(cx*math.cos(a)-cy*math.sin(a)),offsetY=scale*(cx*math.sin(a)+cy*math.cos(a)),targetX=-160+(i%8)*45,targetY=45-(i//8)*90))
markers=''.join(f'<rect x="{max(0,x-.004)}" y="{max(0,y-.004)}" width=".008" height=".008" fill="#163d70"/>' for x,y in row.get('endpoints',[(x,0) for x in range(W)]))
svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">{markers}{"".join(parts)}</svg>'
(ASSETS/f'packed-font-{suffix}.svg').write_text(svg,encoding='utf-8')
config=dict(width=W,height=H,textureGlyphPixels=row['glyphTexturePixels'],scale=scale,chars=chars,items=items,output=output,origin=origin,endpoints=row.get('endpoints',[[0,0],[W-1,0]]),marginPixels=row.get('marginPixels',2))
(ASSETS/f'{suffix}-config.json').write_text(json.dumps(config,ensure_ascii=False,indent=2),encoding='utf-8')
# Use a fresh project rather than redistributing the original reference sample.
empty=b'<svg xmlns="http://www.w3.org/2000/svg" width="1" height="1"></svg>'
backdrop=b'<svg xmlns="http://www.w3.org/2000/svg" width="480" height="360"><rect width="480" height="360" fill="white"/></svg>'
backdrop_id=hashlib.md5(backdrop).hexdigest()
base=dict(variables={},lists={},broadcasts={},blocks={},comments={},sounds=[],currentCostume=0,volume=100)
stage=dict(base,isStage=True,name='Stage',costumes=[dict(name='背景',dataFormat='svg',assetId=backdrop_id,md5ext=backdrop_id+'.svg',bitmapResolution=1,rotationCenterX=240,rotationCenterY=180)],tempo=60,videoTransparency=50,videoState='on',textToSpeechLanguage=None)
sprite=dict(base,isStage=False,name='Sprite',costumes=[],layerOrder=1,draggable=False,rotationStyle='all around')
p=dict(targets=[stage,sprite],monitors=[],extensions=['pen'],meta={'semver':'3.0.0','vm':'5.0.300'})
asset=hashlib.md5(svg.encode()).hexdigest();emptyid=hashlib.md5(empty).hexdigest()
t=p['targets'][1];t.update(name=f'{count}文字パッキング',blocks={},sounds=[],comments={},currentCostume=0,x=0,y=0,size=100,direction=90,visible=False)
t['costumes']=[dict(name=costume_name,dataFormat='svg',assetId=asset,md5ext=asset+'.svg',bitmapResolution=1,rotationCenterX=origin[0],rotationCenterY=origin[1]),dict(name='none',dataFormat='svg',assetId=emptyid,md5ext=emptyid+'.svg',bitmapResolution=1,rotationCenterX=0,rotationCenterY=0)]
p['targets'][0]['sounds']=[];p['meta']={'semver':'3.0.0','agent':'Dense bounding box SVG font experiment'}
config['renderer']=configure_list_renderer(p,items,scale,costume_name)
(ASSETS/f'{suffix}-config.json').write_text(json.dumps(config,ensure_ascii=False,indent=2),encoding='utf-8')
with zipfile.ZipFile(PROJECTS/output,'w',zipfile.ZIP_DEFLATED) as z:
    z.writestr('project.json',json.dumps(p,ensure_ascii=False));z.writestr(asset+'.svg',svg);z.writestr(emptyid+'.svg',empty);z.writestr(p['targets'][0]['costumes'][0]['md5ext'],backdrop)
print(json.dumps({'width':W,'count':len(items),'chars':chars,'scale':scale},ensure_ascii=False))
