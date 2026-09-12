(function(){
  const root=document.getElementById('compare-result'),picker=document.getElementById('compare-picker');
  let products=[],intel={}; let differencesOnly=false;
  const esc=s=>String(s??'').replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
  const params=()=>new URLSearchParams(location.search);
  const ids=()=>[...new Set(params().getAll('p').concat([params().get('a'),params().get('b')]).filter(Boolean))].slice(0,4);
  const price=p=>{let x=p?.price; if(typeof x==='number')return x; if(!x)return null; let n=String(x).replace(/,/g,'').match(/\d+(?:\.\d+)?/); return n?Number(n[0]):null};
  const nums=s=>{let m=String(s??'').replace(/,/g,'').match(/-?\d+(?:\.\d+)?/);return m?Number(m[0]):null};
  const unit=s=>{let m=String(s??'').toLowerCase().match(/(mah|gb|tb|mp|hz|w|kg|g|mm|inch|in|%|wh|cores?|nm|hours?|hr|x)/);return m?m[1]:''};
  const lowerBetter=k=>/(price|weight|thickness|latency|response|temperature|power consumption|charging time)/i.test(k);
  function verdict(chosen){
    const scores=chosen.map(p=>({p,score:0,value:0,price:price(p)}));
    scores.forEach(x=>{const i=intel[x.p.slug]||{};x.value=Number(i.value_score)||0;x.score=x.value+(Number(i.price_drop_percent)||0)*.25+(Number(i.rating)||0)*2});
    const bestValue=[...scores].sort((a,b)=>b.score-a.score)[0];
    const bestPrice=[...scores].filter(x=>x.price!=null).sort((a,b)=>a.price-b.price)[0];
    const bestRated=[...scores].filter(x=>Number((intel[x.p.slug]||{}).rating)>0).sort((a,b)=>Number((intel[b.p.slug]||{}).rating)-Number((intel[a.p.slug]||{}).rating))[0];
    return `<section class="v12-verdict"><div><span class="v12-kicker">COMPARISON VERDICT</span><h2>Which one should you choose?</h2><p>Scores are based only on available catalog and intelligence data.</p></div><div class="v12-verdict-grid">${bestValue?`<article><small>BEST OVERALL / VALUE</small><strong>${esc(bestValue.p.name)}</strong><span>Strongest available value signal</span></article>`:''}${bestPrice?`<article><small>LOWEST LISTED PRICE</small><strong>${esc(bestPrice.p.name)}</strong><span>${esc(bestPrice.p.price||'Price listed')}</span></article>`:''}${bestRated?`<article><small>HIGHEST RATED</small><strong>${esc(bestRated.p.name)}</strong><span>${esc((intel[bestRated.p.slug]||{}).rating)} rating</span></article>`:''}</div></section>`;
  }
  function cell(k,p,all){
    const v=(p.specifications||{})[k]; if(v==null||v==='')return '<span class="v12-muted">—</span>';
    const n=nums(v), u=unit(v); let comparable=n!==null;
    if(comparable){let values=all.map(q=>nums((q.specifications||{})[k])).filter(x=>x!==null); if(values.length>=2){let best=lowerBetter(k)?Math.min(...values):Math.max(...values); if(n===best)return `<span class="v12-winner"><i class="fa-solid fa-trophy"></i>${esc(v)}</span>`;}}
    return esc(v);
  }
  function same(a,b){return String(a??'').trim().toLowerCase()===String(b??'').trim().toLowerCase()}
  function row(k,chosen){let vals=chosen.map(p=>(p.specifications||{})[k]??'');if(differencesOnly&&vals.every((v,i)=>i===0||same(v,vals[i-1])))return '';return `<tr><th>${esc(k)}</th>${chosen.map(p=>`<td>${cell(k,p,chosen)}</td>`).join('')}</tr>`}
  function controls(chosen){picker.innerHTML=`<div class="v12-picker"><label><span>Add product</span><select id="product-select"><option value="">Choose a product…</option>${products.filter(p=>!chosen.some(q=>q.slug===p.slug)).map(p=>`<option value="${esc(p.slug)}">${esc(p.name)}</option>`).join('')}</select></label><span class="v12-count">${chosen.length}/4 selected</span><button id="share-compare" class="v12-btn secondary"><i class="fa-solid fa-share-nodes"></i> Share</button><button id="toggle-diff" class="v12-btn ${differencesOnly?'active':''}"><i class="fa-solid fa-filter"></i> ${differencesOnly?'Show all specs':'Differences only'}</button></div>`;
    document.getElementById('product-select').onchange=e=>{if(!e.target.value)return;const u=new URL(location);u.searchParams.delete('a');u.searchParams.delete('b');u.searchParams.append('p',e.target.value);location.href=u};
    document.getElementById('toggle-diff').onclick=()=>{differencesOnly=!differencesOnly;render()};
    document.getElementById('share-compare').onclick=async()=>{try{await navigator.clipboard.writeText(location.href);const b=document.getElementById('share-compare');b.innerHTML='<i class="fa-solid fa-check"></i> Link copied';setTimeout(()=>{b.innerHTML='<i class="fa-solid fa-share-nodes"></i> Share'},1800)}catch(e){prompt('Copy this comparison link:',location.href)}};
  }
  function render(){const chosen=ids().map(id=>products.find(p=>p.slug===id)).filter(Boolean);controls(chosen);if(!chosen.length){root.innerHTML='<div class="compare-empty"><i class="fa-solid fa-code-compare"></i><h2>Choose products to compare</h2><p>Add up to four products. The comparison never guesses missing specifications.</p></div>';return}const keys=[...new Set(chosen.flatMap(p=>Object.keys(p.specifications||{})))];let rows=keys.map(k=>row(k,chosen)).filter(Boolean).join('');root.innerHTML=verdict(chosen)+`<div class="v12-summary">${chosen.map(p=>{const i=intel[p.slug]||{};return `<article><span>${esc(p.brand||p.category||'Product')}</span><h3>${esc(p.name)}</h3><strong>${esc(p.price||'Price not listed')}</strong>${i.price_drop_percent?`<em>${esc(i.price_drop_percent)}% price drop</em>`:''}<a href="/products/${esc(p.slug)}/">View product</a><button class="v12-remove" data-id="${esc(p.slug)}">Remove</button></article>`}).join('')}</div><div class="v12-table-wrap"><table class="v12-table"><thead><tr><th>Specification</th>${chosen.map(p=>`<th><a href="/products/${esc(p.slug)}/">${esc(p.name)}</a></th>`).join('')}</tr></thead><tbody><tr><th>Brand</th>${chosen.map(p=>`<td>${esc(p.brand||'—')}</td>`).join('')}</tr><tr><th>Category</th>${chosen.map(p=>`<td>${esc(p.category||'—')}</td>`).join('')}</tr><tr><th>Price</th>${chosen.map(p=>`<td><strong>${esc(p.price||'Not listed')}</strong></td>`).join('')}</tr>${rows||'<tr><td colspan="5" class="v12-muted">No comparable specifications have been added yet.</td></tr>'}</tbody></table></div><p class="compare-note">Winner badges appear only where numeric specifications can be compared safely. Missing data is shown as unavailable.</p>`;
    document.querySelectorAll('.v12-remove').forEach(b=>b.onclick=()=>{const keep=ids().filter(x=>x!==b.dataset.id),u=new URL(location);u.search='';keep.forEach(x=>u.searchParams.append('p',x));location.href=u});
  }
  Promise.all([fetch('/data/products.json',{cache:'no-store'}).then(r=>r.json()),fetch('/data/product-intelligence.json',{cache:'no-store'}).then(r=>r.json()).catch(()=>({products:{}}))]).then(([d,i])=>{products=d.products||[];intel=i.products||i||{};render()}).catch(()=>root.innerHTML='<div class="compare-empty"><h2>Comparison data unavailable</h2><p>Please try again after the catalog is built.</p></div>');
})();
