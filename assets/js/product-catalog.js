(function(){
  const DATA='/data/products.json';
  const state={products:[],selected:new Set(),brand:'',category:'',q:''};
  const esc=s=>String(s??'').replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
  const slug=s=>String(s||'').toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'');
  function compareUrl(ids){const u=new URL('/compare/',location.origin);ids.slice(0,4).forEach(x=>u.searchParams.append('p',x));return u.pathname+u.search}
  function image(p){return p.image?`<img src="${esc(p.image)}" alt="${esc(p.name)}" loading="lazy">`:'<i class="fa-solid fa-mobile-screen-button"></i>'}
  function price(p){if(p.price!==undefined&&p.price!==null&&p.price!=='')return esc(p.price);const v=(p.variants||[]).find(x=>x.price);return v?esc(v.price):'Price not listed'}
  function mount(){
    const grid=document.getElementById('product-grid'),q=document.getElementById('product-search'),brand=document.getElementById('product-brand'),category=document.getElementById('product-category'),count=document.getElementById('product-count'),compare=document.getElementById('catalog-compare');
    if(!grid)return;
    const brands=[...new Set(state.products.map(p=>p.brand).filter(Boolean))].sort();
    const cats=[...new Set(state.products.map(p=>p.category).filter(Boolean))].sort();
    brand.innerHTML='<option value="">All brands</option>'+brands.map(x=>`<option>${esc(x)}</option>`).join('');
    category.innerHTML='<option value="">All categories</option>'+cats.map(x=>`<option>${esc(x)}</option>`).join('');
    function render(){
      const term=state.q.toLowerCase().trim();
      const list=state.products.filter(p=>(!state.brand||p.brand===state.brand)&&(!state.category||p.category===state.category)&&(!term||[p.name,p.brand,p.category,p.subcategory,p.summary].filter(Boolean).join(' ').toLowerCase().includes(term)));
      count.textContent=`${list.length} product${list.length===1?'':'s'}`;
      grid.innerHTML=list.length?list.map(p=>{const checked=state.selected.has(p.slug);return `<article class="catalog-card"><a class="catalog-media" href="/products/${esc(p.slug)}/">${image(p)}</a><div class="catalog-body"><span class="catalog-kicker">${esc(p.brand||'')} · ${esc(p.category||'Gadget')}</span><h2><a href="/products/${esc(p.slug)}/">${esc(p.name)}</a></h2><strong class="catalog-price">${price(p)}</strong><span class="catalog-availability">${esc(p.availability||'Availability not listed')}</span><div class="catalog-actions"><a href="/products/${esc(p.slug)}/">View details</a><button type="button" class="catalog-compare-btn ${checked?'selected':''}" data-slug="${esc(p.slug)}">${checked?'✓ Added':'Compare'}</button></div></div></article>`}).join(''):'<div class="catalog-empty"><i class="fa-solid fa-box-open"></i><h2>No catalog matches yet</h2><p>Search, brand and category filters are ready. Verified products can be added to <code>data/products.json</code>.</p></div>';
      grid.querySelectorAll('.catalog-compare-btn').forEach(b=>b.onclick=()=>{const id=b.dataset.slug;if(state.selected.has(id))state.selected.delete(id);else if(state.selected.size<4)state.selected.add(id);else alert('You can compare up to 4 products.');render();updateCompare()});
    }
    function updateCompare(){const n=state.selected.size;compare.innerHTML=n?`<a class="catalog-floating-compare" href="${compareUrl([...state.selected])}"><i class="fa-solid fa-code-compare"></i> Compare ${n} product${n===1?'':'s'}</a>`:''}
    q?.addEventListener('input',e=>{state.q=e.target.value;render()});brand?.addEventListener('change',e=>{state.brand=e.target.value;render()});category?.addEventListener('change',e=>{state.category=e.target.value;render()});render();updateCompare();
  }
  fetch(DATA,{cache:'no-store'}).then(r=>r.json()).then(d=>{state.products=(d.products||[]).map(p=>({...p,slug:p.slug||slug(p.name)}));mount()}).catch(()=>{const g=document.getElementById('product-grid');if(g)g.innerHTML='<div class="catalog-empty"><h2>Product database unavailable</h2><p>Please try again after the catalog is built.</p></div>'});
})();
