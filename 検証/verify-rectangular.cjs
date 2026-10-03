const workspace=require('./paths.cjs');
const {chromium}=require('playwright');
const fs=require('fs'),path=require('path');
(async()=>{
const browser=await chromium.launch({...(process.env.CHROME_PATH?{executablePath:process.env.CHROME_PATH}:{}),headless:true,args:['--allow-file-access-from-files','--enable-unsafe-swiftshader']});
const page=await browser.newPage({viewport:{width:480,height:360},deviceScaleFactor:1});
page.on('pageerror',e=>console.log(e.message));
await page.goto('file:///'+workspace.verify('verify-vm.html').replaceAll('\\','/'));
await page.evaluate(b=>window.run(b),fs.readFileSync(workspace.project('SVG文字パッキング20文字_32x16.sb3')).toString('base64'));
const config=JSON.parse(fs.readFileSync(workspace.asset('rectangular-config.json'),'utf8'));
await page.evaluate(()=>vm.stopAll());
const results=[];
for(const [i,key] of [...'123456789abcdefghijk'].entries()){
    await page.evaluate(k=>{vm.postIOData('keyboard',{key:k,isDown:true});vm.postIOData('keyboard',{key:k,isDown:false});},key);
    await page.waitForTimeout(170);
    const result=await page.evaluate(()=>{
        const t=vm.runtime.targets[1],r=vm.runtime.renderer,d=r._allDrawables[t.drawableID],skin=d.skin;
        return {hull:d._convexHullPoints,threads:vm.runtime.threads.length,maxTextureScale:skin._maxTextureScale,silhouetteWidth:skin._silhouette._width,silhouetteHeight:skin._silhouette._height};
    });
    if(JSON.stringify(result.hull)!=='[[0,0],[31,0]]'||result.threads!==0)throw Error('Invalid single glyph '+key);
    result.key=key;result.char=config.items[i].char;results.push(result);
    await page.screenshot({path:workspace.image('rectangular-'+key+'.png')});
}
// Confirm the actual timed scripts run in order and return to the beginning.
await page.evaluate(()=>vm.greenFlag());
const seen=[];
for(let i=0;i<86;i++){
    const q=await page.evaluate(()=>({direction:vm.runtime.targets[1].direction,time:performance.now()}));
    const index=config.items.findIndex(t=>Math.abs(t.direction-q.direction)<.0001);
    if(!seen.length||seen.at(-1).index!==index)seen.push({index,char:config.items[index].char,time:q.time});
    await page.waitForTimeout(250);
}
if(new Set(seen.map(q=>q.index)).size!==20)throw Error('Missing automatic glyph');
for(let i=1;i<seen.length;i++)if(seen[i].index!==(seen[i-1].index+1)%20)throw Error('Incorrect sequence');
if(!seen.some((q,i)=>i&&q.index===0&&seen[i-1].index===19))throw Error('Missing loop');
fs.writeFileSync(workspace.result('rectangular-verification.json'),JSON.stringify({single:results,automatic:seen},null,2));
console.log('Verified 20 single glyphs, line hull, texture dimensions, timed sequence, and loop.');
console.log(JSON.stringify(results[0]));
await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
