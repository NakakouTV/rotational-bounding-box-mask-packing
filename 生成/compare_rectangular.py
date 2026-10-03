from workspace_paths import ROOT,ASSETS,RESULTS,PROJECTS,SAMPLES
"""Compare rectangular SVG atlases at equal glyph quality and display size.
The line hull is on the top row; glyphs occupy its lower circular arc.
"""
import math,json
from pathlib import Path
from calculate_capacity import calculate

GLYPH_PIXELS=28.16
DISPLAY_PIXELS=33

def geometry(width,height):
    texture_scale=2**math.floor(math.log2(2048/math.ceil(max(width,height))))
    n=math.ceil(width);length=n-1
    side=GLYPH_PIXELS/texture_scale
    scale=DISPLAY_PIXELS/side
    def accept(a,r):
        cx=n/2+r*length*math.cos(2*a);cy=.5+r*length*math.sin(2*a)
        e=side/2*(abs(math.sin(a))+abs(math.cos(a)))
        if cx-e<0 or cx+e>width or cy-e<0 or cy+e>height:return False
        buffer=2/texture_scale
        for x in range(max(0,math.floor(cx-e-buffer)),min(n,math.ceil(cx+e+buffer)+1)):
            for y in range(max(0,math.floor(cy-e-buffer)),min(math.ceil(height),math.ceil(cy+e+buffer)+1)):
                dx=x-cx;dy=y-cy
                u=dx*math.cos(a)+dy*math.sin(a);v=-dx*math.sin(a)+dy*math.cos(a)
                if abs(u)<=side/2+buffer and abs(v)<=side/2+buffer:return False
        return True
    return dict(texture_scale=texture_scale,n=n,length=length,side=side,scale=scale,accept=accept)

def clique(adj):
    best=[]
    def expand(chosen,p):
        nonlocal best
        if not p:
            if len(chosen)>len(best):best=chosen
            return
        order=[];bounds=[];remaining=p;color=0
        while remaining:
            color+=1;available=remaining
            while available:
                bit=available&-available;v=bit.bit_length()-1
                order.append(v);bounds.append(color)
                remaining&=~bit;available&=~bit;available&=~adj[v]
        for v,bound in zip(reversed(order),reversed(bounds)):
            if len(chosen)+bound<=len(best):return
            expand(chosen+[v],p&adj[v]);p&=~(1<<v)
    expand([],(1<<len(adj))-1)
    return best

def variable_radius(g):
    side=g['side']/g['length']; margin=2/g['scale']/g['length']
    nodes=[]
    for i in range(1,180):
        a=math.radians(i*.5)
        maximum=.5-(side/2+margin)/min(math.sin(a),math.cos(a))
        for ri in range(math.floor(maximum*2000),599,-1):
            radius=ri/2000
            if g['accept'](a,radius):
                nodes.append((a,radius));break
    def excludes(a,b):
        angle,radius=a; other,r=b
        x=r*math.cos(2*other-angle);y=-r*math.sin(2*other-angle)
        e=side/2*(abs(math.cos(angle-other))+abs(math.sin(angle-other)))
        return max(abs(x)-e-.5*math.cos(angle),abs(y)-e-.5*math.sin(angle))>=margin
    adj=[0]*len(nodes)
    for i,a in enumerate(nodes):
        for j in range(i):
            if excludes(a,nodes[j]) and excludes(nodes[j],a):adj[i]|=1<<j;adj[j]|=1<<i
    result=clique(adj)
    positions=[dict(phi=round(math.degrees(nodes[i][0]),4),radius=nodes[i][1]*g['length']) for i in result]
    positions.sort(key=lambda q:q['phi'])
    return positions

rows=[]
for width,height in [(4,4),(4,2),(8,8),(8,4),(16,16),(16,8),(32,32),(32,24),(32,16),(32,12),(32,8),(32,4),(48,24),(64,32),(100,50)]:
    g=geometry(width,height)
    fixed=max((calculate(side=g['side']/g['length'],radius=r/1000,margin=2/g['scale']/g['length'],step=.5,accept_angle=g['accept']) for r in range(300,496,5)),key=lambda q:q['count'])
    positions=variable_radius(g)
    row=dict(width=width,height=height,textureScale=g['texture_scale'],textureWidth=width*g['texture_scale'],textureHeight=height*g['texture_scale'],glyphTexturePixels=GLYPH_PIXELS,displayPixels=DISPLAY_PIXELS,scale=g['scale'],fixedCount=fixed['count'],fixedPositions=[dict(phi=a,radius=fixed['radius']*g['length']) for a in fixed['angles']],variableCount=len(positions),positions=positions)
    rows.append(row)
    print(f"{width}x{height}: fixed {fixed['count']}, variable {len(positions)}",flush=True)
(RESULTS/'rectangular-results.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
