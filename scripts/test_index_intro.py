from pathlib import Path


INDEX = Path(__file__).resolve().parents[1] / "index.html"


def test_index_uses_two_stage_intro_and_requested_reveal_order():
    html = INDEX.read_text(encoding="utf-8")

    required_markers = [
        'id="cover-stage"',
        'id="序章-stage"',
        'id="startExplore"',
        'data-reveal="poem"',
        'data-reveal="author-note"',
        'data-reveal="question"',
        'data-reveal="metadata"',
    ]
    for marker in required_markers:
        assert marker in html, f"missing intro marker: {marker}"

    assert html.index('data-reveal="poem"') < html.index('data-reveal="author-note"')
    assert html.index('data-reveal="author-note"') < html.index('data-reveal="question"')
    assert html.index('data-reveal="question"') < html.index('data-reveal="metadata"')
    assert 'id="evidenceBtn"' not in html
    assert 'id="evidence"' not in html


def test_index_keeps_poem_and_metadata_copy():
    html = INDEX.read_text(encoding="utf-8")

    for text in [
        "侠客重恩光",
        "骢马饰金装",
        "瞥闻传羽檄",
        "驰突救边荒",
        "写它的人，是武周朝的宠臣",
        "他为什么需要想象一个侠客？",
        "唐（武周时期）",
        "张易之",
    ]:
        assert text in html, f"missing intro copy: {text}"


def test_index_uses_exported_poem_artwork_and_real_logo():
    html = INDEX.read_text(encoding="utf-8")

    for filename in ["第一句.png", "第二句.png", "第三句.png", "第四句.png"]:
        assert filename in html, f"missing poem artwork: {filename}"
    assert "侠logo.svg" in html
    assert "cover-seal" not in html
    assert "class=\"seal\"" not in html


def test_unfurl_button_is_revealed_after_metadata_and_button_spacing_matches():
    html = INDEX.read_text(encoding="utf-8")

    assert 'class="unfurl-wrap hidden"' in html
    assert "metadata.classList.add('revealed')" in html
    assert "unfurlWrap.classList.add('revealed')" in html
    assert ".start-button, .unfurl-button" in html
    assert "letter-spacing: .35em" in html


def test_unfurl_transitions_to_one_screen_scene_then_unlocks_scroll():
    html = INDEX.read_text(encoding="utf-8")

    for marker in [
        'id="scene-stage"',
        'class="scene-title"',
        'class="scene-layer scene-background"',
        'class="scene-layer scene-road"',
        'class="scene-layer scene-foreground"',
        'data-scene-state="locked"',
        'classList.add(\'scene-ready\')',
        'classList.add(\'scene-title-ready\')',
        'classList.remove(\'scene-locked\')',
    ]:
        assert marker in html, f"missing scene flow marker: {marker}"

    assert "overflow: hidden" in html
    assert "assets/img/序/场景/背景1.png" in html
    assert "assets/img/序/场景/前景1.png" in html
    assert "assets/img/序/场景/路1.png" in html
    assert html.index("classList.add('scene-title-ready')") < html.index("classList.add('scene-ready')")


def test_intro_and_scene_share_the_ink_title_and_scene_is_followed_by_directory():
    html = INDEX.read_text(encoding="utf-8")

    assert "image/title-brush-诗风侠影.png" in html
    assert html.count("title-brush-诗风侠影.png") >= 2
    assert 'class="scene-design"' in html
    assert 'class="scene-directory"' in html
    assert html.index('class="scene-design"') < html.index('class="scene-directory"')
    assert html.index('class="scene-directory"') < html.index('class="colophon-footer"')
    assert "--design-width: 1440px" in html
    for anchor in ["top: 707.49px", "top: 1489.86px", "top: 1909.51px"]:
        assert anchor in html, f"missing reference coordinate: {anchor}"
    assert "body.scene-active .序章-stage { display: none; }" not in html


def test_title_watermark_is_four_percent_over_the_correct_base_colors():
    html = INDEX.read_text(encoding="utf-8")

    assert 'class="title-watermark"' in html
    assert html.count('class="title-watermark"') >= 2
    assert ".title-watermark {" in html
    assert "opacity: .04" in html
    assert ".cover-stage { background: #2B2B2B;" in html
    assert ".序章-stage { background: #fff;" in html
    assert ".序章-stage::before" not in html
    assert "repeating-linear-gradient(112deg" not in html
    assert ".scene-design { --design-width: 1440px;" in html
    assert "background: #fff;" in html
    assert "opacity: .04; z-index: 0" in html
    assert "opacity: .075" not in html
