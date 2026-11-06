#!/usr/bin/env python3
"""Native PPTX Morph spike using REAL upstream Anatomy official sample images.

Source: https://github.com/wheresryan22/anatomy
Images: .github/assets/raptor-engine-firing.webp, turning-dial.webp,
        ripple-tank.webp. MIT copyright (c) 2026 Ryan. See docs/ASSET-RIGHTS.md
This is a 4-pose / 3-native-Morph camera experiment, NOT an interactive
Anatomy simulation. Actual Microsoft PowerPoint playback is unverified.
Requires: python-pptx Pillow
"""
import argparse
import re
import tempfile
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile,ZIP_DEFLATED

from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR,PP_ALIGN
from pptx.util import Inches,Pt

W,H=13.333333,7.5
BG='111B20'; PAPER='F0ECE3'; GOLD='E4BD87'; MUTED='9EA7A6'
ORANGE='E86542'; SOFT='F9F7F0'
P='http://schemas.openxmlformats.org/presentationml/2006/main'
MC='http://schemas.openxmlformats.org/markup-compatibility/2006'
P159='http://schemas.microsoft.com/office/powerpoint/2015/09/main'
P14='http://schemas.microsoft.com/office/powerpoint/2010/main'
FONT='Noto Sans CJK TC'; SERIF='Noto Serif CJK TC'

SHOTS=[
 (14.30,4.26,1.54,'一個零件，藏著整套系統。','RAPTOR 2 / CLOSE-UP','01'),
 (11.40,4.25,0.70,'從特寫拉遠，結構浮現。','THE REVEAL','02'),
 (22.70,4.25,0.81,'平移，閱讀另一套機械語言。','TURNING DIAL / PAN','03'),
 (33.00,4.25,0.95,'同一個視覺世界，持續向前。','RIPPLE TANK / PAN','04'),
]

def i(v):return Inches(v)
def color(v):return RGBColor.from_string(v)
def shape(sl,n,x,y,w,h,fill):
    s=sl.shapes.add_shape(MSO_SHAPE.RECTANGLE,i(x),i(y),i(w),i(h))
    s.name=n;s.fill.solid();s.fill.fore_color.rgb=color(fill);s.line.fill.background()
    return s
def text(sl,n,t,x,y,w,h,pt,col=PAPER,face=FONT,bold=False,align=None):
    s=sl.shapes.add_textbox(i(x),i(y),i(w),i(h));s.name=n;tf=s.text_frame
    tf.clear();tf.word_wrap=False;tf.vertical_anchor=MSO_ANCHOR.MIDDLE
    tf.margin_left=tf.margin_right=tf.margin_top=tf.margin_bottom=0
    p=tf.paragraphs[0];p.alignment=align or PP_ALIGN.LEFT
    r=p.add_run();r.text=t;r.font.name=face;r.font.size=Pt(pt)
    r.font.color.rgb=color(col);r.font.bold=bold
    return s
def at(x,y,cx,cy,z):return W/2+(x-cx)*z,H/2+(y-cy)*z
def wb(sl,n,x,y,w,h,col,cx,cy,z):
    X,Y=at(x,y,cx,cy,z);return shape(sl,n,X,Y,w*z,h*z,col)
def wt(sl,n,t,x,y,w,h,pt,cx,cy,z,col=PAPER,face=FONT,bold=False):
    X,Y=at(x,y,cx,cy,z)
    return text(sl,n,t,X,Y,w*z,h*z,pt*z,col,face,bold)
def pic(sl,n,p,x,y,w,h,cx,cy,z):
    X,Y=at(x,y,cx,cy,z)
    obj=sl.shapes.add_picture(str(p),i(X),i(Y),width=i(w*z),height=i(h*z))
    obj.name=n
    return obj
def assets_in(p):
    images={}
    for key in ['raptor-engine-firing','turning-dial','ripple-tank']:
        source=p/(key+'.webp')
        if not source.exists():
            raise FileNotFoundError('OFFICIAL IMAGE REQUIRED; no placeholder permitted: '+str(source))
        dest=p/(key+'.png')
        if not dest.exists() or dest.stat().st_mtime < source.stat().st_mtime:
            Image.open(source).convert('RGB').save(dest,optimize=True)
        images[key]=dest
    return images
