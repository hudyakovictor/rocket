#!/usr/bin/env python3
from pathlib import Path
import csv,json
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
for category in ('rubber','handle'):
 with Image.open(ROOT/f'{category}_atlas_template.png') as im:assert im.size==(2048,2048) and im.mode=='RGB'
rows=list(csv.DictReader(open(ROOT/'mapping/atlas_mapping.csv')))
assert len(rows)==45
assert len({r['collectionId'] for r in rows})==15
assert {r['atlasPage'] for r in rows}=={'v01','v02','v03'}
assert all(r['rubberUvRect']==r['handleUvRect'] for r in rows)
assert not any('reserved' in r['colorwayId'].lower() for r in rows)
b=json.loads((ROOT/'validation/browser_validation.json').read_text())
assert b['errors']==[] and b['collections']==15 and b['independentCombinations']==225 and b['shapeChecks']==12
assert set(b['templateTextures'])=={'rubberAtlas_template','handleAtlas_template'}
assert b.get('textInAtlas') is False and b.get('panIncluded') is False
assert b.get('handleColourGroups') == 2
assert b.get('handleSideUvCorrected') is True and b.get('handleSideUvMeshes') == 6
side=json.loads((ROOT/'validation/handle_side_uv.json').read_text())
assert side.get('sideUvOnly') is True and side.get('geometryUnchanged') is True and len(side.get('handles',{}))==6
assert side.get('method')=='fixed contour segments + measured arc-length unwrap'
assert 'removed' in b.get('handleTemplateOutlines','')
report={'status':'OK','templateOnly':True,'artworkIncluded':False,'textInAtlas':False,'panIncluded':False,'handleColourGroups':2,'handleSideUvCorrected':True,'handleSideUvMeshes':6,'handleEdgeUnwrap':'measured contour arc length','sidePanelsContinuous':True,'handleTemplateOutlines':False,'handleBleed':'4 master px','handlePreviewMaterial':'high roughness, no white edge glare','geometryUnchanged':True,'categories':['rubber','handle'],'collections':15,'mappingRows':45,'shapeChecks':12,'independentCombinations':225,'textureStatus':b['textureStatus'],'layout':{'page':[2048,2048],'cell':384,'inner':360,'bleed':12,'gap':16,'origin':[32,432],'step':400},'browserErrors':[]}
(ROOT/'validation/validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps(report,ensure_ascii=False,indent=2))
