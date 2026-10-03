const fs=require('fs'),path=require('path');
const root=path.resolve(__dirname,'..');
function folder(name){const value=path.join(root,name);fs.mkdirSync(value,{recursive:true});return value;}
const assets=folder('素材'),results=folder('検証結果/データ'),images=folder('検証結果/画像');
module.exports={root,asset:name=>path.join(assets,name),result:name=>path.join(results,name),image:name=>path.join(images,name),verify:name=>path.join(__dirname,name),project:name=>{
    for(const dir of ['成果物','過去の成果物','参考サンプル']){const filename=path.join(root,dir,name);if(fs.existsSync(filename))return filename;}
    throw Error('Project not found: '+name);
}};
