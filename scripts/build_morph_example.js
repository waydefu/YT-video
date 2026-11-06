#!/usr/bin/env node
// Reusable source-only demo for PowerPoint native Morph.
// Run: npm install --no-save pptxgenjs && node scripts/build_morph_example.js
// Then: python scripts/pptx_morph_patch.py morph-draft.pptx morph-native.pptx
// Optional WORLD_IMAGE=/path/to/cleared.png embeds your own licensed visual.
const pptxgen = require('pptxgenjs');
const fs = require('node:fs');
const path = require('node:path');
const pptx = new pptxgen();
pptx.layout = 'LAYOUT_WIDE';
pptx.author = 'YT-video / BROKE TRIO';
pptx.lang = 'zh-TW';
pptx.theme = {headFontFace:'Noto Sans CJK TC',bodyFontFace:'Noto Sans CJK TC',lang:'zh-TW'};
const W=13.3333,H=7.5;
const imagePath=process.env.WORLD_IMAGE || '';
const COLOR={paper:'F1EADA',gold:'D9B67B',cyan:'7CCBC9',dark:'09141D'};
const configs=[
  {focus:[3.0,3.7,1.22],title:'從小細節進場',sub:'01 · MACRO / 世界裡的第一個鏡頭'},
  {focus:[3.0,3.7,.79],title:'拉遠揭露場景',sub:'02 · PULL BACK / 主體不切換'},
  {focus:[6.0,3.7,.81],title:'平移追蹤主體',sub:'03 · PAN / 視覺錨點持續存在'},
  {focus:[8.2,4.0,1.15],title:'推近另一個細節',sub:'04 · PUSH IN / 跨頁延續'},
  {focus:[5.5,3.7,.54],title:'最後回到全景',sub:'05 · WIDE SHOT / 總結'}
];
function addIllustration(s, cx, cy, zoom) {
  if(imagePath && fs.existsSync(imagePath)){
    // Image is deliberately allowed to overflow the viewport: camera pan/zoom.
    const imgW=28.0*zoom, imgH=13.0*zoom;
    s.addImage({path:imagePath,x:W/2 -cx/10*imgW,y:H/2-cy/7.5*imgH,w:imgW,h:imgH,altText:'!!MURAL'});
    return;
  }
  const X=(n)=>(n-cx)*zoom+W/2;
  const Y=(n)=>(n-cy)*zoom+H/2;
  const bg=s.addShape(pptx.ShapeType.rect,{x:X(0),y:Y(0),w:W*zoom,h:H*zoom,
    line:{color:COLOR.dark},fill:{color:COLOR.dark},altText:'!!WORLD_BG'});
  const centers=[[3,3.6],[6.2,3.6],[9.2,3.6]];
  centers.forEach(([x,y],j)=>{
    s.addShape(pptx.ShapeType.ellipse,{x:X(x-1),y:Y(y-1),w:2*zoom,h:2*zoom,
      line:{color:j===1?COLOR.gold:COLOR.cyan,width:2},fill:{color:'102838',transparency:16},
      altText:'!!CIRCLE_'+j});
    s.addShape(pptx.ShapeType.line,{x:X(x-1.4),y:Y(y),w:2.8*zoom,h:0,
      line:{color:COLOR.gold,width:1,transparency:45},altText:'!!RULER_'+j});
  });
}
configs.forEach((q,i)=>{
  const s=pptx.addSlide();
  s.background={color:COLOR.dark};
  addIllustration(s,...q.focus);
  // UI remains editable; large illustration uses matching object identities.
  s.addShape(pptx.ShapeType.rect,{x:.78,y:1.08,w:6.4,h:2.42,line:{color:'516872',width:.4,transparency:80},
    fill:{color:'08151F',transparency:12},altText:'!!TITLE_PLATE'});
  s.addText(q.sub,{x:1.04,y:1.32,w:5.65,h:.34,fontFace:'Noto Sans CJK TC',
    fontSize:13,color:COLOR.gold,bold:true,margin:0,altText:'scene-subtitle'});
  s.addText(q.title,{x:1.05,y:1.88,w:5.9,h:.87,fontFace:'Noto Sans CJK TC',
    fontSize:33,color:COLOR.paper,bold:true,margin:0,altText:'scene-title'});
  s.addText('PRESENTATION · NATIVE MORPH', {x:.81,y:7.11,w:10,h:.22,
    fontSize:9,color:'92A4AD',margin:0,altText:'!!FOOTER'});
  s.addNotes('This is an original transition test; not an Anatomy feature demonstration.');
});
pptx.writeFile({fileName:path.resolve('morph-draft.pptx')});
