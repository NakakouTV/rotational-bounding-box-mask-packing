"""Export Japanese and number outlines from the OFL-licensed Noto Sans JP."""
from pathlib import Path
import json,argparse
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.transformPen import TransformPen
from workspace_paths import ROOT,ASSETS

parser=argparse.ArgumentParser()
parser.add_argument('--font',type=Path,default=ROOT/'フォント/NotoSansJP.ttf')
args=parser.parse_args()
font=TTFont(args.font)
units=font['head'].unitsPerEm
cmap=font.getBestCmap()

def outlines(text,glyphset):
    path=SVGPathPen(glyphset);bounds=BoundsPen(glyphset);advance=0
    for char in text:
        glyph=glyphset[cmap[ord(char)]]
        transform=(100/units,0,0,-100/units,advance,0)
        glyph.draw(TransformPen(path,transform));glyph.draw(TransformPen(bounds,transform))
        advance+=glyph.width*100/units
    x0,y0,x1,y1=bounds.bounds
    return dict(d=path.getCommands(),x=x0,y=y0,w=x1-x0,h=y1-y0)

chars='日本語文字画像表示実験大小上下左右天地山川森林水火木金土月星空海石田米車花'
regular_font=instantiateVariableFont(font,{'wght':400},inplace=False)
bold_font=instantiateVariableFont(font,{'wght':700},inplace=False)
regular_font.save(ROOT/'フォント/NotoSansJP-Regular.ttf')
bold_font.save(ROOT/'フォント/NotoSansJP-Bold.ttf')
regular=regular_font.getGlyphSet()
bold=bold_font.getGlyphSet()
(ASSETS/'glyphs-expanded.json').write_text(json.dumps({c:outlines(c,regular) for c in chars},ensure_ascii=False,indent=2),encoding='utf-8')
(ASSETS/'number-paths.json').write_text(json.dumps({str(i):outlines(str(i),bold) for i in range(1,32)},indent=2),encoding='utf-8')
print('Noto Sans JP: Japanese outlines and numbers 1-31 exported.')
