from workspace_paths import ROOT,ASSETS,RESULTS,PROJECTS,SAMPLES
import json,math
from pathlib import Path
from search_packing_combinations import search
rows=[]
cases=[]
for quality in [24,28.16,32,40]:cases.append(('quality',32,16,quality,2,.1))
for margin in [1,2,3,5]:cases.append(('margin',32,16,28.16,margin,.1))
for width in [7.99,8,8.01,15.99,16,16.01,31.99,32,32.01,63.99,64]:
    cases.append(('dimension',width,width/2,28.16,2,.25))
for step in [.5,.25,.1,.05]:cases.append(('angleStep',32,16,28.16,2,step))
for label,w,h,quality,margin,step in cases:
    q=search(w,h,[0,0],[math.ceil(w)-1,0],quality=quality,margin_pixels=margin,step=step)
    q['factor']=label;rows.append(q)
    print(f"{label} {w}x{h}, quality {quality}, margin {margin}, angleStep {step}: {q['count']}",flush=True)
(RESULTS/'factor-sweep-results.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
