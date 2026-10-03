from workspace_paths import ROOT,ASSETS,RESULTS,PROJECTS,SAMPLES
"""Explore line-hull geometry and fully use each mask corner.

Keeps glyph raster quality, display size and clearances explicit. Results are
feasible configurations under square glyph bounds, not global upper bounds.
"""
import math,json,argparse,time
from pathlib import Path

def maximum_clique(adj):
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

def search(width,height,endpoint1,endpoint2,quality=28.16,display=33,margin_pixels=2,step=.5,placement='corner',aspect=1):
    texture=2**math.floor(math.log2(2048/math.ceil(max(width,height))))
    side=quality/texture;scale=display/side;margin=margin_pixels/scale
    glyph_w=side*min(1,aspect);glyph_h=side*min(1,1/aspect)
    dx=endpoint2[0]-endpoint1[0];dy=endpoint2[1]-endpoint1[1]
    length=math.hypot(dx,dy);beta=math.atan2(dy,dx)
    center=((endpoint1[0]+endpoint2[0]+1)/2,(endpoint1[1]+endpoint2[1]+1)/2)
    def accept(cx,cy,a):
        sx=center[0]+cx*math.cos(beta)-cy*math.sin(beta)
        sy=center[1]+cx*math.sin(beta)+cy*math.cos(beta)
        angle=a+beta;ex=(glyph_w*abs(math.cos(angle))+glyph_h*abs(math.sin(angle)))/2;ey=(glyph_w*abs(math.sin(angle))+glyph_h*abs(math.cos(angle)))/2
        if sx-ex<0 or sx+ex>width or sy-ey<0 or sy+ey>height:return False
        buffer=2/texture
        for x in range(max(0,math.floor(sx-ex-buffer)),min(math.ceil(width),math.ceil(sx+ex+buffer)+1)):
            for y in range(max(0,math.floor(sy-ey-buffer)),min(math.ceil(height),math.ceil(sy+ey+buffer)+1)):
                u=(x-sx)*math.cos(angle)+(y-sy)*math.sin(angle)
                v=-(x-sx)*math.sin(angle)+(y-sy)*math.cos(angle)
                if abs(u)<=glyph_w/2+buffer and abs(v)<=glyph_h/2+buffer:return False
        return True
    nodes=[]
    for i in range(1,round(90/step)):
        a=math.radians(i*step);c=math.cos(a);s=math.sin(a)
        hx=length/2*c;hy=length/2*s;px=glyph_w/2+margin;py=glyph_h/2+margin
        if hx<px or hy<py:continue
        if placement=='radial':
            maximum=length/2-max(px/c,py/s)
            chosen=None
            for ri in range(math.floor(maximum*2000/length),599,-1):
                r=ri*length/2000;cx=r*math.cos(2*a);cy=r*math.sin(2*a)
                if accept(cx,cy,a):chosen=(cx,cy);break
        else:
            # Place the upright glyph directly beside both mask edges, then
            # back off in texture-pixel steps only when a query point interferes.
            chosen=None;grid=1/texture
            for total in range(0,round(1.5/grid)+1):
                for ix in range(total+1):
                    iy=total-ix
                    x=hx-px-ix*grid;y=-hy+py+iy*grid
                    if abs(x)>hx-px or abs(y)>hy-py:continue
                    cx=x*c+y*s;cy=x*s-y*c
                    # Opposite mask corners are equivalent under central
                    # symmetry, but one can fit the atlas better than the other.
                    for sign in [1,-1]:
                        if accept(sign*cx,sign*cy,a):chosen=(sign*cx,sign*cy);break
                    if chosen:break
                if chosen:break
        if chosen:nodes.append(dict(phi=i*step,cx=chosen[0],cy=chosen[1]))
    def excludes(a,b):
        angle=math.radians(a['phi']);delta=math.radians(a['phi']-b['phi'])
        x=b['cx']*math.cos(angle)+b['cy']*math.sin(angle)
        y=b['cx']*math.sin(angle)-b['cy']*math.cos(angle)
        ex=(glyph_w*abs(math.cos(delta))+glyph_h*abs(math.sin(delta)))/2
        ey=(glyph_w*abs(math.sin(delta))+glyph_h*abs(math.cos(delta)))/2
        return max(abs(x)-ex-length/2*math.cos(angle),abs(y)-ey-length/2*math.sin(angle))>=margin-1e-10
    adj=[0]*len(nodes)
    for i,a in enumerate(nodes):
        for j in range(i):
            if excludes(a,nodes[j]) and excludes(nodes[j],a):adj[i]|=1<<j;adj[j]|=1<<i
    selected=maximum_clique(adj)
    positions=sorted([nodes[i] for i in selected],key=lambda q:q['phi'])
    return dict(width=width,height=height,endpoints=[endpoint1,endpoint2],hullLength=length,hullAngle=math.degrees(beta),hullCenter=center,textureScale=texture,textureWidth=width*texture,textureHeight=height*texture,glyphTexturePixels=quality,displayPixels=display,marginPixels=margin_pixels,scale=scale,stepDegrees=step,placement=placement,aspect=aspect,count=len(positions),positions=positions)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--fine',action='store_true');args=parser.parse_args()
    cases=[]
    if not args.fine:
        for w,h in [(4,2),(8,4),(16,8),(24,12),(32,16),(32,24),(32,32),(48,24),(64,32),(100,50)]:
            cases.append((w,h,[0,0],[w-1,0],'corner'))
        for w,h in [(16,16),(32,16),(32,32)]:
            for dy in [1,4,8,min(h-1,w-1)]:cases.append((w,h,[0,0],[w-1,dy],'corner'))
        cases.append((32,16,[0,0],[31,0],'radial'))
        step=.5;filename='combination-results.json'
    else:
        prior=json.loads((RESULTS/'combination-results.json').read_text())
        leaders=sorted(prior,key=lambda q:(q['count'],-q['textureWidth']*q['textureHeight']),reverse=True)[:3]
        cases=[(q['width'],q['height'],*q['endpoints'],q['placement']) for q in leaders]
        step=.1;filename='combination-fine-results.json'
    rows=[]
    for w,h,p1,p2,placement in cases:
        q=search(w,h,p1,p2,step=step,placement=placement);rows.append(q)
        print(f"{w}x{h}, hull {p1}->{p2}, {placement}, step {step}: {q['count']}",flush=True)
    (RESULTS/filename).write_text(json.dumps(rows,indent=2),encoding='utf-8')
