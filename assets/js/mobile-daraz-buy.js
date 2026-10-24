/* LaxmanNepal Daraz shopping buttons for the main mobile-price catalogue. */
(function(window, document){
  'use strict';
  var loaded = false, phones = [];
  var esc = function(s){ return String(s == null ? '' : s).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];}); };
  var money = function(n){ return Number(n) > 0 ? 'Rs. ' + Number(n).toLocaleString('en-IN') : 'Price not confirmed'; };
  var offers = function(p){ return (Array.isArray(p.prices) ? p.prices : []).filter(function(x){return Number(x.price)>0;}).sort(function(a,b){return Number(a.price)-Number(b.price);}); };
  var daraz = function(p){ return offers(p).filter(function(x){return String(x.store||'').toLowerCase()==='daraz' && x.url;})[0]; };
  function inject(){
    if(!loaded || !phones.length) return;
    document.querySelectorAll('#list .card').forEach(function(card){
      if(card.querySelector('.daraz-buy')) return;
      var input = card.querySelector('.compare-pick'); if(!input) return;
      var p = phones.find(function(x){return x.slug === input.getAttribute('data-slug');});
      var d = p && daraz(p); if(!d) return;
      var name = p.model || p.title || 'Phone';
      var box = document.createElement('div'); box.className = 'daraz-buy';
      box.innerHTML = '<div class="daraz-price">Daraz: <strong>'+esc(money(d.price))+'</strong></div><a class="daraz-btn" data-daraz-url="'+esc(d.url)+'" data-daraz-product="'+esc(name)+'" href="'+esc(d.url)+'">🛒 Buy on Daraz</a>';
      var watch = card.querySelector('.watch-btn'); if(watch) watch.parentNode.insertBefore(box, watch); else card.appendChild(box);
    });
    if(window.LaxmanDarazAffiliate) window.LaxmanDarazAffiliate.decorate(document, window.LaxmanDarazAffiliate.config || {});
  }
  function addStyles(){
    if(document.getElementById('laxman-daraz-buy-style')) return;
    var style=document.createElement('style'); style.id='laxman-daraz-buy-style';
    style.textContent='.daraz-buy{margin:0 12px 12px;padding:10px;border:1px solid #e4e7ec;border-radius:11px;background:#fcfcfd}.daraz-price{font-size:11px;color:#667085;margin-bottom:7px}.daraz-price strong{font-size:14px;color:#101828}.daraz-btn{display:block;text-align:center;padding:9px 10px;border-radius:9px;background:#111827;color:#fff!important;text-decoration:none!important;font-size:12px;font-weight:900}.daraz-btn:hover{opacity:.9}@media(max-width:650px){.daraz-buy{margin:0 10px 10px;padding:8px}.daraz-price{font-size:10px}.daraz-price strong{font-size:12px}.daraz-btn{padding:8px 6px;font-size:11px}}';
    document.head.appendChild(style);
  }
  function start(){
    addStyles();
    fetch('/data/mobile-prices.json?v='+Date.now(),{cache:'no-store'}).then(function(r){return r.ok?r.json():null;}).then(function(d){
      phones = d && Array.isArray(d.phones) ? d.phones : []; loaded = true; inject();
      var list=document.getElementById('list'); if(list) new MutationObserver(inject).observe(list,{childList:true,subtree:true});
    }).catch(function(){});
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',start); else start();
})(window, document);
