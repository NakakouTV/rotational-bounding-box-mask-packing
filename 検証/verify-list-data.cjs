const workspace=require('./paths.cjs');
const {chromium}=require('playwright');
const fs=require('fs');
(async()=>{
const config=JSON.parse(fs.readFileSync(workspace.asset('optimized-config.json'),'utf8'));
const browser=await chromium.launch({...(process.env.CHROME_PATH?{executablePath:process.env.CHROME_PATH}:{}),headless:true,args:['--allow-file-access-from-files','--enable-unsafe-swiftshader']});
const page=await browser.newPage({viewport:{width:480,height:360},deviceScaleFactor:1});
await page.goto('file:///'+workspace.verify('verify-vm.html').replaceAll('\\','/'));
await page.evaluate(b=>window.run(b),fs.readFileSync(workspace.project(config.output)).toString('base64'));
await page.evaluate(()=>vm.stopAll());
// Test-only call, inserted into the running VM; it is never saved to the sb3.
await page.evaluate(()=>{
  const t=vm.runtime.targets[1],template=Object.values(t.blocks._blocks).find(b=>b.opcode==='procedures_call');
  const call={...structuredClone(template),id:'test_render_call',next:null,parent:null,topLevel:true,inputs:{}};
  for(const [name,opcode,field,value]of [['image_id_argument','text','TEXT','日'],['image_x_argument','math_number','NUM','0'],['image_y_argument','math_number','NUM','0']]){
    const id='test_'+name;t.blocks.createBlock({id,opcode,next:null,parent:call.id,inputs:{},fields:{[field]:{name:field,value}},shadow:true,topLevel:false});
    call.inputs[name]={name,block:id,shadow:id};
  }
  t.blocks.createBlock(call);
});
async function render(imageId,x=0,y=0){
  await page.evaluate(({imageId,x,y})=>{
    const t=vm.runtime.targets[1];
    for(const [name,field,value]of [['image_id_argument','TEXT',imageId],['image_x_argument','NUM',String(x)],['image_y_argument','NUM',String(y)]])
      t.blocks.changeBlock({id:'test_'+name,element:'field',name:field,value});
    vm.runtime._pushThread('test_render_call',t,{stackClick:true});
  },{imageId,x,y});
  await page.waitForTimeout(120);
}
const initial=await page.evaluate(()=>{
  const t=vm.runtime.targets[1],ids=['atlas_ids','atlas_x','atlas_y','atlas_direction','atlas_size','atlas_costume'];
  window.listSnapshot=Object.fromEntries(ids.map(id=>[id,[...t.lookupOrCreateList(id,'').value]]));
  return Object.fromEntries(ids.map(id=>[id,t.lookupOrCreateList(id,'').value.length]));
});
if(!Object.values(initial).every(n=>n===31))throw Error('Misaligned lists');
await render('日');
const before=await page.evaluate(()=>{const t=vm.runtime.targets[1];return{x:t.x,y:t.y,direction:t.direction,index:t.variables.atlas_selected.value}});
if(before.index!==1)throw Error('Incorrect first lookup');
// Swapping complete rows must keep rendering the same image while changing
// the selected index. Hardcoded coordinates could not pass this test.
await page.evaluate(()=>{const t=vm.runtime.targets[1];for(const id of Object.keys(window.listSnapshot)){const values=t.lookupOrCreateList(id,'').value;[values[0],values[1]]=[values[1],values[0]]}});
await render('日');
const swapped=await page.evaluate(()=>{const t=vm.runtime.targets[1];return{x:t.x,y:t.y,direction:t.direction,index:t.variables.atlas_selected.value}});
if(swapped.index!==2||swapped.x!==before.x||swapped.y!==before.y||swapped.direction!==before.direction)throw Error('Renderer did not follow reordered lists');
await page.evaluate(()=>{const t=vm.runtime.targets[1];t.lookupOrCreateList('atlas_x','').value[1]+=7;t.lookupOrCreateList('atlas_y','').value[1]-=5});
await render('日');
const changed=await page.evaluate(()=>{const t=vm.runtime.targets[1];return{x:t.x,y:t.y}});
if(Math.abs(changed.x-(before.x-7))>1e-6||Math.abs(changed.y-(before.y+5))>1e-6)throw Error('Position did not follow list values');
await page.evaluate(()=>{const t=vm.runtime.targets[1];for(const [id,values]of Object.entries(window.listSnapshot))t.lookupOrCreateList(id,'').value=[...values];t.lookupOrCreateList('atlas_ids','').value[0]='任意画像'});
await render('日');
const missing=await page.evaluate(()=>vm.runtime.targets[1].variables.atlas_selected.value);
if(missing!==0)throw Error('Unknown ID should not draw');
await render('任意画像');
const arbitrary=await page.evaluate(()=>{const t=vm.runtime.targets[1];return{index:t.variables.atlas_selected.value,threads:vm.runtime.threads.length}});
if(arbitrary.index!==1||arbitrary.threads!==0)throw Error('Arbitrary ID lookup failed');
await page.screenshot({path:workspace.image('リスト参照_任意ID確認.png')});
await page.evaluate(()=>{const t=vm.runtime.targets[1];for(const [id,values]of Object.entries(window.listSnapshot))t.lookupOrCreateList(id,'').value=[...values]});
await render('日',100,-50);
const placed=await page.evaluate(()=>{const t=vm.runtime.targets[1];return{x:t.x,y:t.y,index:t.variables.atlas_selected.value}});
if(Math.abs(placed.x-(before.x+100))>1e-6||Math.abs(placed.y-(before.y-50))>1e-6)throw Error('Custom block x/y placement failed');
await page.screenshot({path:workspace.image('リスト参照_XY指定確認.png')});
fs.writeFileSync(workspace.result('list-data-verification.json'),JSON.stringify({listLengths:initial,before,swapped,changed,unknownIndex:missing,arbitrary,placed},null,2));
console.log('Verified list alignment, ID search, row reordering, data edits, unknown IDs, arbitrary IDs, and custom x/y.');await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
