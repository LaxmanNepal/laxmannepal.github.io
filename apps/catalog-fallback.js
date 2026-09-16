(()=>{
'use strict';
const fallbackApps=[
 ['Apps','/apps/','App launcher'],['Nepali Patro','/Nepali-Patro/','Nepali calendar and patro'],['Janma Kundali','/Janma-Kundali/','Nepali birth chart and kundali'],['Mausam','/mausam/','Nepali weather dashboard'],['Documents','/documents/','Personal document vault'],['Photos','/Photos/','Photo gallery'],['Laxlink','/Laxlink/','Personal link manager'],['PDF Books','/PDF-Books/','PDF reading library'],['Lofi','/lofi/','Lofi music experience'],['YouTube','/YouTube/','YouTube creator tools'],['Nepali Typing','/nepalityping.github.io/','Nepali typing tool'],['Weather','/Weather/','Weather app'],['Gold Price In Nepal','/Gold-Price-In-Nepal/','Gold price tracker'],['NEPSE','/nepse/','Nepal stock market tools'],['Quotes','/Quotes/','Quotes collection'],['Nisulka Tools','/Nisulka-Tools/','Free online tools'],['AI Tools BY Laxman','/AIToolsBYLaxman/','AI tools directory'],['Text To Handwriting','/Text-To-Handwriting/','Text to handwriting'],['YouTube Search','/YouTube-search-app/','YouTube search tool'],['QR Code Scanner','/qrcodescanner/','QR code scanner'],['Compress JPG','/compressjpg/','JPG compression tool'],['Compress Image','/compress-image/','Image compression tool'],['Progress Bar Of The Year','/Progress-Bar-Of-The-Year/','Year progress visualizer'],['Music','/Music/','Music app'],['Radio','/Radio/','Online radio'],['Live TV','/Live-TV/','Live TV launcher'],['Laxman Nepal Search','/Laxman-Nepal-Search/','Personal search'],['Laxman Nepal Sabda','/laxman-nepal-sabda/','Nepali word tool'],['Clipora','/Clipora/','Creative media tool'],['Kritim','/Kritim/','AI and creative project']
].map((x,i)=>({repo:x[0],name:x[0],url:new URL(x[1],location.origin).href,description:x[2],topics:[],stars:0,updated:'',category:typeof cat==='function'?cat({name:x[0],description:x[2],topics:[]}):'Other',icon:(icons||['fa-table-cells'])[i%(icons?.length||1)],gradient:'none',snapshot:'/assets/app-snapshots/'+slug(x[0])+'.webp',fallback:'https://image.thum.io/get/width/1200/crop/900/noanimate/'+new URL(x[1],location.origin).href,favicon:typeof favUrl==='function'?favUrl(new URL(x[1],location.origin).href):'',featured:i<4}));
const grid=document.getElementById('apps-grid');
if(!grid)return;
const activate=()=>{
 const text=grid.textContent||'';
 if(!/Apps could not be loaded/i.test(text))return;
 if(typeof allApps==='undefined'||typeof render!=='function')return;
 allApps=fallbackApps; if(typeof renderCategories==='function')renderCategories(); render();
 const label=document.getElementById('results-label'); if(label)label.textContent=fallbackApps.length+' apps shown · fallback catalog';
};
new MutationObserver(activate).observe(grid,{childList:true,subtree:true,characterData:true});
setTimeout(activate,2500);
})();
