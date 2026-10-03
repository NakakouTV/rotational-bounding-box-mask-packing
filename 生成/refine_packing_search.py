from workspace_paths import ROOT,ASSETS,RESULTS,PROJECTS,SAMPLES
import json
from pathlib import Path
from search_packing_combinations import search
rows=[]
for w,h,margin in [(8,4,2),(16,8,2),(16,8,3),(32,16,2),(32,16,3),(32,16,4)]:
    q=search(w,h,[0,0],[w-1,0],step=.1,margin_pixels=margin);q['factor']='finalCandidate';rows.append(q)
    print(f'Candidate {w}x{h}, margin {margin}: {q["count"]}',flush=True)
for aspect in [.5,.75,1,1.333333,2]:
    q=search(32,16,[0,0],[31,0],step=.25,aspect=aspect);q['factor']='aspect';rows.append(q)
    print(f'Aspect {aspect}: {q["count"]}',flush=True)
(RESULTS/'refined-combination-results.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
