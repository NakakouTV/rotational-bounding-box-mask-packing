# Third-party notices

The outline data in `素材/glyphs-expanded.json`, `素材/number-paths.json`, generated SVG atlases and the downloadable Scratch demos is derived from Noto Sans JP, distributed under the SIL Open Font License 1.1. The full copyright and license text is in [フォント/OFL.txt](フォント/OFL.txt). Font files are downloaded separately by `setup_dependencies.py`, pinned to google/fonts commit `66a36c8c94b1a5d992ee4e7f392fccfe4945767c`; SHA-256: `c2f3b4d463500a2ddcd3849cded1fceeb9fd6d1c32e6cbecd568453ba50fc68f`.

Scratch browser dependencies are fetched from their official npm distributions with pinned versions and SHA-256 checksums in `dependencies.json`. The downloaded JavaScript bundles are excluded from Git. scratch-render 2.2.84, scratch-vm 5.0.300 and scratch-storage 6.2.1 declare AGPL-3.0-only. Their upstream repositories are [scratch-render](https://github.com/scratchfoundation/scratch-render), [scratch-vm](https://github.com/scratchfoundation/scratch-vm) and [scratch-storage](https://github.com/scratchfoundation/scratch-storage). Review their license terms when distributing an application containing them.

The paper PDF is a document with subsetted Meiryo fonts; the local fonts report editable document embedding permission (`OS/2.fsType = 8`). Windows font binaries and the original independently addressable Meiryo glyph atlases are not included. The original reference Scratch project is not redistributed because its third-party provenance and license were not established.

Original code and paper: copyright nakakoutv. No additional open-source license for these original works has been selected. Public visibility alone does not grant an unrestricted reuse license. This does not restrict the rights already granted by the third-party font license.
