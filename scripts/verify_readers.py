"""Rendered smoke tests for seven local readers, using the installed agent-browser."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile

LIBRARY = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
OUT = Path(tempfile.mkdtemp(prefix='ebook-reader-qa-'))
BOOKS = {
    'ai-engineer': ('ai-engineer/index.html', 'ai-engineer/01.html'),
    'agent-memory': ('agent-memory/index.html', 'agent-memory/chapters/01-mental-model.html'),
    'ai-infra': ('ai-infra/index.html', 'ai-infra/chapters/01-request-journey.html'),
    'langchain': ('langchain-langgraph/index.html', 'langchain-langgraph/chapters/01-two-layers.html'),
    'pi': ('pi-code-mode/index.html', 'pi-code-mode/index.html'),
    'rag': ('rag/wiki/index.html', 'rag/wiki/chapters/03-data-model.md'),
    'octop': ('octop/wiki/index.html', 'octop/wiki/chapters/08-turn-path.html'),
}
# Select the real RAG chapter without assuming the author's chapter slug.
BOOKS['rag'] = ('rag/wiki/index.html', str(next((LIBRARY/'rag/wiki/chapters').glob('03-*.html')).relative_to(LIBRARY)))


def run(*args):
    p = subprocess.run(['agent-browser','--session','ebook-polish-qa','--json',*args],
                       capture_output=True, text=True, timeout=35)
    if p.returncode:
        raise RuntimeError(p.stdout + p.stderr)
    result = json.loads(p.stdout)
    if not result.get('success'):
        raise RuntimeError(result)
    return result.get('data', {})


MEASURE = '''(() => {
const content=document.querySelector('.prose,.content,.reading,.layout>main');
const title=document.querySelector('h1');
const theme=document.querySelector('[data-reader-theme]');
const buttons=[...document.querySelectorAll('.topbar button,.bar button,.tools button')];
return {title:title?.textContent.trim(),width:innerWidth,scrollWidth:document.documentElement.scrollWidth,
font:content?getComputedStyle(content).fontSize:null,theme:!!theme,
mobileToc:!!document.querySelector('.reader-mobile-toc,.mobile-toc,.toc'),
smallButtons:buttons.filter(x=>{const r=x.getBoundingClientRect();return r.width>0&&r.height>0&&(r.width<42||r.height<42)}).map(x=>x.textContent)};
})()'''


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    results = []
    for name,(home,chapter) in BOOKS.items():
        for width,height,page,theme in [(1440,1000,home,'light'),(834,1112,chapter,'light'),(390,844,chapter,'dark')]:
            run('set','viewport',str(width),str(height))
            run('open',(LIBRARY/page).as_uri())
            run('eval',f'document.documentElement.dataset.theme="{theme}"; scrollTo(0,0)')
            measured = run('eval',MEASURE)['result']
            measured.update(book=name,page=page,themeTest=theme)
            assert measured['title'], measured
            assert measured['scrollWidth'] <= width + 2, measured
            assert measured['theme'], measured
            assert not measured['smallButtons'], measured
            results.append(measured)
            if width in (390,1440):
                run('screenshot',str(OUT/f'{name}-{width}-{theme}.png'))
        print(f'PASS {name}: desktop, tablet, mobile; theme control; no page overflow',flush=True)
    run('open',(LIBRARY/'langchain-langgraph/search.html').as_uri())
    run('fill','#search','工具')
    search_count = run('eval','document.querySelectorAll(".search-hit").length')['result']
    assert search_count > 0, 'search produced no results'
    results.append({'search':'工具','hits':search_count})
    # A denied clipboard API must still allow the reader to select code.
    run('open',(LIBRARY/'octop/wiki/chapters/08-turn-path.html').as_uri())
    run('eval','Object.defineProperty(navigator,"clipboard",{value:{writeText:()=>Promise.reject(new Error("denied"))},configurable:true})')
    run('eval','document.querySelector("pre").scrollIntoView({block:"center",behavior:"instant"})')
    run('wait','--fn','document.querySelector("button.copy").getBoundingClientRect().top > 80 && document.querySelector("button.copy").getBoundingClientRect().bottom < innerHeight')
    refs = run('snapshot','-i')['refs']
    copy_ref = next(key for key,item in refs.items() if item.get('role') == 'button' and item.get('name') == '复制这段代码')
    run('click','@' + copy_ref)
    selected=run('eval','getSelection().toString().length')['result']
    assert selected > 0, 'clipboard fallback did not select code'
    results.append({'clipboardDeniedFallback':selected})
    copy_size = run('eval','(() => { const r=document.querySelector("button.copy").getBoundingClientRect(); return [r.width,r.height]; })()')['result']
    assert min(copy_size) >= 44, copy_size
    results.append({'copyTouchTarget':copy_size})
    # Real disclosures must print completely without changing the reading state.
    run('open',(LIBRARY/'octop/wiki/chapters/16-tradeoffs.html').as_uri())
    printed = run('eval','''(() => {
      const d=document.querySelector('main details'); d.open=false;
      dispatchEvent(new Event('beforeprint'));
      dispatchEvent(new Event('beforeprint'));
      const expanded=d.open;
      dispatchEvent(new Event('afterprint'));
      return {expanded,restored:!d.open};
    })()''')['result']
    assert printed == {'expanded':True,'restored':True}, printed
    results.append({'printDisclosure':printed})
    run('set','viewport','390','844')
    run('open',(LIBRARY/'pi-code-mode/index.html').as_uri())
    run('set','viewport','1440','1000')
    toc = run('eval','document.querySelector(".reader-book-toc").open && document.querySelector("nav.toc").checkVisibility()')['result']
    assert toc, 'Pi desktop TOC disappeared after mobile layout'
    results.append({'responsivePiToc':toc})
    run('click','[data-reader-theme]')
    theme = run('eval','document.documentElement.dataset.theme')['result']
    run('reload')
    assert run('eval','document.documentElement.dataset.theme')['result'] == theme
    results.append({'themePersists':theme})
    (OUT/'browser-results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
    run('close')
    print(f'PASS {len(results)} checks; screenshots and browser-results.json in {OUT}')


if __name__ == '__main__':
    main()
