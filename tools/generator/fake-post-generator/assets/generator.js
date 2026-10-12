(() => {
  const $ = id => document.getElementById(id);
  const cfg = {
    twitter:{name:'X / Twitter',brand:'#1d9bf0',handle:'@',metrics:['Reposts','Replies','Likes'],placeholder:'What is happening?!',client:'X for Web',limit:280,context:'',actions:['Reply','Repost','Like','Views'],description:'Create an X-style post with its compact text-first layout, @handle, timestamp, source label, reply/repost/like metrics and optional media. Standard posts are limited to 280 characters.',settingLabel:'Reply permissions',settingOptions:['Everyone can reply','Accounts you follow','Only accounts mentioned'],settingPrefix:'Replies: ',},
    facebook:{name:'Facebook',brand:'#0866ff',handle:'',metrics:['Reactions','Comments','Shares'],placeholder:'What’s on your mind?',client:'Facebook Web',limit:5000,context:'🌐 Public · Feed post',actions:['Like','Comment','Share'],description:'Build a Facebook feed-style post with reaction totals, comments, shares, an audience label and optional photo. Use the audience label as illustrative context only.',settingLabel:'Post audience',settingOptions:['Public','Friends','Only me'],settingPrefix:'Audience: ',},
    instagram:{name:'Instagram',brand:'#c13584',handle:'@',metrics:['Likes','Comments','Shares'],placeholder:'Write a caption…',client:'Instagram',limit:2200,context:'',actions:['Like','Comment','Share','Save'],description:'Create a photo-first Instagram feed mockup with a square media area, caption, likes, comments, share and save actions. Add a local image to make the preview feel like a real feed post.',settingLabel:'Post format',settingOptions:['Feed photo','Caption only'],settingPrefix:'Format: ',},
    linkedin:{name:'LinkedIn',brand:'#0a66c2',handle:'',metrics:['Reactions','Comments','Reposts'],placeholder:'What would you like to share with your network?',client:'LinkedIn',limit:3000,context:'🌐 Anyone · Professional update',actions:['Like','Comment','Repost','Send'],description:'Create a professional LinkedIn update with profile identity, professional context, reactions, comments and reposts. The audience line is illustrative, not a live privacy setting.',settingLabel:'Post audience',settingOptions:['Anyone','Connections only','Group members'],settingPrefix:'Audience: ',},
    threads:{name:'Threads',brand:'#111111',handle:'@',metrics:['Likes','Replies','Reposts'],placeholder:'Start a thread…',client:'Threads',limit:500,context:'',actions:['Like','Reply','Repost','Share'],description:'Create a Threads-style text-first post with an @handle, short conversational copy, replies, reposts and likes. The standard post text field is set to 500 characters.',settingLabel:'Reply controls',settingOptions:['Everyone','Followers only','Mentioned profiles only'],settingPrefix:'Replies: ',},
    youtube:{name:'YouTube Community',brand:'#ff0033',handle:'@',metrics:['Likes','Comments','Shares'],placeholder:'Share something with your community…',client:'YouTube',limit:5000,context:'Community post',actions:['Like','Comment','Share'],description:'Create a YouTube Community-style creator update with channel handle, optional image, likes, comments and shares. Community posts can include text or media; this mockup focuses on a single image or text post.'}
  };
  const platform=document.body.dataset.platform||'twitter', c=cfg[platform]||cfg.twitter;
  document.documentElement.style.setProperty('--brand',c.brand);
  document.title=c.name+' Mockup Generator | Laxman Nepal';
  $('platformName').textContent=c.name;
  $('eyebrow').textContent='✦ '+c.name.toUpperCase()+' MOCKUP TOOL';
  $('pageTitle').textContent=c.name+' Mockup Generator';
  $('pageDescription').textContent=c.description+' Export a clearly labeled fictional PNG mockup.';
  $('usernameLabel').textContent=platform==='facebook'||platform==='linkedin'?'Profile label':'Username / handle';
  $('username').value=platform==='facebook'?'Sample Creator':platform==='linkedin'?'Sample Creator · Product Designer':'sample_creator';
  $('message').maxLength=c.limit;
  $('message').placeholder=c.placeholder;
  $('message').value=platform==='twitter'?'Quick update: building something useful today. ✨':platform==='facebook'?'A little update from my day. What do you think? ✨':platform==='instagram'?'Small moments, big memories. ✨ #DailyUpdate':platform==='linkedin'?'I’ve been working on a new project and learned a lot along the way. Here are a few takeaways.':platform==='threads'?'What’s one small thing that made your day better?':'New community update! What should we make next?';
  $('client').value=c.client;
  $('metricOneLabel').textContent=c.metrics[0];$('metricTwoLabel').textContent=c.metrics[1];$('metricThreeLabel').textContent=c.metrics[2];
  $('outMetricOneLabel').textContent=c.metrics[0];$('outMetricTwoLabel').textContent=c.metrics[1];$('outMetricThreeLabel').textContent=c.metrics[2];
  $('outHandlePrefix').textContent=c.handle;
  $('post').classList.add(platform);
  $('post').dataset.platform=platform;
  $('messageCount').previousElementSibling.textContent='Up to '+c.limit.toLocaleString()+' characters';
  let context=$('post').querySelector('.platform-context');
  if(!context){context=document.createElement('div');context.className='platform-context';$('outMessage').insertAdjacentElement('afterend',context);}
  const settingField=document.createElement('div');settingField.className='field platform-setting';
  const settingLabel=document.createElement('label');settingLabel.htmlFor='platformSetting';settingLabel.textContent=c.settingLabel;
  const settingSelect=document.createElement('select');settingSelect.id='platformSetting';settingSelect.className='platform-setting-select';
  c.settingOptions.forEach(option=>{const el=document.createElement('option');el.value=option;el.textContent=option;settingSelect.appendChild(el);});
  settingField.append(settingLabel,settingSelect);
  const themeField=document.querySelector('input[name=theme]')?.closest('.field');
  if(themeField)themeField.parentNode.insertBefore(settingField,themeField);
  const poll=document.createElement('div');poll.className='community-poll';poll.innerHTML='<strong>Sample community poll</strong><div>Which should we cover next?</div><span>AI tools <b>62%</b></span><span>Mobile tips <b>38%</b></span>';poll.hidden=true;
  $('postMedia').insertAdjacentElement('afterend',poll);
  const actions=$('post').querySelector('.post-actions');
  actions.innerHTML=c.actions.map((label,i)=>'<span class="action action-'+i+'"><span class="action-glyph" aria-hidden="true">'+({Like:'♡',Reply:'↩',Replies:'↩',Repost:'⟳',Reposts:'⟳',Comment:'▢',Comments:'▢',Share:'↗',Send:'➤',Save:'⌑',Views:'◉'}[label]||'•')+'</span>'+label+'</span>').join('');
  document.querySelectorAll('.platforms a').forEach(a=>{if(a.dataset.platform===platform)a.setAttribute('aria-current','page');});
  const formatCount=value=>{const n=Math.max(0,Number(value)||0);return n>=1e6?(n/1e6).toFixed(n%1e6===0?0:1)+'M':n>=1e3?(n/1e3).toFixed(n%1e3===0?0:1)+'K':String(n);};
  function update(){
    const name=$('displayName').value.trim()||'Sample Creator';
    const user=$('username').value.trim().replace(platform==='facebook'||platform==='linkedin'?/[^a-zA-Z0-9 ._·-]/g:/[^a-zA-Z0-9_.]/g,'').slice(0,40);
    if($('username').value!==user)$('username').value=user;
    $('outName').textContent=name;$('outUsername').textContent=user||(platform==='facebook'?'Sample Creator':'sample_creator');
    $('outMessage').textContent=$('message').value;
    $('outTime').textContent=$('time').value.trim()||'Time';$('outDate').textContent=$('date').value.trim()||'Date';
    $('outClient').textContent=$('client').value.trim()||c.client;
    $('outMetricOne').textContent=formatCount($('metricOne').value);$('outMetricTwo').textContent=formatCount($('metricTwo').value);$('outMetricThree').textContent=formatCount($('metricThree').value);
    $('nameCount').textContent=$('displayName').value.length+'/50';$('userCount').textContent=user.length+'/40';$('messageCount').textContent=$('message').value.length+'/'+c.limit;
    const settingValue=settingSelect.value;
    context.textContent=platform==='instagram'?(settingValue==='Caption only'?'Caption-only post · no image required':'Photo feed post'):platform==='youtube'?(settingValue==='Poll'?'Community · Poll':settingValue==='Image post'?'Community · Image post':'Community · Text post'):c.settingPrefix+settingValue;
    context.hidden=false;
    poll.hidden=!(platform==='youtube'&&settingValue==='Poll');
    const media=$('postMedia'),hasMedia=!!media.getAttribute('src');
    const showMedia=hasMedia&&!(platform==='instagram'&&settingValue==='Caption only')&&!(platform==='youtube'&&settingValue!=='Image post')&&!(platform==='youtube'&&settingValue==='Poll');
    media.hidden=!showMedia;media.classList.toggle('visible',showMedia);
    $('avatarFallback').textContent=[...name][0]?.toUpperCase()||'S';
    $('post').classList.remove('dim','dark');
    const theme=document.querySelector('input[name=theme]:checked')?.value||'light';if(theme!=='light')$('post').classList.add(theme);
    $('verifiedBadge').classList.toggle('show',document.querySelector('input[name=verified]:checked')?.value==='show');
  }
  ['displayName','username','message','time','date','client','metricOne','metricTwo','metricThree'].forEach(id=>$(id).addEventListener('input',update));
  settingSelect.addEventListener('change',update);
  document.querySelectorAll('input[name=theme],input[name=verified]').forEach(el=>el.addEventListener('change',update));
  $('avatarInput').addEventListener('change',e=>{
    const f=e.target.files&&e.target.files[0];if(!f)return;
    if(!/^image\/(png|jpeg|webp)$/.test(f.type)){alert('Choose a PNG, JPG or WebP image.');e.target.value='';return}
    if(f.size>5*1024*1024){alert('Please choose an image under 5 MB.');e.target.value='';return}
    const reader=new FileReader();reader.onload=()=>{$('avatarImage').src=reader.result;$('avatarImage').hidden=false;$('avatarFallback').hidden=true;$('fileName').textContent=f.name};reader.readAsDataURL(f);
  });
  if($('mediaInput'))$('mediaInput').addEventListener('change',e=>{
    const f=e.target.files&&e.target.files[0];if(!f)return;
    if(!/^image\/(png|jpeg|webp)$/.test(f.type)){alert('Choose a PNG, JPG or WebP image.');e.target.value='';return}
    if(f.size>5*1024*1024){alert('Please choose an image under 5 MB.');e.target.value='';return}
    const reader=new FileReader();reader.onload=()=>{$('postMedia').src=reader.result;$('mediaFileName').textContent=f.name;if(platform==='youtube')settingSelect.value='Image post';update();};reader.readAsDataURL(f);
  });
  $('resetBtn').addEventListener('click',()=>{
    $('displayName').value='Sample Creator';$('username').value=platform==='facebook'?'Sample Creator':platform==='linkedin'?'Sample Creator · Product Designer':'sample_creator';
    $('message').value=platform==='twitter'?'Quick update: building something useful today. ✨':platform==='facebook'?'A little update from my day. What do you think? ✨':platform==='instagram'?'Small moments, big memories. ✨ #DailyUpdate':platform==='linkedin'?'I’ve been working on a new project and learned a lot along the way. Here are a few takeaways.':platform==='threads'?'What’s one small thing that made your day better?':'New community update! What should we make next?';
    $('time').value='4:38 PM';$('date').value='Oct 13, 2026';$('client').value=c.client;$('metricOne').value='100';$('metricTwo').value='12';$('metricThree').value='453';
    document.querySelector('input[name=theme][value=light]').checked=true;document.querySelector('input[name=verified][value=hide]').checked=true;settingSelect.selectedIndex=0;
    $('avatarInput').value='';$('avatarImage').removeAttribute('src');$('avatarImage').hidden=true;$('avatarFallback').hidden=false;$('fileName').textContent='No image selected';
    if($('mediaInput')){$('mediaInput').value='';$('postMedia').removeAttribute('src');$('postMedia').hidden=true;$('postMedia').classList.remove('visible');$('mediaFileName').textContent='No image selected';}
    update();
  });
  $('downloadBtn').addEventListener('click',async()=>{
    const b=$('downloadBtn');if(typeof window.html2canvas!=='function'){alert('Image export library is still loading. Please try again in a moment.');return}
    b.disabled=true;b.textContent='Preparing PNG…';
    try{const canvas=await window.html2canvas($('post'),{scale:window.devicePixelRatio>1?2:1,backgroundColor:null,useCORS:true,logging:false});const a=document.createElement('a');a.download='fictional-'+platform+'-mockup.png';a.href=canvas.toDataURL('image/png');a.click();}
    catch(e){alert('Could not export the image. Please try a smaller profile or post image.');}
    finally{b.disabled=false;b.textContent='Download PNG';}
  });
  update();
})(),settingLabel:'Community format',settingOptions:['Text post','Image post','Poll'],settingPrefix:'Community · ';