def stage(sl,cx,cy,z,imgs):
    wb(sl,'!!SCENE_BACKGROUND',-3,-3,47,16,BG,cx,cy,z)
    for j,x in enumerate([.9,10.1,20.6,31.1,41.6]):
        wb(sl,f'!!RULE_{j}',x,-2,.012,12,'26333A',cx,cy,z)
    wt(sl,'!!INTRO_01','01   /   ANATOMY — INTERACTIVE FIGURE ATLAS',1.6,1.48,8.5,.45,14,cx,cy,z,GOLD,bold=True)
    wt(sl,'!!INTRO_02','IDEAS,',1.5,2.28,9.25,1.33,70,cx,cy,z,PAPER,SERIF)
    wt(sl,'!!INTRO_03','MADE',1.5,3.44,9.25,1.33,70,cx,cy,z,PAPER,SERIF)
    wt(sl,'!!INTRO_04','TANGIBLE.',1.5,4.60,9.25,1.33,70,cx,cy,z,PAPER,SERIF)
    wt(sl,'!!INTRO_05','INTERACTIVE SVG   ·   WEBGL   ·   EXPERIMENTAL 3D',1.63,6.25,8.3,.48,15,cx,cy,z,MUTED)
    wb(sl,'!!INTRO_LINE',1.64,7.14,6.1,.02,GOLD,cx,cy,z)
    # Identical object names and actual official source pixels across each
    # successive slide enable native PowerPoint 1:1 matching.
    panels=[
        ('RAPTOR','raptor-engine-firing',10.55,1.00,7.55,'01   /   SVG + WEBGL','RAPTOR 2 · TEST STAND'),
        ('DIAL','turning-dial',21.19,1.00,7.55,'02   /   3D BETA','THE TURNING DIAL'),
        ('RIPPLE','ripple-tank',31.85,1.00,7.55,'03   /   SVG + WEBGL','THE RIPPLE TANK')]
    for tag,key,x,y,k,micro,label in panels:
        wb(sl,'!!'+tag+'_FRAME',x-.17,y-.18,k+.34,k+.37,SOFT,cx,cy,z)
        pic(sl,'!!'+tag+'_IMAGE',imgs[key],x,y,k,k,cx,cy,z)
        wb(sl,'!!'+tag+'_FOOT',x-.17,y+k+.10,k+.34,.6,'17242A',cx,cy,z)
        wt(sl,'!!'+tag+'_INDEX',micro,x,y+k+.19,k*.45,.22,11,cx,cy,z,GOLD,bold=True)
        wt(sl,'!!'+tag+'_LABEL',label,x+k*.48,y+k+.18,k*.5,.24,11,cx,cy,z,PAPER)
    wb(sl,'!!GALLERY_TRACK',1.6,9.43,38,.028,'8C8D83',cx,cy,z)
def overlay(sl,n,cap,tag):
    shape(sl,'!!HUD_TOP',0,0,W,.75,'101A1F')
    shape(sl,'!!HUD_BOTTOM',0,6.86,W,.64,'101A1F')
    shape(sl,'!!HUD_TOPLINE',.72,.72,11.9,.013,'374447')
    shape(sl,'!!HUD_BOTLINE',.72,6.86,11.9,.013,'374447')
    text(sl,'!!HUD_BRAND','ANATOMY',.72,.22,3.7,.30,18,PAPER,bold=True)
    text(sl,'!!HUD_EDITION','VISUAL ESSAY  /  MORPH MOTION STUDY',7.2,.24,5.40,.28,11,MUTED,align=PP_ALIGN.RIGHT)
    text(sl,'CAPTION_'+n,cap,.74,6.98,9.5,.28,13,PAPER)
    text(sl,'LABEL_'+n,tag,9.34,6.98,3.08,.28,10,GOLD,align=PP_ALIGN.RIGHT)
    for j in range(4):
        shape(sl,'!!PROGRESS_'+str(j),.74+j*.60,6.74,.47,.025,ORANGE if j==int(n)-1 else '657476')
