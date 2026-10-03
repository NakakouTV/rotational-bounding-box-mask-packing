from workspace_paths import ROOT,ASSETS,RESULTS,PROJECTS,SAMPLES
"""Exact maximum clique on a specified angular grid, for square glyph bounds.
This is a capacity calculation for the experiment's circular layout, not a
proof of an unrestricted SVG packing maximum.
"""
import math,json
from pathlib import Path

def calculate(side=.055,radius=.395,margin=2/600,step=.25,atlas_half_width=None,atlas_half_height=None,accept_angle=None):
    candidates=[]
    for i in range(1,round(90/step)):
        a=math.radians(i*step)
        atlas_extent=side/2*(abs(math.sin(a))+abs(math.cos(a)))
        fits=(atlas_half_width is None or abs(radius*math.cos(2*a))+atlas_extent<=atlas_half_width) and (atlas_half_height is None or abs(radius*math.sin(2*a))+atlas_extent<=atlas_half_height)
        if fits and (accept_angle is None or accept_angle(a,radius)) and (.5-radius)*min(math.sin(a),math.cos(a))-side/2 >= margin:
            candidates.append(a)
    def excludes(a,b):
        x=radius*math.cos(2*b-a); y=-radius*math.sin(2*b-a)
        extent=side/2*(abs(math.cos(a-b))+abs(math.sin(a-b)))
        return max(abs(x)-extent-.5*math.cos(a),abs(y)-extent-.5*math.sin(a))>=margin
    adj=[0]*len(candidates)
    for i,a in enumerate(candidates):
        for j in range(i):
            b=candidates[j]
            if excludes(a,b) and excludes(b,a):
                adj[i]|=1<<j;adj[j]|=1<<i
    best=[]
    def expand(chosen,p):
        nonlocal best
        if not p:
            if len(chosen)>len(best):best=chosen
            return
        # Greedy coloring gives an upper bound on remaining clique size.
        order=[]; bounds=[];remaining=p;color=0
        while remaining:
            color+=1;available=remaining
            while available:
                bit=available&-available;v=bit.bit_length()-1
                order.append(v);bounds.append(color)
                remaining&=~bit;available&=~bit;available&=~adj[v]
        for v,bound in zip(reversed(order),reversed(bounds)):
            if len(chosen)+bound<=len(best):return
            expand(chosen+[v],p&adj[v]);p&=~(1<<v)
    expand([], (1<<len(candidates))-1)
    return dict(side=side,radius=radius,margin=margin,stepDegrees=step,count=len(best),angles=sorted(round(math.degrees(candidates[i]),3) for i in best),textureGlyphPixels=side*1024)

if __name__=='__main__':
    rows=[]
    for px in [56.32,48,40,32,24,16,8]:
        side=px/1024
        rows.append(calculate(side=side))
    optimized=[]
    for px in [56.32,48,40,32,24,16,8]:
        scale=33*1024/px
        best=max((calculate(side=px/1024,radius=r/1000,margin=2/scale,step=.5) for r in range(300,496,5)),key=lambda q:q['count'])
        best['displayGlyphPixels']=33
        best['displayScale']=scale
        optimized.append(best)
    result={'model':'square glyphs; lower half atlas; fixed radius .395, 2px clearance at scale600 on .25 degree grid; optimized: 33px display glyphs, 2px clearance, radius .300 to .495 step .005 on .5 degree grid', 'rows':rows,'optimized':optimized}
    (RESULTS/'capacity-results.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))
