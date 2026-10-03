# Workspace instructions

User preference: all future Scratch `.sb3` outputs must store per-image rendering parameters in Scratch lists and use a shared custom rendering block to look up an image ID. Do not duplicate coordinates/angles/size as a separate drawing script for every image.

- Reuse `生成/scratch_list_renderer.py`. The shared block is `画像を描画 (画像ID) x (x) y (y)`.
- Keep `画像ID`, `描画X補正`, `描画Y補正`, `描画方向`, `描画サイズ`, and `描画コスチューム` lists aligned by index.
- Write deliverable sb3s into `成果物/`; SVGs, glyph paths and configuration into `素材/`; generated numerical results into `検証結果/データ/`; screenshots into `検証結果/画像/`.
- Keep generation scripts in `生成/`, test scripts in `検証/`, third-party browser libraries in `ライブラリ/`, and explanations in `資料/`.
- Preserve original samples in `参考サンプル/` and earlier deliverables in `過去の成果物/`.
- Use paths relative to each script's location, through `生成/workspace_paths.py` or `検証/paths.cjs`, so running scripts does not scatter files in the workspace root.
- Demos only show one image at a time in a one-second loop. Do not add keyboard selection or input prompts unless requested.
- The two-sprite demo is an explicit exception: characters loop on the left, and numbered checkerboard tiles on the right are selected with the integer `画像番号` slider (1–31). Keep the frame black. Coordinate clearing and stamping through the stage so both sprites remain visible; redraw only on a timer tick or slider change.
- Immediately before each stamp, evaluate `touching edge` in an empty `if` block to compute precise bounds. Do not use `say a` to trigger bounds calculation.
- Test in whatever form is easiest, but confirm actual Scratch list lookup and the generated sb3's rendering. Code-only mathematical checks do not replace execution for a modified renderer.
