const workspace=require('./paths.cjs');
const {chromium}=require('playwright');
const fs=require('fs'),path=require('path');
(async()=>{
const config=JSON.parse(fs.readFileSync(workspace.asset('optimized-config.json'),'utf8'));const count=config.items.length;const keys='123456789abcdefghijklmnopqrstuvwxyz'.slice(0,count);
const browser=await chromium.launch({...(process.env.CHROME_PATH?{executablePath:process.env.CHROME_PATH}:{}),headless:true,args:['--allow-file-access-from-files','--enable-unsafe-swiftshader']});
const page=await browser.newPage({viewport:{width:480,height:360},deviceScaleFactor:1});
page.on('pageerror',e=>console.log(e.message));
await page.goto('file:///'+workspace.verify('verify-vm.html').replaceAll('\\','/'));
await page.evaluate(b=>window.run(b),fs.readFileSync(workspace.project(config.output)).toString('base64'));
const results=Array(count),seen=[];
for(let i=0;i<Math.ceil((count+1.5)*4);i++){
    const q=await page.evaluate(()=>{
        const t=vm.runtime.targets[1],d=vm.runtime.renderer._allDrawables[t.drawableID],skin=d.skin;
        return {index:t.variables.atlas_selected.value-1,direction:t.direction,time:performance.now(),
                hull:d._convexHullPoints,threads:vm.runtime.threads.length,visible:t.visible,
                maxTextureScale:skin._maxTextureScale,silhouetteWidth:skin._silhouette._width,silhouetteHeight:skin._silhouette._height};
    });
    const index=q.index;
    if(index<0||index>=count||Math.abs(q.direction-config.items[index].direction)>.0001||
       JSON.stringify(q.hull)!==JSON.stringify(config.endpoints)||q.threads!==1||q.visible)throw Error('Invalid automatic glyph '+JSON.stringify(q));
    if(!seen.length||seen.at(-1).index!==index){
        seen.push({index,char:config.items[index].char,time:q.time});
        if(!results[index]){
            results[index]={...q,key:keys[index],char:config.items[index].char};
            await page.screenshot({path:workspace.image('optimized-'+keys[index]+'.png')});
        }
    }
    await page.waitForTimeout(250);
}
if(new Set(seen.map(q=>q.index)).size!==count)throw Error('Missing automatic glyph');
for(let i=1;i<seen.length;i++)if(seen[i].index!==(seen[i-1].index+1)%count)throw Error('Incorrect sequence');
if(!seen.some((q,i)=>i&&q.index===0&&seen[i-1].index===count-1))throw Error('Missing loop');
fs.writeFileSync(workspace.result('optimized-verification.json'),JSON.stringify({single:results,automatic:seen},null,2));
console.log(`Verified ${count} automatic glyphs, line hull, texture dimensions, timed sequence, and loop.`);console.log(JSON.stringify(results[0]));await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
