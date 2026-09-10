"""JavaScript walker that flattens open Shadow DOM trees into serializable HTML.

Used by the browser fetchers when `pierce_shadow=True`: the returned serialization
inlines every open shadow root as `<template shadowrootmode="open">` (matching the
declarative shadow DOM format), inlines same-origin `srcdoc`/iframe documents, and
keeps regular light DOM intact, so the normal `Selector` (lxml) pipeline can query
shadow content without any parser changes.

Limitations (by design):
- Closed shadow roots are not readable from JavaScript; their host elements are
  serialized without the shadow content.
- Cross-origin iframes can't be inlined through `contentDocument` and are skipped.
"""

SHADOW_PIERCE_JS = r"""
() => {
  const VOID = new Set(['area','base','br','col','embed','hr','img','input',
                        'link','meta','source','track','wbr']);
  const esc  = s => String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  const escA = s => String(s).replace(/&/g,'&amp;').replace(/"/g,'&quot;');
  function ser(node){
    if(node.nodeType === Node.TEXT_NODE) return esc(node.textContent);
    if(node.nodeType !== Node.ELEMENT_NODE) return '';
    const tag = node.tagName.toLowerCase();
    let h = '<' + tag;
    for(const a of node.attributes){
      if(tag === 'iframe' && a.name === 'srcdoc') continue; // replaced by the real inlined contentDocument below
      h += ` ${a.name}="${escA(a.value)}"`;
    }
    if(VOID.has(tag)) return h + '>';
    h += '>';
    if(node.shadowRoot){  // open shadow root -> declarative template wrapper
      h += '<template shadowrootmode="open">';
      for(const c of node.shadowRoot.childNodes) h += ser(c);
      h += '</template>';
    }
    for(const c of node.childNodes) h += ser(c);
    if(tag === 'iframe'){  // same-origin iframe: inline its document through the same walker
      try{
        const doc = node.contentDocument;
        if(doc && doc.documentElement){
          h += '<template data-frame="same-origin">';
          for(const c of doc.documentElement.childNodes) h += ser(c);
          h += '</template>';
        }
      }catch(e){ /* cross-origin frames are skipped */ }
    }
    return h + `</${tag}>`;
  }
  // No whitespace after the doctype: matches the exact serialization shape of page.content()
  return '<!DOCTYPE html>' + ser(document.documentElement);
}
"""
