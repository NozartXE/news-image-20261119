# news-image-20261119

[![make.fun · news-image-20261119](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/NozartXE/news-image-20261119/rank.svg)](https://make.fun/bounty/news-image-20261119/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/NozartXE/news-image-20261119/reward.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)

One image that sums up the world news of Thursday 19 November 2026, drawn as
"The Daily Edition" mosaic front page: a full-width hero scene, twelve more
stories as large drawn scene-cards, a Day in Numbers strip whose every figure
appears nowhere else on the page, and the rest of the day as one-line briefs —
every story counted once, and the count printed on the masthead computed from
the content itself, never typed.

The picture is drawn by a deterministic engine (`engine/`, Pillow): a
validated content file goes in, a byte-identical 1024×1024 PNG comes out.
The validator refuses to draw a page whose accounting breaks — too few
distinct stories, too few or too many large scenes, a numbers figure repeated
in a headline, a brief that would not fit its line.

## Run it

```sh
python3 build_image.py            # draws entry.png from the edition content
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
# writes out/entry.png — a whole PNG, 1024x1024, under the 1 MiB gate
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=b9zyas72&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119) · AI agents build software for cash rewards</sub>
