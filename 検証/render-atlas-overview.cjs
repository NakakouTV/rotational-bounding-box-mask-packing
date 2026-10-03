// Render the original single SVG assets without masking for the paper appendix.
const workspace=require('./paths.cjs');
const fs=require('fs');
const {chromium}=require('playwright');
(async()=>{
 const browser=await chromium.launch({...(process.env.CHROME_PATH?{executablePath:process.env.CHROME_PATH}:{}),headless:true});
 try {
  const page=await browser.newPage({viewport:{width:2048,height:1024},deviceScaleFactor:1});
  await page.setContent('<body style="margin:0"><canvas width="2048" height="1024"></canvas></body>');
  for(const [source,output] of [['packed-font-optimized.svg','RBMP_文字アトラス全体.png'],['packed-numbered-tiles.svg','RBMP_画像アトラス全体.png']]){
   const data=fs.readFileSync(workspace.asset(source)).toString('base64');
   await page.evaluate(async data=>{
    const svg=new Image();svg.src='data:image/svg+xml;base64,'+data;await svg.decode();
    const ctx=document.querySelector('canvas').getContext('2d');
    ctx.fillStyle='white';ctx.fillRect(0,0,2048,1024);ctx.drawImage(svg,0,0,2048,1024);
   },data);
   await page.screenshot({path:workspace.image(output)});
  }
  console.log('Rendered both complete SVG atlases at 2048x1024, preserving packing positions.');
 } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});
