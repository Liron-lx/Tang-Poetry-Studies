# 序章设计 QA

## Source visual truth

- `image/prologue-reference/00.jpg` — 00 片头，1440 × 1024
- `image/prologue-reference/01-1.jpg` — 01-1 封面，1440 × 1024
- `image/prologue-reference/01-2.jpg` — 01-2 展开诗卷，1440 × 1024
- `image/prologue-reference/01-3.jpg` — 01-3 模糊序词，1440 × 1024
- `image/prologue-reference/01-4-01-5-scroll.jpg` — 01-4/01-5 长卷，1440 × 3072
- `image/prologue-reference/01-5-collapsed.jpg` — 目录收起状态，1440 × 1024
- `image/prologue-reference/01-5-expanded.jpg` — 目录展开状态，1273 × 1024

### Supplied element assets used in implementation

- `image/prologue-elements/book-closed.png` — 合上书本，358 × 493
- `image/prologue-elements/book-open.png` — 展开书本，675 × 493
- `image/prologue-elements/poem-01.png` to `poem-04.png` — 四列诗句透明 PNG

## Implementation

- URL: `http://127.0.0.1:8000/index.html`
- Intended viewport: 1920 × 1080 CSS px, device scale factor 1
- Intended states: splash → cover → poem → preface → unfurled; directory hover preview and click lock
- Fresh browser screenshots captured after the sizing fix at the available local viewport (877 × 777 CSS px):
  - `/private/tmp/tang-prologue-splash-fixed.png`
  - `/private/tmp/tang-prologue-cover-fixed.png`

## Findings

- [P1] 当前版本已切换为以用户提供的参考图和透明书本元素作为序章视觉表面，并保留状态机与交互热点。
- [P1] 01-1 和 01-2 已不再把整张页面截图作为书本本体，改为直接使用用户提供的合书/展开书本 PNG；诗句也改为四个独立透明元素叠加。
- [P1] 修复了通用 `.reference-stage > img` 规则误把 `book-closed.png` 当成整页背景的问题；合书现在按其 358 × 493 原始比例居中显示。
- [P1] 修复了开屏导航占位导致的 60 px 垂直偏移，并让整页开屏参考图满屏铺开，避免底部出现空带。
- [P1] 修正 01-2 四列诗句：容器从脊线附近移入右页，收窄为 24% 书宽，诗句 PNG 恢复为接近原始 26 px 宽度。
- [P2] 当前导航左侧显示的是现有共享文字品牌；Figma 截图中的“侠”形标志没有对应的独立素材，需用户补充 SVG/PNG 才能做到一比一替换。
- [P2] 目录展开图使用整段参考图叠加，仍需在浏览器截图中确认覆盖位置、滚动比例和移动端裁切。
- [P2] 透明导航层和透明交互热点需要浏览器实际点击验证，尤其是 01-1/01-2 无可见按钮的整本书点击区域。

## Comparison evidence

- Source images were opened and inspected from the local reference files above.
- The local implementation server is running, and `npm test` passes.
- Fresh browser screenshots now confirm the splash stage begins at viewport y=0 and the closed-book asset renders at 327.25 × 450.66 CSS px in the available viewport, preserving the supplied 358:493 ratio.
- At the exact 1440 × 1024 reference viewport, the open-book poem columns render at x=790.88, 836.21, 881.54, and 926.88 CSS px, matching the right-page grouping in the supplied reference screenshot.
- The implementation target is now 1920 × 1080; splash hit-area positioning is calculated from the supplied reference image's rendered scale instead of fixed viewport percentages.
- Desktop reference screenshots are mapped to the 1920 × 1080 stage without `cover` cropping, so the supplied bottom seal remains visible; mobile keeps the existing responsive crop behavior.

## Final result

blocked

Blocker: the missing Figma header-mark asset remains pending; automated tests and the available-viewport visual check pass.
