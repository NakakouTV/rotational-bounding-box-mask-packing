"""Two packed SVG sprites: timed characters and slider-selected numbered tiles."""
import copy
import hashlib
import json
import math
import zipfile
from workspace_paths import ASSETS, PROJECTS
from scratch_list_renderer import configure_list_renderer

source = PROJECTS / 'SVG文字パッキング31文字_16x8.sb3'
output = 'SVGパッキング31文字と31画像_スライダーデモ.sb3'
config = json.loads((ASSETS / 'optimized-config.json').read_text(encoding='utf-8'))
numbers = json.loads((ASSETS / 'number-paths.json').read_text(encoding='utf-8-sig'))
with zipfile.ZipFile(source) as archive:
    assets = {name: archive.read(name) for name in archive.namelist() if name != 'project.json'}
    project = json.loads(archive.read('project.json'))
project['targets'] = project['targets'][:2]
tile = copy.deepcopy(project['targets'][1])
tile.update(name='31画像パッキング', layerOrder=2)
project['targets'].append(tile)

# Each tile uses the same square envelope as the placement search's glyphs.
# Artwork is expressed in a 100x100 design coordinate system, then packed at .22 SVG units.
side = config['textureGlyphPixels'] / 128
display_side = 66
tile_scale = display_side / side
groups, items = [], []
for index, original in enumerate(config['items'], 1):
    number = numbers[str(index)]
    fit = min(72 / number['w'], 52 / number['h'])
    content = ['<rect width="100" height="100" fill="#000000"/>']
    for y in range(6):
        for x in range(6):
            color = '#ffffff' if (x + y) % 2 == 0 else '#b9bdc3'
            content.append(f'<rect x="{5+x*15}" y="{5+y*15}" width="15" height="15" fill="{color}"/>')
    content.append(f'<g transform="translate(50 50) scale({fit}) translate({-number["x"]-number["w"]/2} {-number["y"]-number["h"]/2})"><path d="{number["d"]}" fill="#15283e" stroke="white" stroke-width="{3/fit}" stroke-linejoin="round" paint-order="stroke fill"/></g>')
    a = math.radians(original['phi'])
    # Recover the SVG center from the already validated screen-space offsets.
    cx = (original['offsetX'] * math.cos(a) + original['offsetY'] * math.sin(a)) / config['scale']
    cy = (-original['offsetX'] * math.sin(a) + original['offsetY'] * math.cos(a)) / config['scale']
    sx, sy = config['origin'][0] + cx, config['origin'][1] - cy
    groups.append(f'<g transform="translate({sx} {sy}) rotate({original["phi"]}) scale({side/100}) translate(-50 -50)">{"".join(content)}</g>')
    q = dict(original, char=str(index), offsetX=original['offsetX'] * tile_scale / config['scale'], offsetY=original['offsetY'] * tile_scale / config['scale'])
    items.append(q)
markers = ''.join(f'<rect x="{max(0,x-.004)}" y="{max(0,y-.004)}" width=".008" height=".008" fill="#263342"/>' for x,y in config['endpoints'])
svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="16" height="8" viewBox="0 0 16 8">{markers}{"".join(groups)}</svg>'
(ASSETS / 'packed-numbered-tiles.svg').write_text(svg, encoding='utf-8')
asset_id = hashlib.md5(svg.encode()).hexdigest()
assets[asset_id + '.svg'] = svg.encode()
tile['costumes'][0].update(name='31画像 atlas', assetId=asset_id, md5ext=asset_id+'.svg')
configure_list_renderer(project, config['items'], config['scale'], '31文字 atlas', demo=False)
configure_list_renderer(project, items, tile_scale, '31画像 atlas', target_index=2, demo=False)

# Stage owns the shared pen canvas. Redraw both sprites only on a change;
# otherwise the second sprite's stamp would be erased by the character demo.
stage = project['targets'][0]
stage.update(blocks={}, comments={}, variables={
    'demo_tile_number':['画像番号',1],
    'demo_character_number':['文字番号',1],
    'demo_previous_tile':['前回の画像番号',0],
    'demo_next_time':['次の文字の時刻',1],
}, broadcasts={'demo_draw':'描画'})
class Blocks:
    def __init__(self,target,prefix):self.target=target;self.blocks=target['blocks'];self.prefix=prefix;self.serial=0
    def make(self,opcode,inputs=None,fields=None,mutation=None):
        self.serial+=1;key=f'{self.prefix}_{self.serial}'
        node=dict(opcode=opcode,next=None,parent=None,inputs=inputs or {},fields=fields or {},shadow=False,topLevel=False)
        if mutation:node['mutation']=mutation
        self.blocks[key]=node
        for value in node['inputs'].values():
            if isinstance(value[1],str) and value[1] in self.blocks:self.blocks[value[1]]['parent']=key
        return key
    def chain(self,ids,top=False,x=30,y=30):
        for before,after in zip(ids,ids[1:]):self.blocks[before]['next']=after;self.blocks[after]['parent']=before
        if top:self.blocks[ids[0]].update(topLevel=True,x=x,y=y)
        return ids[0]
    def var(self,key):return self.make('data_variable',fields={'VARIABLE':[stage['variables'][key][0],key]})
    def set(self,key,value):return self.make('data_setvariableto',{'VALUE':value},{'VARIABLE':[stage['variables'][key][0],key]})
