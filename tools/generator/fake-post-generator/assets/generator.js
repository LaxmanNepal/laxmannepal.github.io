(() => {
  const $ = id => document.getElementById(id);
  const cfg = {
    twitter:{name:'X / Twitter',brand:'#1d9bf0',handle:'@',metrics:['Reposts','Quotes','Likes'],placeholder:'What would you like to share?',client:'Web App'},
    facebook:{name:'Facebook',brand:'#0866ff',handle:'',metrics:['Shares','Comments','Reactions'],placeholder:'What’s on your mind?',client:'Facebook Web'},
    instagram:{name:'Instagram',brand:'#c13584',handle:'@',metrics:['Likes','Comments','Shares'],placeholder:'Write a caption…',client:'Instagram'},
    linkedin:{name:'LinkedIn',brand:'#0a66c2',handle:'',metrics:['Reposts','Comments','Reactions'],placeholder:'Share an update with your network…',client:'LinkedIn'},
    threads:{name:'Threads',brand:'#111111',handle:'@',metrics:['Reposts','Replies','Likes'],placeholder:'Start a thread…',client:'Threads'},
    youtube:{name:'YouTube Community',brand:'#ff0033',handle:'@',metrics:['Likes','Comments','Views'],placeholder:'Share an update with your community…',client:'YouTube'}
  };
  const platform = document.body.dataset.platform || 'twitter';
  const c = cfg[platform] || cfg.twitter;
  document.documentElement.style.setProperty('--brand',c.brand);
  document.title = c.name + ' Mockup Generator | Laxman Nepal';
  $('platformName').textContent = c.name;
  $('eyebrow').textContent = '✦ ' + c.name.toUpperCase() + ' MOCKUP TOOL';
  $('pageTitle').textContent = c.name + ' Mockup Generator';
  $('pageDescription').textContent = 'Create a fictional ' + c.name + ' post mockup for UI demos, presentations, stories, and design practice. Customize it and export a PNG.';
  $('usernameLabel').textContent = platform === 'facebook' || platform === 'linkedin' ? 'Profile label' : 'Username';
  $('username').value = platform === 'facebook' ? 'Sample.Creator' : platform === 'linkedin' ? 'Sample Creator · Creator' : 'sample_creator';
  $('username').maxLength = 40;
  $('message').placeholder = c.placeholder;
  $('message').value = 'Sharing a little update ✨ This is a fictional social post mockup.';
  $('client').value = c.client;
  $('metricOneLabel').textContent = c.metrics[0]; $('metricTwoLabel').textContent = c.metrics[1]; $('metricThreeLabel').textContent = c.metrics[2];
  $('outMetricOneLabel').textContent = c.metrics[0]; $('outMetricTwoLabel').textContent = c.metrics[1]; $('outMetricThreeLabel').textContent = c.metrics[2];
  $('outHandlePrefix').textContent = c.handle;
  $('post').classList.add(platform);
  document.querySelectorAll('.platforms a').forEach(a => { if(a.dataset.platform === platform) a.setAttribute('aria-current','page'); });
  const formatCount = value => { const n=Math.max(0,Number(value)||0); return n>=1e6?(n/1e6).toFixed(n%1e6===0?0:1)+'M':n>=1e3?(n/1e3).toFixed(n%1e3===0?0:1)+'K':String(n); };
  function update(){
    const name=$('displayName').value.trim()||'Sample Creator';
    const user=$('username').value.trim().replace(platform==='facebook'||platform==='linkedin'?/[^a-zA-Z0-9 ._·-]/g:/[^a-zA-Z0-9_.]/g,'').slice(0,40);
    if($('username').value!==user)$('username').value=user;
    $('outName').textContent=name; $('outUsername').textContent=user||(platform==='facebook'?'Sample Creator':'sample_creator');
    $('outMessage').textContent=$('message').value;
    $('outTime').textContent=$('time').value.trim()||'Time'; $('outDate').textContent=$('date').value.trim()||'Date';
    $('outClient').textContent=$('client').value.trim()||c.client;
    $('outMetricOne').textContent=formatCount($('metricOne').value); $('outMetricTwo').textContent=formatCount($('metricTwo').value); $('outMetricThree').textContent=formatCount($('metricThree').value);
    $('nameCount').textContent=$('displayName').value.length+'/50'; $('userCount').textContent=user.length+'/40'; $('messageCount').textContent=$('message').value.length+'/280';
    $('avatarFallback').textContent=[...name][0]?.toUpperCase()||'S';
    $('post').classList.remove('dim','dark');
    const theme=document.querySelector('input[name=theme]:checked')?.value||'light'; if(theme!=='light')$('post').classList.add(theme);
    $('verifiedBadge').classList.toggle('show',document.querySelector('input[name=verified]:checked')?.value==='show');
  }
  ['displayName','username','message','time','date','client','metricOne','metricTwo','metricThree'].forEach(id=>$(id).addEventListener('input',update));
  document.querySelectorAll('input[name=theme],input[name=verified]').forEach(el=>el.addEventListener('change',update));
  $('avatarInput').addEventListener('change',e=>{
    const f=e.target.files&&e.target.files[0]; if(!f)return;
    if(!/^image\/(png|jpeg|webp)$/.test(f.type)){alert('Choose a PNG, JPG or WebP image.');e.target.value='';return}
    if(f.size>5*1024*1024){alert('Please choose an image under 5 MB.');e.target.value='';return}
    const reader=new FileReader();reader.onload=()=>{$('avatarImage').src=reader.result;$('avatarImage').hidden=false;$('avatarFallback').hidden=true;$('fileName').textContent=f.name};reader.readAsDataURL(f);
  });
  $('resetBtn').addEventListener('click',()=>{
    $('displayName').value='Sample Creator';$('username').value=platform==='facebook'?'Sample.Creator':platform==='linkedin'?'Sample Creator · Creator':'sample_creator';
    $('message').value='Sharing a little update ✨ This is a fictional social post mockup.';$('time').value='4:38 PM';$('date').value='Oct 13, 2026';$('client').value=c.client;
    $('metricOne').value='100';$('metricTwo').value='12';$('metricThree').value='453';
    document.querySelector('input[name=theme][value=light]').checked=true;document.querySelector('input[name=verified][value=hide]').checked=true;
    $('avatarInput').value='';$('avatarImage').removeAttribute('src');$('avatarImage').hidden=true;$('avatarFallback').hidden=false;$('fileName').textContent='No image selected';update();
  });
  $('downloadBtn').addEventListener('click',async()=>{
    const b=$('downloadBtn');if(typeof window.html2canvas!=='function'){alert('Image export library is still loading. Please try again in a moment.');return}
    b.disabled=true;b.textContent='Preparing PNG…';
    try{const canvas=await window.html2canvas($('post'),{scale:window.devicePixelRatio>1?2:1,backgroundColor:null,useCORS:true,logging:false});const a=document.createElement('a');a.download='fictional-'+platform+'-mockup.png';a.href=canvas.toDataURL('image/png');a.click()}
    catch(e){alert('Could not export the image. Please try a smaller profile picture.')}
    finally{b.disabled=false;b.textContent='Download PNG'}
  });
  update();
})();