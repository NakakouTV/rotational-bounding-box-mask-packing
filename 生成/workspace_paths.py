from pathlib import Path

# This module lives in 生成/ after workspace organization.
ROOT=Path(__file__).resolve().parent
if ROOT.name=='生成':ROOT=ROOT.parent
ASSETS=ROOT/'素材'
RESULTS=ROOT/'検証結果'/'データ'
IMAGES=ROOT/'検証結果'/'画像'
PROJECTS=ROOT/'成果物'
ARCHIVE=ROOT/'過去の成果物'
SAMPLES=ROOT/'参考サンプル'
VERIFICATION=ROOT/'検証'

for directory in [ASSETS,RESULTS,IMAGES,PROJECTS,ARCHIVE,SAMPLES,VERIFICATION]:directory.mkdir(parents=True,exist_ok=True)