def patch(src,dst,duration=1450,advance=2050):
    with ZipFile(src) as z:items={n:z.read(n) for n in z.namelist()}
    names=sorted((n for n in items if re.fullmatch(r'ppt/slides/slide\d+\.xml',n)),
                 key=lambda n:int(re.search(r'slide(\d+)',n).group(1)))
    for j,name in enumerate(names):
        xml=items[name].decode()
        if j==0:
            tr=f'<p:transition xmlns:p="{P}" spd="slow" advTm="{advance}" advClick="1"><p:fade/></p:transition>'
        else:
            tr=(f'<mc:AlternateContent xmlns:mc="{MC}">'
                f'<mc:Choice Requires="p159" xmlns:p159="{P159}">'
                f'<p:transition xmlns:p="{P}" xmlns:p14="{P14}" p14:dur="{duration}" '
                f'spd="slow" advTm="{advance}" advClick="1">'
                '<p159:morph option="byObject"/></p:transition></mc:Choice>'
                f'<mc:Fallback><p:transition xmlns:p="{P}" spd="slow" '
                f'advTm="{advance}" advClick="1"><p:fade/></p:transition>'
                '</mc:Fallback></mc:AlternateContent>')
        match=re.search(r'<p:clrMapOvr[^>]*>.*?</p:clrMapOvr>|<p:clrMapOvr[^>]*/>',xml)
        if not match:raise RuntimeError('Missing clrMapOvr in '+name)
        xml=xml[:match.end()]+tr+xml[match.end():]
        ET.fromstring(xml.encode())
        items[name]=xml.encode()
    with ZipFile(dst,'w',ZIP_DEFLATED,compresslevel=8) as z:
        for name,data in items.items():z.writestr(name,data)
def verify(file):
    with ZipFile(file) as z:
        sl=sorted((n for n in z.namelist() if re.fullmatch(r'ppt/slides/slide\d+\.xml',n)),
                  key=lambda n:int(re.search(r'slide(\d+)',n).group(1)))
        assert len(sl)==4,len(sl)
        for j,n in enumerate(sl):
            x=z.read(n).decode();ET.fromstring(x)
            for name in ('!!RAPTOR_IMAGE','!!DIAL_IMAGE','!!RIPPLE_IMAGE','!!HUD_BRAND'):
                assert name in x,(n,name)
            assert (j==0) or ('p159:morph option="byObject"' in x and '<mc:Fallback>' in x)
        assert z.testzip() is None
    return '4 slides / 3 Office native Morph transitions / 3 matched official images / XML valid'
def main():
    a=argparse.ArgumentParser()
    a.add_argument('--assets',type=Path,required=True)
    a.add_argument('--output',type=Path,required=True)
    arg=a.parse_args()
    img=assets_in(arg.assets)
    license_file=arg.assets.parent/'LICENSE_ANATOMY.txt'
    if not license_file.is_file():
        raise FileNotFoundError('Required upstream MIT LICENSE not available: '+str(license_file))
    license_text=license_file.read_text(encoding='utf-8')
    assert 'Copyright (c) 2026 Ryan' in license_text
    p=Presentation();p.slide_width=i(W);p.slide_height=i(H)
    for cx,cy,zoom,cap,tag,num in SHOTS:
        sl=p.slides.add_slide(p.slide_layouts[6])
        sl.background.fill.solid();sl.background.fill.fore_color.rgb=color(BG)
        stage(sl,cx,cy,zoom,img);overlay(sl,num,cap,tag)
        sl.notes_slide.notes_text_frame.text=(
            '官方示範圖：wheresryan22/anatomy；MIT License，Copyright (c) 2026 Ryan。'
            ' 本 PPT 僅使用原始靜態範例圖作連續鏡頭特寫，並非實際可互動 Anatomy 動畫。'
            ' PowerPoint 原生 Morph 實播狀態：NOT RUN。\n\n' + license_text)
    arg.output.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory() as d:
        draft=Path(d)/'draft.pptx';p.save(draft)
        patch(draft,arg.output)
    print(verify(arg.output))
    print(arg.output)
if __name__=='__main__':main()
