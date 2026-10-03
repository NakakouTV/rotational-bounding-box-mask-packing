from workspace_paths import ROOT,ASSETS,RESULTS,PROJECTS,SAMPLES
import math,json
from pathlib import Path
from calculate_capacity import calculate

rows=[]
for width in [1.1,1.25,1.5,1.75,2,2.5,3,4,6,8]:
    # Hull points remain at pixel centers .5,1.5,...; fractional SVG widths
    # can therefore have a hull center different from their image center.
    n=math.ceil(width); length=n-1
    texture_scale=2**math.floor(math.log2(2048/math.ceil(width)))
    native_side=28.16/texture_scale
    # Symmetric conservative usable width around the hull's center n/2.
    half_width=min(n/2,width-n/2)/length
    best=max((calculate(side=native_side/length,radius=r/1000,margin=2*native_side/(33*length),step=.5,atlas_half_width=half_width,atlas_half_height=.5/length) for r in range(100,496,5)),key=lambda q:q['count'])
    rows.append(dict(width=width,height=1,hullLength=length,textureScale=texture_scale,glyphNativeSide=native_side,count=best['count'],normalizedRadius=best['radius'],angles=best['angles']))
(RESULTS/'half-dimension-results.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
print(json.dumps(rows,indent=2))

square_rows=[]
for width in [2,4,8,16,32,100]:
    height=width; length=width-1; tex=2**math.floor(math.log2(2048/width)); native=28.16/tex
    def accept(a,r):
        cx=width/2+r*length*math.cos(2*a);cy=.5+r*length*math.sin(2*a)
        e=native/2*(abs(math.sin(a))+abs(math.cos(a)))
        if cx-e<0 or cx+e>width or cy-e<0 or cy+e>height:return False
        # Avoid all integer silhouette query points by a 2-texel buffer.
        for x in range(max(0,math.floor(cx-e-2/tex)),min(width,math.ceil(cx+e+2/tex)+1)):
            for y in range(max(0,math.floor(cy-e-2/tex)),min(height,math.ceil(cy+e+2/tex)+1)):
                dx=x-cx;dy=y-cy
                u=dx*math.cos(a)+dy*math.sin(a)
                v=-dx*math.sin(a)+dy*math.cos(a)
                if abs(u)<=native/2+2/tex and abs(v)<=native/2+2/tex:return False
        return True
    best=max((calculate(side=native/length,radius=r/1000,margin=2*native/(33*length),step=.5,accept_angle=accept) for r in range(300,496,5)),key=lambda q:q['count'])
    unrestricted=max((calculate(side=native/length,radius=r/1000,margin=2*native/(33*length),step=.5) for r in range(300,496,5)),key=lambda q:q['count'])
    square_rows.append(dict(width=width,height=height,hullLength=length,textureScale=tex,glyphTexturePixels=28.16,count=best['count'],radius=best['radius']*length,angles=best['angles'],ignoringSamplePointsCount=unrestricted['count']))
(RESULTS/'square-half-dimension-results.json').write_text(json.dumps(square_rows,indent=2),encoding='utf-8')
print('Square SVG with line hull and sample-point avoidance:')
print(json.dumps(square_rows,indent=2))

