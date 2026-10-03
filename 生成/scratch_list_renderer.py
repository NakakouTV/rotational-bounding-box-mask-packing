"""Reusable Scratch renderer: all per-image data lives in Scratch lists."""
import json


def configure_list_renderer(project,items,scale,costume_name,target_index=1,demo=True):
    target=project['targets'][target_index]
    blocks={};serial=0
    def b(op,inputs=None,fields=None,shadow=False,mutation=None):
        nonlocal serial
        serial+=1;key=f'list_renderer_{serial}'
        node=dict(opcode=op,next=None,parent=None,inputs=inputs or {},fields=fields or {},shadow=shadow,topLevel=False)
        if mutation is not None:node['mutation']=mutation
        blocks[key]=node
        for value in node['inputs'].values():
            if len(value)>1 and isinstance(value[1],str) and value[1] in blocks:blocks[value[1]]['parent']=key
        return key
    def num(value):return [1,[4,str(value)]]
    def text(value):return [1,[10,value]]
    def ref(key):return [2,key]
    def reporter(key):return [3,key,[10,'']]
    def chain(ids,top=False,x=30,y=30):
        for before,after in zip(ids,ids[1:]):blocks[before]['next']=after;blocks[after]['parent']=before
        if top:blocks[ids[0]].update(topLevel=True,x=x,y=y)
        return ids[0]
    list_specs=[
        ('atlas_ids','画像ID',[q['char'] for q in items]),
        ('atlas_x','描画X補正',[q['offsetX'] for q in items]),
        ('atlas_y','描画Y補正',[q['offsetY'] for q in items]),
        ('atlas_direction','描画方向',[q['direction'] for q in items]),
        ('atlas_size','描画サイズ',[q.get('size',scale*100) for q in items]),
        ('atlas_costume','描画コスチューム',[q.get('costume',costume_name) for q in items]),
    ]
    target['lists']={key:[name,values] for key,name,values in list_specs}
    target['variables']={'atlas_selected':['選択番号',0],'atlas_cycle':['表示番号',1]}
    names={key:name for key,name,_ in list_specs}
    def variable(key):return b('data_variable',fields={'VARIABLE':[target['variables'][key][0],key]})
    def setvar(key,value):return b('data_setvariableto',{'VALUE':value},{'VARIABLE':[target['variables'][key][0],key]})
    def item(key,index):return b('data_itemoflist',{'INDEX':index},{'LIST':[names[key],key]})
    def selected_item(key):return item(key,reporter(variable('atlas_selected')))
    def costume(value):return b('looks_switchcostumeto',{'COSTUME':value})
    argument_ids=['image_id_argument','image_x_argument','image_y_argument']
    argument_names=['画像ID','x','y']
    proccode='画像を描画 %s x %s y %s'
    mutation={'tagName':'mutation','children':[],'proccode':proccode,'argumentids':json.dumps(argument_ids),'warp':'true'}
    def argument(name,shadow=False):return b('argument_reporter_string_number',fields={'VALUE':[name,None]},shadow=shadow)
    prototype_mutation=dict(mutation,argumentnames=json.dumps(argument_names,ensure_ascii=False),argumentdefaults=json.dumps(['','','']))
    proto=b('procedures_prototype',{key:[1,argument(name,True)] for key,name in zip(argument_ids,argument_names)},shadow=True,mutation=prototype_mutation)
    definition=b('procedures_definition',{'custom_block':[1,proto]})
    find=b('data_itemnumoflist',{'ITEM':reporter(argument('画像ID'))},{'LIST':[names['atlas_ids'],'atlas_ids']})
    select=setvar('atlas_selected',reporter(find))
    valid=b('operator_gt',{'OPERAND1':reporter(variable('atlas_selected')),'OPERAND2':num(0)})
    divide=b('operator_divide',{'NUM1':num(1),'NUM2':num(0)})
    x=b('operator_subtract',{'NUM1':reporter(argument('x')),'NUM2':reporter(selected_item('atlas_x'))})
    y=b('operator_subtract',{'NUM1':reporter(argument('y')),'NUM2':reporter(selected_item('atlas_y'))})
    edge_menu=b('sensing_touchingobjectmenu',fields={'TOUCHINGOBJECTMENU':['_edge_',None]},shadow=True)
    touching_edge=b('sensing_touchingobject',{'TOUCHINGOBJECTMENU':[1,edge_menu]})
    # Evaluating edge contact computes the precise bounds even with an empty body.
    update_bounds=b('control_if',{'CONDITION':ref(touching_edge)})
    render_body=[
        b('looks_show'),costume(text('none')),
        b('looks_setsizeto',{'SIZE':reporter(divide)}),
        b('motion_gotoxy',{'X':reporter(x),'Y':reporter(y)}),
        b('motion_pointindirection',{'DIRECTION':reporter(selected_item('atlas_direction'))}),
        b('looks_setsizeto',{'SIZE':reporter(selected_item('atlas_size'))}),
        costume(reporter(selected_item('atlas_costume'))),update_bounds,b('pen_stamp'),b('looks_hide'),
    ]
    inside=chain(render_body)
    guard=b('control_if',{'CONDITION':ref(valid),'SUBSTACK':ref(inside)})
    chain([definition,select,guard],True,30,30)
    def call(image_id,x=0,y=0):
        return b('procedures_call',{argument_ids[0]:image_id,argument_ids[1]:num(x),argument_ids[2]:num(y)},mutation=dict(mutation))
    if demo:
        # A short, data-driven timed demo instead of one script per image.
        flag=b('event_whenflagclicked');loop=b('control_forever')
        current=item('atlas_ids',reporter(variable('atlas_cycle')))
        length=b('data_lengthoflist',fields={'LIST':[names['atlas_ids'],'atlas_ids']})
        past_end=b('operator_gt',{'OPERAND1':reporter(variable('atlas_cycle')),'OPERAND2':reporter(length)})
        reset=setvar('atlas_cycle',num(1))
        wrap=b('control_if',{'CONDITION':ref(past_end),'SUBSTACK':ref(reset)})
        loop_body=chain([b('pen_clear'),call(reporter(current)),b('control_wait',{'DURATION':num(1)}),
                         b('data_changevariableby',{'VALUE':num(1)},{'VARIABLE':['表示番号','atlas_cycle']}),wrap])
        blocks[loop]['inputs']={'SUBSTACK':ref(loop_body)};blocks[loop_body]['parent']=loop
        chain([flag,b('looks_cleargraphiceffects'),setvar('atlas_cycle',num(1)),loop],True,650,30)
    target.update(blocks=blocks,comments={})
    return {'procedure':proccode,'argumentIds':argument_ids,'lists':[name for _,name,_ in list_specs],'boundsTrigger':'touching-edge'}
