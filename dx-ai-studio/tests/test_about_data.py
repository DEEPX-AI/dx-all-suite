"""about-data.json 구조 검증 테스트.

about-data.json은 기업 랜딩페이지 구조:
hero, company, technology, products, investment, partners, news
+ meta, developer, contact, distribution (user-centric extensions)
"""
import json
from pathlib import Path

import pytest

DATA_PATH = Path(__file__).resolve().parent.parent / 'launcher' / 'static' / 'about-data.json'

REQUIRED_SECTIONS = ('hero', 'company', 'technology', 'products',
                     'investment', 'partners', 'news', 'meta', 'developer',
                     'contact', 'distribution')

SUPPORTED_LANGS = ("en", "ko", "ja", "zh-CN", "zh-TW", "es")


@pytest.fixture(scope='module')
def about_data():
    assert DATA_PATH.exists(), f'{DATA_PATH} not found'
    with open(DATA_PATH) as f:
        return json.load(f)


def test_top_level_structure(about_data):
    for section in REQUIRED_SECTIONS:
        assert section in about_data, f'missing top-level section: {section}'


def test_hero_section(about_data):
    hero = about_data['hero']
    assert 'slogan' in hero
    assert 'subtitle' in hero
    assert 'stats' in hero
    assert len(hero['stats']) >= 1, 'hero should have at least 1 stat'


def test_company_section(about_data):
    company = about_data['company']
    for key in ('overview', 'timeline', 'offices'):
        assert key in company, f'company missing {key}'
    assert len(company['timeline']) >= 1
    assert len(company['offices']) >= 1


def test_products_section(about_data):
    products = about_data['products']
    assert 'chips' in products
    assert len(products['chips']) >= 1, 'products should have at least 1 chip'


def test_news_section(about_data):
    news = about_data['news']
    assert 'media' in news
    assert 'upcoming' in news or 'past' in news or 'events' in news
    past = news.get('past') or news.get('events') or []
    assert len(past) >= 1
    if 'upcoming' in news:
        assert len(news['upcoming']) >= 1
    assert 'archive' not in news


def test_distribution_has_direct_sales_channel(about_data):
    channels = about_data['distribution']['channels']
    names = [c['name'] for c in channels]
    assert 'DEEPX Sales' in names
    sales = next(c for c in channels if c['name'] == 'DEEPX Sales')
    assert sales['url'].startswith('https://deepx.ai/contact-us/')


def test_developer_hub(about_data):
    dev = about_data['developer']
    # supportEmail + modelZooSnapshot were intentionally removed (commit 67a2116, "remove
    # version/stats chrome from developer hub"); the 271-model claim is now covered by
    # test_sdk_model_count_official via the developer links.
    assert len(dev.get('links', [])) >= 4
    assert len(dev.get('ctas', [])) >= 2


def test_partners_no_legacy_logos(about_data):
    assert 'logos' not in about_data['partners']


def test_meta_tracking(about_data):
    meta = about_data['meta']
    assert meta.get('lastVerified')
    assert 'deepx.ai' in str(meta.get('sources', []))
    assert meta.get('updateCadence') == 'quarterly'


def test_investment_rounds_collapsed(about_data):
    inv = about_data['investment']
    assert inv.get('showRounds') is False
    assert 'rounds' in inv
    assert len(inv['awards']) >= 1


def _is_i18n_leaf(obj):
    return (
        isinstance(obj, dict)
        and set(SUPPORTED_LANGS).issubset(obj.keys())
        and all(isinstance(obj.get(lang), str) for lang in SUPPORTED_LANGS)
    )


def _collect_i18n_strings(obj, path=""):
    results = []
    if isinstance(obj, dict):
        if any(lang in obj for lang in SUPPORTED_LANGS):
            assert _is_i18n_leaf(obj), f"{path} must include {SUPPORTED_LANGS}"
            results.append(path)
            return results
        for key, value in obj.items():
            results.extend(_collect_i18n_strings(value, f"{path}.{key}" if path else key))
    elif isinstance(obj, list):
        for index, value in enumerate(obj):
            results.extend(_collect_i18n_strings(value, f"{path}[{index}]"))
    return results


