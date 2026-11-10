#!/usr/bin/env python3
"""Build clean UV-only templates: no text and no artwork.

Rubber: centered dotted circles + centre mark + separate edge strip.
Handle: solid colour rectangles for A/B/R/L/butt with bleed and no sampled outlines.
The mapping and the previous atlas coordinates remain unchanged.
"""
from pathlib import Path
import base64, colorsys, json, re
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parents[1]
SIZE=2048;CELL=384;INNER=360;X0=32;Y0=432;STEP=400;BLEED=12
MAPPING=json.loads((ROOT/'mapping/atlas_mapping.json').read_text())
COLLECTIONS=MAPPING['collections']

def rect(i,inner=False):
 x=X0+(i%5)*STEP;y=Y0+(i//5)*STEP
 if inner:x+=BLEED;y+=BLEED
 s=INNER if inner else CELL
 return [x,y,x+s,y+s]
def accent(i):
 r,g,b=colorsys.hsv_to_rgb((i*.173)%1,.60,.94);return tuple(int(v*255) for v in (r,g,b))
def master_point(inner,x,y):
 return inner[0]+x/1024*INNER,inner[1]+y/1024*INNER
def master_box(inner,box):
 a=master_point(inner,box[0],box[1]);b=master_point(inner,box[2],box[3]);return [a[0],a[1],b[0],b[1]]
def dotted_circle(d,center,radius,color,width=3,on=5,off=5):
 x,y=center;box=[x-radius,y-radius,x+radius,y+radius]
 for a in range(0,360,on+off):d.arc(box,a,min(a+on,360),fill=color,width=width)
def dotted_line(d,a,b,color,width=1,dash=9):
 # Only horizontal/vertical centre guides are needed here.
 if a[1]==b[1]:
  for x in range(int(a[0]),int(b[0]),dash*2):d.line((x,a[1],min(x+dash,b[0]),b[1]),fill=color,width=width)
 else:
  for y in range(int(a[1]),int(b[1]),dash*2):d.line((a[0],y,b[0],min(y+dash,b[1])),fill=color,width=width)

def base_cell(d,i,inner_fill):
 box=rect(i);inner=rect(i,True)
 d.rectangle(box,fill=(10,15,22),outline=accent(i),width=3)
 d.rectangle(inner,fill=inner_fill,outline=(65,79,93),width=1)
 return inner

def make_rubber():
 im=Image.new('RGB',(SIZE,SIZE),(10,15,22));d=ImageDraw.Draw(im)
 for i,c in enumerate(COLLECTIONS):
  inner=base_cell(d,i,(19,27,37));color=accent(i)
  # This is the centre of the original 768 px FACE in the 1024 px master,
  # not the centre of the whole atlas cell. It therefore lands at the head centre.
  cx,cy=master_point(inner,400,400);scale=INNER/1024
  dotted_line(d,(cx-370*scale,cy),(cx+370*scale,cy),(62,77,91),1)
  dotted_line(d,(cx,cy-370*scale),(cx,cy+370*scale),(62,77,91),1)
  dotted_circle(d,(cx,cy),370*scale,color,3,5,5)
  dotted_circle(d,(cx,cy),270*scale,(190,201,211),2,4,6)
  d.line((cx-11,cy,cx+11,cy),fill=color,width=2);d.line((cx,cy-11,cx,cy+11),fill=color,width=2)
  d.ellipse((cx-3,cy-3,cx+3,cy+3),fill=color)
  edge=master_box(inner,(16,816,1008,1008));d.rectangle(edge,fill=(17,39,49),outline=(60,102,117),width=1)
 im.save(ROOT/'rubber_atlas_template.png',optimize=True)

def make_handle():
 im=Image.new('RGB',(SIZE,SIZE),(10,15,22));d=ImageDraw.Draw(im)
 # Two continuous colour groups instead of a four-colour rainbow.
 # Front + right share blue; back + left share green. This keeps an
 # oblique handle view visually continuous without changing any UVs.
 zones=[((12,12,212,788),(49,132,201)),      # A / front shell
        ((428,12,628,788),(48,157,101))]      # B / back shell
 # Side panels are continuous contour unwraps: front/back halves join without
 # an unused gap. A few master px of bleed keep mip filtering inside colour.
 for x,color in ((224,(49,132,201)),(640,(48,157,101))):
  zones.append(((x+.02*192-4,12,min(x+.98*192+4,1023),788),color))
 for i,c in enumerate(COLLECTIONS):
  inner=base_cell(d,i,(19,27,37))
  for zb,color in zones:
   z=master_box(inner,zb);d.rectangle(z,fill=color)
  cap=master_box(inner,(860,12,1012,164));d.rectangle(cap,fill=(215,184,67))
 im.save(ROOT/'handle_atlas_template.png',optimize=True)

make_rubber();make_handle()
# Update only the two template textures in the existing all-collection reviewer.
viewer=ROOT/'template_viewer.html'
if viewer.exists():
 html=viewer.read_text();m=re.search(r'const PARTS=(.*?),TEXTURES=(.*?),MAP=(.*?);',html,re.S);assert m
 textures=json.loads(m.group(2))
 for category in ('rubber','handle'):
  data=(ROOT/f'{category}_atlas_template.png').read_bytes();textures[f'{category}Atlas_template']='data:image/png;base64,'+base64.b64encode(data).decode()
 html=html[:m.start()]+'const PARTS='+m.group(1)+',TEXTURES='+json.dumps(textures,separators=(',',':'))+',MAP='+m.group(3)+';'+html[m.end():]
 html=html.replace('FULL UV TEMPLATE · 15 COLLECTIONS · NO ARTWORK','CLEAN UV GUIDES · NO TEXT · NO ARTWORK')
 viewer.write_text(html)
print('Built clean text-free templates: dotted rubber circles + coloured handle rectangles')
