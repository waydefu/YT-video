#!/usr/bin/env python3
"""Inspect and render upstream Anatomy Raptor's *real* SVG figure at 4K using Chromium.

Outputs an evidence JSON, a full-page snapshot and up to three SVG art captures.
It never modifies upstream examples. Playwright uses Chromium/SwiftShader software rendering.
"""
import argparse
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ap=argparse.ArgumentParser()
ap.add_argument("--html",type=Path,required=True)
ap.add_argument("--out",type=Path,required=True)
opts=ap.parse_args()
opts.out.mkdir(parents=True,exist_ok=True)
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,args=["--no-sandbox","--disable-dev-shm-usage","--enable-webgl","--use-gl=angle","--use-angle=swiftshader"])
    page=browser.new_page(viewport={"width":1440,"height":1200},device_scale_factor=2)
    page.goto(opts.html.absolute().as_uri(),wait_until="domcontentloaded",timeout=30000)
    page.wait_for_timeout(1600)
    data=page.evaluate("""() => ({
      pageTitle: document.title,
      body: {width:document.body.scrollWidth,height:document.body.scrollHeight},
      svg:Array.from(document.querySelectorAll('svg')).map((e,i)=>({i,
        outerLength:e.outerHTML.length,
        viewBox:e.getAttribute('viewBox'),width:e.getAttribute('width'),
        height:e.getAttribute('height'), cls:e.getAttribute('class'),
        box:(()=>{let r=e.getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height}})()})),
      canvas:Array.from(document.querySelectorAll('canvas')).map((e,i)=>({
        i,width:e.width,height:e.height,box:(()=>{let r=e.getBoundingClientRect();return{x:r.x,y:r.y,w:r.width,h:r.height}})()})),
    })""")
    (opts.out/"dom-summary.json").write_text(json.dumps(data,indent=2),encoding="utf8")
    page.screenshot(path=str(opts.out/"fullpage.png"),full_page=True)
    for row in sorted(data['svg'],key=lambda row:row['box']['w']*row['box']['h'],reverse=True)[:3]:
        j=row['i']
        e=page.locator('svg').nth(j)
        try:
            e.screenshot(path=str(opts.out/f"figure-{j}.png"),timeout=10000)
            (opts.out/f"figure-{j}.svg").write_text(e.evaluate("(e)=>e.outerHTML"),encoding="utf8")
        except Exception as ex:
            (opts.out/f"figure-{j}.error").write_text(str(ex))
    print(json.dumps(data,ensure_ascii=False))
    browser.close()