def test_i18n_strings_have_all_supported_languages(about_data):
    strings = _collect_i18n_strings(about_data)
    assert strings, "no i18n strings found at all"


def test_hero_slogan_i18n(about_data):
    slogan = about_data["hero"]["slogan"]
    assert _is_i18n_leaf(slogan), "slogan missing supported languages"


def test_products_use_cases(about_data):
    cases = about_data['products'].get('useCases', [])
    assert len(cases) >= 6
    assert all('title' in c and 'desc' in c for c in cases)


def test_partners_ecosystem_compressed(about_data):
    pt = about_data['partners']
    assert 'alliance' in pt
    assert 'ecosystem' in pt
    # Curated named-partner list (Hyundai, AWS, Baidu, …); bounded to catch runaway growth
    # while accommodating the real ~25-partner ecosystem.
    assert len(pt['ecosystem']) <= 30


def test_investment_has_rounds(about_data):
    inv = about_data['investment']
    assert 'rounds' in inv
    assert len(inv['rounds']) >= 1


def test_technology_has_iq8_and_npu(about_data):
    tech = about_data['technology']
    assert 'iq8' in tech
    assert 'npu' in tech
    assert 'Intelligent Quantization' in tech['iq8']['title']['en']
    assert tech['sdk'].get('components')
    # SDK component version badges were intentionally removed (commit 67a2116): dx-com v2.3.0
    # was dropped and the dx-rt version is unpublished, so no versions block should ship.
    assert not tech['sdk'].get('versions')


def test_news_events_are_official_curated(about_data):
    events = about_data['news'].get('past') or about_data['news'].get('events', [])
    assert len(events) >= 6
    titles_en = [e['title']['en'] for e in events]
    assert any('Double Honoree' in t for t in titles_en)
    assert any('Triple Honoree' in t for t in titles_en)
    assert not any('DX-V3 SoC World Premiere' in t for t in titles_en)
    for ev in events:
        assert ev.get('date'), f"event missing date: {ev['title']['en']}"
        assert ev.get('type') in ('event', 'award', 'news', 'webinar'), ev['title']['en']


def test_hero_founded_year_official(about_data):
    # 2018 per TechCrunch ("DEEPX was founded in 2018 by CEO Lokwon Kim") and company HR.
    # deepx.ai's our-story "In 2015 ... led me to found DEEPX" is the founder's decision
    # year, not incorporation — don't regress to it.
    founded = next(s for s in about_data['hero']['stats'] if s['label']['en'] == 'Founded')
    assert founded['value'] == '2018'


def test_sdk_model_count_official(about_data):
    # The verified-model-count claim lives in the developer links section (the SDK technology
    # block was redesigned to a steps/start-here flow and no longer carries a stats array).
    descs = [l['desc']['en'] for l in about_data['developer']['links'] if isinstance(l.get('desc'), dict)]
    assert any('271' in d and 'ONNX' in d for d in descs), descs


def test_news_items_with_urls_are_official(about_data):
    news = about_data['news']
    # DEEPX-owned domains, plus the reputable press/newswire outlets actually cited in the
    # coverage section (real DEEPX press releases and articles). Unknown domains still fail.
    allowed = (
        'https://deepx.ai/', 'https://developer.deepx.ai/',
        'https://www.prnewswire.com/', 'https://www.globenewswire.com/',
        'https://www.sedaily.com/', 'https://www.eetasia.com/', 'https://www.asiae.co.kr/',
    )
    for bucket in ('upcoming', 'past'):
        for item in news.get(bucket, []):
            url = item.get('url')
            if url:
                assert url.startswith(allowed), f"non-official url: {url}"
    for m in news.get('media', []):
        url = m.get('url')
        if url:
            assert url.startswith(allowed), f"non-official media url: {url}"
    past = news.get('past', [])
    with_url = sum(1 for e in past if e.get('url'))
    assert with_url >= 8, f'expected most past items linked, got {with_url}'


def test_no_coming_soon_placeholder(about_data):
    raw = json.dumps(about_data)
    assert 'Coming Soon' not in raw