def number(value):return [1,[4,str(value)]]
def ref(key):return [2,key]
def report(key):return [3,key,[10,'']]
b=Blocks(stage,'stage_demo')
def time_passed():return b.make('operator_gt',{'OPERAND1':report(b.make('sensing_timer')),'OPERAND2':report(b.var('demo_next_time'))})
increment=b.make('data_changevariableby',{'VALUE':number(1)},{'VARIABLE':['文字番号','demo_character_number']})
past_end=b.make('operator_gt',{'OPERAND1':report(b.var('demo_character_number')),'OPERAND2':number(31)})
wrap=b.make('control_if',{'CONDITION':ref(past_end),'SUBSTACK':ref(b.set('demo_character_number',number(1)))})
next_time=b.make('operator_add',{'NUM1':report(b.make('sensing_timer')),'NUM2':number(1)})
tick=b.chain([increment,wrap,b.set('demo_next_time',report(next_time))])
update_character=b.make('control_if',{'CONDITION':ref(time_passed()),'SUBSTACK':ref(tick)})
same=b.make('operator_equals',{'OPERAND1':report(b.var('demo_tile_number')),'OPERAND2':report(b.var('demo_previous_tile'))})
changed=b.make('operator_not',{'OPERAND':ref(same)})
needs_update=b.make('operator_or',{'OPERAND1':ref(changed),'OPERAND2':ref(time_passed())})
body=b.chain([
    update_character,b.set('demo_previous_tile',report(b.var('demo_tile_number'))),b.make('pen_clear'),
    b.make('event_broadcastandwait',{'BROADCAST_INPUT':[1,[11,'描画','demo_draw']]}),
    b.make('control_wait_until',{'CONDITION':ref(needs_update)}),
])
loop=b.make('control_forever',{'SUBSTACK':ref(body)})
b.chain([b.make('event_whenflagclicked'),b.make('sensing_resettimer'),b.set('demo_character_number',number(1)),b.set('demo_next_time',number(1)),loop],True)

for target,variable,x in [(project['targets'][1],'demo_character_number',-100),(tile,'demo_tile_number',100)]:
    b=Blocks(target,'draw_demo')
    index=b.var(variable)
    item=b.make('data_itemoflist',{'INDEX':report(index)},{'LIST':['画像ID','atlas_ids']})
    template=next(node for node in target['blocks'].values() if node['opcode']=='procedures_prototype')
    mutation={key:value for key,value in template['mutation'].items() if key not in ['argumentnames','argumentdefaults']}
    call=b.make('procedures_call',{'image_id_argument':report(item),'image_x_argument':number(x),'image_y_argument':number(0)},mutation=mutation)
    b.chain([b.make('event_whenbroadcastreceived',fields={'BROADCAST_OPTION':['描画','demo_draw']}),b.make('looks_cleargraphiceffects'),call],True,650,30)

project['monitors']=[dict(id='demo_tile_number',mode='slider',opcode='data_variable',params={'VARIABLE':'画像番号'},spriteName=None,value=1,width=0,height=0,x=275,y=270,visible=True,sliderMin=1,sliderMax=31,isDiscrete=True)]
project['meta']['agent']='Bounding box SVG packing: characters and numbered checkerboard tiles'
with zipfile.ZipFile(PROJECTS/output,'w',zipfile.ZIP_DEFLATED) as archive:
    archive.writestr('project.json',json.dumps(project,ensure_ascii=False))
    for name,data in assets.items():archive.writestr(name,data)
tile_config=dict(config,items=items,scale=tile_scale,output=output,displaySide=display_side)
(ASSETS/'numbered-tiles-config.json').write_text(json.dumps(tile_config,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'sprites':2,'tiles':31,'displaySide':display_side,'output':output},ensure_ascii=False))
