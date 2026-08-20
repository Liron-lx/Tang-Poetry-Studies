from pathlib import Path
from unittest import TestCase


INDEX = Path(__file__).resolve().parents[1] / "index.html"


class IndexIntroTests(TestCase):
    def test_b_version_intro_and_scene_contract(self):
        html = INDEX.read_text(encoding="utf-8")

        for marker in [
            'id="cover-stage"',
            'id="序章-stage"',
            'id="startExplore"',
            'data-reveal="poem"',
            'data-reveal="author-note"',
            'data-reveal="question"',
            'data-reveal="metadata"',
            'id="scene-stage"',
            'class="scene-layer scene-background3"',
            'class="scene-layer scene-foreground"',
            'data-scene-state="locked"',
            "classList.add('scene-ready')",
            "classList.remove('scene-locked')",
            'class="scene-directory"',
        ]:
            self.assertIn(marker, html)

        for filename in [
            "第一句.png", "第二句.png", "第三句.png", "第四句.png",
            "背景1.svg", "背景2.svg", "背景3.svg", "前景1.png", "山1.png", "建筑1.png",
            "山2.png", "松树.png", "山3.png", "建筑2.png",
        ]:
            self.assertIn(filename, html)

        for text in [
            "侠客重恩光", "骢马饰金装", "瞥闻传羽檄", "驰突救边荒",
            "写它的人，是武周朝的宠臣", "他为什么需要想象一个侠客？",
            "唐（武周时期）", "张易之",
        ]:
            self.assertIn(text, html)

        self.assertIn("侠logo.svg", html)
        self.assertIn("image/title-brush-诗风侠影.png", html)
        self.assertIn("body.scene-active .cover-stage, body.scene-active .序章-stage", html)
        self.assertIn("body.scene-active .scene-stage { margin-top: 0; }", html)
        self.assertIn("window.scrollTo({ top: 0, behavior: 'instant' })", html)
        self.assertLess(html.index('data-reveal="poem"'), html.index('data-reveal="author-note"'))
        self.assertLess(html.index('data-reveal="author-note"'), html.index('data-reveal="question"'))
        self.assertLess(html.index('data-reveal="question"'), html.index('data-reveal="metadata"'))

    def test_scene_uses_updated_assets_and_explicit_depth_order(self):
        html = INDEX.read_text(encoding="utf-8")

        for marker in [
            'class="scene-layer scene-background3"',
            'class="scene-layer scene-background2"',
            'class="scene-layer scene-background1"',
            'src="assets/img/序/场景/背景3.svg"',
            'src="assets/img/序/场景/背景2.svg"',
            'src="assets/img/序/场景/背景1.svg"',
            'src="assets/img/序/场景/走路的人-白色.png"',
            'src="assets/img/序/场景/鸟1.png"',
            'src="assets/img/序/场景/鸟2.png"',
            'src="assets/img/序/场景/鸟3.png"',
            'src="assets/img/序/场景/鸟4.png"',
            '.scene-background3 { z-index: 1; }',
            '.scene-background2 { z-index: 2; }',
            '.scene-background1 { z-index: 3; }',
            '.scene-hill-left { z-index: 13; }',
            '.scene-building-left { z-index: 12; }',
            '.scene-hill-right { z-index: 11; }',
            '.scene-tree { z-index: 10; }',
            '.scene-hill-centre { z-index: 9; }',
            '.scene-building-right { z-index: 8; }',
            '.scene-walker-white { z-index: 16; }',
            '.scene-data { position: absolute; z-index: 30;',
            'data-depth="far"',
            'data-depth="middle"',
            'data-depth="front"',
        ]:
            self.assertIn(marker, html)

        self.assertNotIn('class="scene-layer scene-walker-black"', html)
        self.assertNotIn('class="scene-layer scene-caravan"', html)
        self.assertNotIn('class="scene-layer scene-road-join"', html)
        self.assertNotIn('骆宾王 · 王维 · 李白 · 高适 · 杜甫', html)
        self.assertLess(html.index('class="scene-layer scene-tree"'), html.index('class="scene-layer scene-bird-1"'))
