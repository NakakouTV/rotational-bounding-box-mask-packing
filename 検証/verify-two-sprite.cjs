const workspace=require('./paths.cjs');
const {chromium}=require('playwright');
const fs=require('fs');
(async()=>{
const config=JSON.parse(fs.readFileSync(workspace.asset('numbered-tiles-config.json'),'utf8'));
const svg=fs.readFileSync(workspace.asset('packed-numbered-tiles.svg'),'utf8');
const browser=await chromium.launch({...(process.env.CHROME_PATH?{executablePath:process.env.CHROME_PATH}:{}),headless:true,args:['--allow-file-access-from-files','--enable-unsafe-swiftshader']});
const page=await browser.newPage({viewport:{width:480,height:360},deviceScaleFactor:1});
page.on('pageerror',e=>{throw e;});
await page.goto('file:///'+workspace.verify('verify-vm.html').replaceAll('\\','/'));
await page.evaluate(b=>window.run(b),fs.readFileSync(workspace.project(config.output)).toString('base64'));
const monitor=await page.evaluate(()=>vm.runtime.getMonitorState().get('demo_tile_number').toJS());
if(monitor.mode!=='slider'||!monitor.visible||monitor.sliderMin!==1||monitor.sliderMax!==31||!monitor.isDiscrete)throw Error('Invalid slider '+JSON.stringify(monitor));
const results=[],seen=[];
async function state(){return page.evaluate(()=>{
  const stage=vm.runtime.targets[0],text=vm.runtime.targets[1],tile=vm.runtime.targets[2],d=vm.runtime.renderer._allDrawables[tile.drawableID];
  return {number:stage.variables.demo_tile_number.value,tileIndex:tile.variables.atlas_selected.value,textIndex:text.variables.atlas_selected.value,
    time:performance.now(),hull:d._convexHullPoints,textureWidth:d.skin._silhouette._width,textureHeight:d.skin._silhouette._height,
    tileX:tile.x,tileY:tile.y,tileDirection:tile.direction,visible:tile.visible};
});}
function remember(q){if(!seen.length||seen.at(-1).index!==q.textIndex)seen.push({index:q.textIndex,time:q.time});}
for(let number=1;number<=31;number++){
  // A Scratch slider writes this exact global variable; no test scripts are added.
  await page.evaluate(number=>{vm.runtime.targets[0].variables.demo_tile_number.value=number;},number);
  await page.waitForFunction(number=>vm.runtime.targets[2].variables.atlas_selected.value===number,number,{timeout:3000});
  await page.waitForTimeout(40);
  const q=await state();remember(q);
  if(q.tileIndex!==number||q.visible||JSON.stringify(q.hull)!==JSON.stringify(config.endpoints))throw Error('Incorrect tile '+JSON.stringify(q));
  results.push(q);
  await page.screenshot({path:workspace.image('numbered-tile-'+number+'.png')});
}
for(let i=0;i<340;i++){remember(await state());await page.waitForTimeout(100);}
if(new Set(seen.map(q=>q.index)).size!==31)throw Error('Missing timed character');
for(let i=1;i<seen.length;i++)if(seen[i].index!==seen[i-1].index%31+1)throw Error('Wrong text sequence');
if(!seen.some((q,i)=>i&&q.index===1&&seen[i-1].index===31))throw Error('Text did not loop');
await page.screenshot({path:workspace.image('2スプライトデモ.png')});
await page.evaluate(()=>vm.stopAll());
const reference=await browser.newPage({viewport:{width:480,height:360},deviceScaleFactor:1});
await reference.goto('file:///'+workspace.verify('verify-unmasked.html').replaceAll('\\','/'));
const variants=await reference.evaluate(svg=>{
  const doc=new DOMParser().parseFromString(svg,'image/svg+xml');
  return [...doc.documentElement.children].filter(x=>x.tagName==='g').map(g=>{
    const copy=doc.documentElement.cloneNode(false);copy.appendChild(g.cloneNode(true));return new XMLSerializer().serializeToString(copy);
  });
},svg);
for(let i=0;i<31;i++){
  const item={...config.items[i],offsetX:config.items[i].offsetX-100};
  await reference.evaluate(q=>window.reference(q.svg,q.origin,q.item,q.scale),{svg:variants[i],origin:config.origin,item,scale:config.scale});
  await reference.screenshot({path:workspace.image('numbered-tile-reference-'+(i+1)+'.png')});
  await reference.evaluate(()=>window.clean());
}
fs.writeFileSync(workspace.result('two-sprite-verification.json'),JSON.stringify({monitor,tiles:results,characters:seen},null,2));
await browser.close();console.log('Verified slider range, all 31 numbered tiles, line hull, and the independent character loop; created isolated references.');
})().catch(e=>{console.error(e);process.exit(1)});
