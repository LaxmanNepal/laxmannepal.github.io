(function(){
  const path=location.pathname.split('/').filter(Boolean),slug=path[0]==='products'?path[1]:null;
  if(!slug||slug==='deals')return;
  const esc=s=>String(s??'').replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
  const num=v=>{if(typeof v==='number')return v;const m=String(v??'').replace(/,/g,'').match(/-?\d+(?:\.\d+)?/);return m?Number(m[0]):null};
  const list=v=>Array.isArray(v)?v.filter(Boolean):[];
  function verdict(p,i){
    const rating=num(p.rating)||num(i.rating), value=num(i.value_score), drop=num(i.price_drop_percent)||0;
    if(rating==null&&value==null&&!list(p.pros).length&&!list(p.cons).length)return {title:'Review pending',tone:'pending',why:'Add verified review data to unlock a stronger recommendation.'};
    if((rating>=8.5||value>=80)&&drop>=5)return {title:'Strong buy signal',tone:'good',why:'A strong rating/value signal is combined with a verified recent price drop.'};
    if(rating>=8.5||value>=80)return {title:'Worth considering',tone:'good',why:'Available verified data shows a strong review or value signal.'};
    if(rating>=7||value>=65)return {title:'Consider it',tone:'watch',why:'The available data is positive, but the decision depends on your priorities.'};
    return {title:'Wait for more data',tone:'pending',why:'The current verified dataset is not strong enough for a confident recommendation.'};
  }
  function render(p,i){
    const rating=num(p.rating)||num(i.rating), pros=list(p.pros), cons=list(p.cons), highlights=list(p.review_highlights||p.review_points), summary=p.review_summary||p.rating_note||'';
    const v=verdict(p,i), confidence=[rating!=null,valueScore(i)!=null,pros.length>0,cons.length>0].filter(Boolean).length;
    const cards=[];
    if(rating!=null)cards.push(`<article><small>REVIEW SCORE</small><strong>${esc(rating)}<span>/10</span></strong><p>Verified rating in the product dataset.</p></article>`);
    if(valueScore(i)!=null)cards.push(`<article><small>VALUE SCORE</small><strong>${esc(Math.round(valueScore(i)))}</strong><p>Catalog intelligence signal.</p></article>`);
    cards.push(`<article><small>DATA CONFIDENCE</small><strong>${confidence>=4?'High':confidence>=2?'Medium':'Limited'}</strong><p>${confidence} verified signal${confidence===1?'':'s'} available.</p></article>`);
    const bullets=highlights.length?`<div class="v13-highlights"><h3>Review highlights</h3><ul>${highlights.slice(0,6).map(x=>`<li>${esc(x)}</li>`).join('')}</ul></div>`:'';
    const pc=(pros.length||cons.length)?`<div class="v13-pc"><div><h3>What we like</h3><ul>${(pros.length?pros:['Not added yet']).slice(0,6).map(x=>`<li>${esc(x)}</li>`).join('')}</ul></div><div><h3>What to watch</h3><ul>${(cons.length?cons:['Not added yet']).slice(0,6).map(x=>`<li>${esc(x)}</li>`).join('')}</ul></div></div>`:'';
    const section=document.createElement('section');section.className='v13-review-intelligence';section.innerHTML=`<div class="v13-head"><div><span>REVIEW INTELLIGENCE</span><h2>Should you buy it?</h2><p>Recommendation generated only from verified product fields and catalog intelligence.</p></div><div class="v13-verdict ${v.tone}"><small>VERDICT</small><strong>${esc(v.title)}</strong><span>${esc(v.why)}</span></div></div><div class="v13-metrics">${cards.join('')}</div>${summary?`<div class="v13-summary"><strong>Review summary</strong><p>${esc(summary)}</p></div>`:''}${bullets}${pc}<div class="v13-actions"><a href="/compare/?p=${esc(slug)}">Compare this product</a><a href="/products/">Browse product database</a></div>`;
    const target=document.querySelector('.product-layout'); if(target)target.parentNode.insertBefore(section,target);
  }
  function valueScore(i){return num(i.value_score)}
  Promise.all([
    fetch('/data/products.json',{cache:'no-store'}).then(r=>r.json()),
    fetch('/data/product-intelligence.json',{cache:'no-store'}).then(r=>r.json()).catch(()=>({products:{}}))
  ]).then(([d,i])=>{const p=(d.products||[]).find(x=>x.slug===slug);if(!p)return;const map=i.products||i||{};render(p,map[slug]||{});}).catch(()=>{});
})();
