(() => {
  const $ = id => document.getElementById(id);
  const DEFAULT_AVATAR='https://yt3.googleusercontent.com/PiqDHS27IXtF4qf1Unqbf77nNL_8sdsi48OjJQMy8hJc9XCknV8IRSDJEqzws30MjDlYQMHh=s120-c-k-c0x00ffffff-no-rj';
  const platform=document.body.dataset.platform||'twitter';
  const cfg={
    twitter:{name:'X / Twitter',brand:'#1d9bf0',usernameLabel:'Username',name:'Laxman Nepal'},
    facebook:{name:'Facebook',brand:'#0866ff',usernameLabel:'Username',name:'Laxman Nepal'},
    instagram:{name:'Instagram',brand:'#c13584',usernameLabel:'Username',name:'Laxman Nepal'},
    linkedin:{name:'LinkedIn',brand:'#0a66c2',usernameLabel:'Username / headline',name:'Laxman Nepal'},
    threads:{name:'Threads',brand:'#111111',usernameLabel:'Username',name:'Laxman Nepal'},
    youtube:{name:'YouTube Community',brand:'#ff0033',usernameLabel:'Channel handle',name:'Laxman Nepal'}
  };
  const c=cfg[platform]||cfg.twitter;
  document.documentElement.style.setProperty('--brand',c.brand);
  document.title=c.name+' Post Card Designer | Laxman Nepal';
  $('platformName').textContent=c.name;$('eyebrow').textContent='✦ '+c.name.toUpperCase()+' CARD DESIGNER';
  $('pageTitle').textContent=c.name+' Post Card Designer';
  $('pageDescription').textContent='Design a customizable '+c.name+'-inspired post card inside your own frame. Adjust proportions, spacing, colors, shadows and text fit, then export a high-resolution image.';
  $('usernameLabel').textContent=c.usernameLabel;
  const defaultContext={twitter:'· 2h',facebook:'2h · 🌐 Public',instagram:'2h · 🌐',linkedin:'Creator • Tech & AI · 2h · 🌐',threads:'· 2h',youtube:'2 hours ago · Public'};
  $('postContext').value=defaultContext[platform]||'2h · Public';
  $('outContext').textContent=$('postContext').value;
  $('contextCount').textContent=$('postContext').value.length+'/100';
  $('displayName').value='Laxman Nepal';$('username').value='@laxmannepal';$('message').value='your post show here ,';
  $('outName').textContent='Laxman Nepal';$('outUsername').textContent='@laxmannepal';$('outMessage').textContent='your post show here ,';
  $('outHandlePrefix').textContent='';
  function loadDefaultAvatar(){
    const avatar=$('avatarImage');
    avatar.hidden=false;
    $('avatarFallback').hidden=true;
    // Set CORS before src so the image can be included in PNG exports when allowed.
    avatar.crossOrigin='anonymous';
    avatar.src=DEFAULT_AVATAR;
    $('fileName').textContent='Default profile picture loaded';
  }
  $('avatarImage').addEventListener('error',()=>{
    $('avatarImage').hidden=true;
    $('avatarFallback').hidden=false;
    if($('fileName').textContent==='Default profile picture loaded')$('fileName').textContent='Default image unavailable · initials shown';
  });
  loadDefaultAvatar();
  $('post').classList.add(platform);$('post').dataset.platform=platform;
  $('messageCount').textContent=$('message').value.length+'/10000';
  document.querySelectorAll('.platforms a').forEach(a=>{if(a.dataset.platform===platform)a.setAttribute('aria-current','page');});
  const root=document.documentElement, frame=$('frame'), post=$('post'), message=$('outMessage');
  const pairs=[['frameWidth','frameWidthOut',' px'],['frameHeight','frameHeightOut',' px'],['framePadding','framePaddingOut',' px'],['frameRadius','frameRadiusOut',' px'],['cardPadding','cardPaddingOut',' px'],['cardRadius','cardRadiusOut',' px'],['cardWidth','cardWidthOut','%'],['fontSize','fontSizeOut',' px'],['avatarSize','avatarSizeOut',' px'],['nameSize','nameSizeOut',' px']];
  function apply(){
    const ratio=$('frameRatio').value;
    frame.style.aspectRatio=(ratio==='auto'||ratio==='custom')?'auto':ratio;
    frame.style.height=ratio==='custom'?$('frameHeight').value+'px':'auto';
    frame.style.overflow='hidden';
    frame.classList.toggle('no-frame-shadow',$('frameShadow').value==='off');
    frame.style.width='min('+ $('frameWidth').value+'px, 100%)';
    frame.style.padding=$('framePadding').value+'px';
    frame.style.borderRadius=$('frameRadius').value+'px';
    frame.style.background=$('frameColor').value;
    frame.style.boxShadow=$('frameShadow').value==='on'?'0 12px 34px rgba(15,23,42,.15)':'none';
    post.style.padding=$('cardPadding').value+'px';
    post.style.borderRadius=$('cardRadius').value+'px';
    post.style.background=$('cardColor').value;
    post.style.color=$('cardTextColor').value;
    post.style.width=$('cardWidth').value+'%';
    post.style.maxWidth='none';
    post.style.boxShadow=$('cardShadow').value==='on'?'0 8px 26px rgba(15,23,42,.20)':'none';
    post.style.border=$('cardBorder').value==='on'?'1px solid rgba(100,116,139,.35)':'none';
    post.style.height=$('postHeight').value==='auto'?'100%':$('postHeight').value+'px';
    post.style.minHeight=$('postHeight').value==='auto'?'0':$('postHeight').value+'px';
    post.style.alignSelf='center';
    post.style.setProperty('--custom-avatar-size',$('avatarSize').value+'px');
    post.style.setProperty('--custom-avatar-shape',$('avatarShape').value);
    post.style.setProperty('--custom-name-size',$('nameSize').value+'px');
    post.style.setProperty('--custom-handle-color',$('handleColor').value);
    $('verifiedBadge').classList.toggle('show',$('showBadge').value==='on');
    const media=$('postMedia');if(media&&!media.hidden)media.classList.add('visible');
    pairs.forEach(([id,out,suffix])=>$(out).textContent=$(id).value+suffix);
    fitMessage();
  }
  function fitMessage(){
    const behavior=$('fitText').value, requested=Number($('fontSize').value);
    message.style.fontSize=requested+'px';
    message.style.overflow='hidden';
    message.style.flex='0 1 auto';
    message.style.minHeight='0';
    post.style.overflow='hidden';

    const media=$('postMedia');
    if(media&&!media.hidden){media.style.maxHeight=$('postHeight').value==='auto'?'none':Math.max(100,Number($('postHeight').value)*0.48)+'px';}
    if(behavior==='grow'){
      // Grow mode must release the fixed-ratio frame; otherwise long text is clipped
      // by the frame even though the inner card itself is allowed to grow.
      frame.style.aspectRatio='auto';
      frame.style.height='auto';
      frame.style.overflow='visible';
      post.style.height='auto';
      post.style.minHeight='0';
      post.style.overflow='visible';
      message.style.overflow='visible';
      message.style.flex='0 0 auto';
      return;
    }

    if($('postHeight').value==='auto' && $('frameRatio').value==='auto'){
      post.style.height='auto';
      post.style.minHeight='0';
      message.style.overflow='visible';
      message.style.flex='0 0 auto';
      return;
    }

    if(behavior==='scroll'){
      message.style.overflow='auto';
      message.style.flex='1 1 auto';
      message.style.minHeight='0';
      return;
    }

    message.style.flex='1 1 auto';
    message.style.minHeight='0';
    let size=requested;
    for(let i=0;i<48;i++){
      message.style.fontSize=size+'px';
      if(message.scrollHeight<=message.clientHeight+1)break;
      if(size<=7)break;
      size=Math.max(7,size-.5);
    }
  }
  ['displayName','username','message'].forEach(id=>$(id).addEventListener('input',()=>{
    $('outName').textContent=$('displayName').value||'Laxman Nepal';
    let user=$('username').value.trim();if(user&& !user.startsWith('@'))user='@'+user;
    $('outUsername').textContent=user||'@laxmannepal';
    $('outMessage').textContent=$('message').value;
    $('nameCount').textContent=$('displayName').value.length+'/50';
    $('userCount').textContent=$('username').value.length+'/40';
    $('messageCount').textContent=$('message').value.length+'/10000';
    fitMessage();
  }));
  $('postContext').addEventListener('input',()=>{$('outContext').textContent=$('postContext').value;$('contextCount').textContent=$('postContext').value.length+'/100';});
  $('mediaInput').addEventListener('change',e=>{
    const file=e.target.files&&e.target.files[0];if(!file)return;
    if(!/^image\/(png|jpeg|webp)$/.test(file.type)){alert('Choose a PNG, JPG or WebP image.');e.target.value='';return;}
    if(file.size>5*1024*1024){alert('Choose an image under 5 MB.');e.target.value='';return;}
    const reader=new FileReader();reader.onload=()=>{$('postMedia').src=reader.result;$('postMedia').hidden=false;$('postMedia').classList.add('visible');$('mediaFileName').textContent=file.name;};reader.readAsDataURL(file);
  });
  const controlIds=['frameRatio','frameWidth','frameHeight','framePadding','frameRadius','frameColor','frameShadow','cardPadding','cardRadius','cardColor','cardTextColor','cardWidth','postHeight','fontSize','fitText','cardShadow','cardBorder','avatarSize','avatarShape','nameSize','handleColor','showBadge'];
  controlIds.forEach(id=>$(id).addEventListener('input',apply));
  controlIds.forEach(id=>$(id).addEventListener('change',apply));
  $('avatarInput').addEventListener('change',e=>{
    const file=e.target.files&&e.target.files[0];if(!file)return;
    if(!/^image\/(png|jpeg|webp)$/.test(file.type)){alert('Choose a PNG, JPG or WebP image.');e.target.value='';return;}
    if(file.size>5*1024*1024){alert('Choose an image under 5 MB.');e.target.value='';return;}
    const reader=new FileReader();reader.onload=()=>{$('avatarImage').removeAttribute('crossorigin');$('avatarImage').src=reader.result;$('avatarImage').hidden=false;$('avatarFallback').hidden=true;$('fileName').textContent=file.name;};reader.readAsDataURL(file);
  });
  $('resetBtn').addEventListener('click',()=>{
    $('displayName').value='Laxman Nepal';$('username').value='@laxmannepal';$('message').value='your post show here ,';
    $('avatarInput').value='';loadDefaultAvatar();
    $('mediaInput').value='';$('postMedia').removeAttribute('src');$('postMedia').hidden=true;$('postMedia').classList.remove('visible');$('mediaFileName').textContent='No image selected';
    $('postContext').value=defaultContext[platform]||'2h · Public';$('outContext').textContent=$('postContext').value;$('contextCount').textContent=$('postContext').value.length+'/100';
    const defaults={frameRatio:'1 / 1',frameWidth:520,frameHeight:520,framePadding:24,frameRadius:18,frameColor:'#eef2f7',frameShadow:'on',cardPadding:18,cardRadius:14,cardColor:'#ffffff',cardTextColor:'#17202b',cardWidth:100,postHeight:'auto',fontSize:16,fitText:'shrink',cardShadow:'off',cardBorder:'on',avatarSize:48,avatarShape:'50%',nameSize:16,handleColor:'#64748b',showBadge:'off'};
    Object.entries(defaults).forEach(([id,value])=>$(id).value=value);
    $('nameCount').textContent='12/50';$('userCount').textContent='12/40';$('messageCount').textContent=$('message').value.length+'/10000';
    $('outName').textContent='Laxman Nepal';$('outUsername').textContent='@laxmannepal';$('outMessage').textContent='your post show here ,';apply();
  });
  const exportFormat=$('exportFormat');
  const exportLabels={png:'PNG',jpeg:'JPG',webp:'WebP'};
  function syncExportLabel(){ $('downloadBtn').textContent='Download '+(exportLabels[exportFormat.value]||'JPG'); }
  exportFormat.addEventListener('change',syncExportLabel);
  syncExportLabel();
  $('downloadBtn').addEventListener('click',async()=>{
    const button=$('downloadBtn');
    if(typeof window.html2canvas!=='function'){alert('The image export library is still loading. Please try again in a moment.');return;}
    const format=exportFormat.value;
    const mime={png:'image/png',jpeg:'image/jpeg',webp:'image/webp'}[format]||'image/jpeg';
    const extension={png:'png',jpeg:'jpg',webp:'webp'}[format]||'jpg';
    button.disabled=true;button.textContent='Preparing '+(exportLabels[format]||'JPG')+'…';
    try{
      const canvas=await window.html2canvas(frame,{scale:3,backgroundColor:format==='jpeg'?'#ffffff':null,useCORS:true,allowTaint:false,logging:false,windowWidth:Math.max(document.documentElement.clientWidth,frame.scrollWidth)});
      const dataUrl=canvas.toDataURL(mime,format==='png'?undefined:0.94);
      // Some browsers may not support WebP encoding; detect fallback rather than
      // silently saving a PNG/JPG with the wrong extension.
      if(format==='webp'&&!dataUrl.startsWith('data:image/webp'))throw new Error('WebP export is not supported by this browser.');
      const link=document.createElement('a');link.download='laxman-nepal-'+platform+'-post-card.'+extension;link.href=dataUrl;link.click();
    }catch(error){alert((error&&error.message&&error.message.includes('WebP'))?'WebP export is not supported in this browser. Try JPG or PNG.':'Image export failed. Try a smaller frame or a locally uploaded profile picture.');}
    finally{button.disabled=false;syncExportLabel();}
  });
  apply();
})();