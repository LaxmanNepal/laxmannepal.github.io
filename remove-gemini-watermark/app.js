const $=id=>document.getElementById(id);
const input=$('fileInput'),drop=$('dropzone'),editor=$('editor'),canvas=$('canvas'),ctx=canvas.getContext('2d',{willReadFrequently:true});
const selection=$('selection'),wrap=$('canvasWrap');
let original=null,history=[],dragging=false,startX=0,startY=0,rect=null;
$('year').textContent=new Date().getFullYear();

function openPicker(){input.click()}
$('chooseBtn').onclick=openPicker;
drop.addEventListener('click',e=>{if(!e.target.closest('button'))openPicker()});
['dragenter','dragover'].forEach(ev=>drop.addEventListener(ev,e=>{e.preventDefault();e.stopPropagation();drop.classList.add('drag')}));
['dragleave','drop'].forEach(ev=>drop.addEventListener(ev,e=>{e.preventDefault();e.stopPropagation();drop.classList.remove('drag')}));
drop.addEventListener('drop',e=>{const f=e.dataTransfer.files?.[0];if(f)loadFile(f)});
input.addEventListener('change',()=>{const f=input.files?.[0];if(f)loadFile(f);input.value='' });

function loadFile(file){
  if(!file.type.startsWith('image/'))return alert('Please choose an image file.');
  const r=new FileReader();
  r.onload=()=>{const im=new Image();im.onload=()=>{
    canvas.width=im.naturalWidth;canvas.height=im.naturalHeight;ctx.clearRect(0,0,canvas.width,canvas.height);ctx.drawImage(im,0,0);
    original=ctx.getImageData(0,0,canvas.width,canvas.height);history=[];rect=null;selection.hidden=true;
    $('undoBtn').disabled=true;$('fileName').textContent=file.name;$('imageInfo').textContent=` · ${im.naturalWidth} × ${im.naturalHeight}`;
    drop.hidden=true;editor.hidden=false;requestAnimationFrame(drawSelection);
  };im.onerror=()=>alert('The image could not be decoded by this browser.');im.src=r.result};
  r.readAsDataURL(file)
}

function pointerPos(e){
  const b=canvas.getBoundingClientRect();
  return {x:Math.max(0,Math.min(canvas.width,(e.clientX-b.left)/b.width*canvas.width)),y:Math.max(0,Math.min(canvas.height,(e.clientY-b.top)/b.height*canvas.height))}
}
canvas.addEventListener('pointerdown',e=>{if(!canvas.width)return;dragging=true;canvas.setPointerCapture(e.pointerId);const p=pointerPos(e);startX=p.x;startY=p.y;rect={x:p.x,y:p.y,w:0,h:0};drawSelection()});
canvas.addEventListener('pointermove',e=>{if(!dragging)return;const p=pointerPos(e);rect={x:Math.min(startX,p.x),y:Math.min(startY,p.y),w:Math.abs(p.x-startX),h:Math.abs(p.y-startY)};drawSelection()});
canvas.addEventListener('pointerup',()=>{dragging=false;if(!rect||rect.w<4||rect.h<4){rect=null;selection.hidden=true}});
canvas.addEventListener('pointercancel',()=>{dragging=false});

function drawSelection(){
  if(!rect){selection.hidden=true;return}
  const cw=canvas.clientWidth,ch=canvas.clientHeight;
  selection.hidden=false;
  selection.style.left=(canvas.offsetLeft+rect.x/canvas.width*cw)+'px';
  selection.style.top=(canvas.offsetTop+rect.y/canvas.height*ch)+'px';
  selection.style.width=(rect.w/canvas.width*cw)+'px';
  selection.style.height=(rect.h/canvas.height*ch)+'px';
}
window.addEventListener('resize',drawSelection);
$('feather').oninput=e=>$('featherOut').textContent=e.target.value;
$('patchSize').oninput=e=>$('patchOut').textContent=e.target.value;
function clamp(v,a,b){return Math.max(a,Math.min(b,v))}

function makePatch(source,x,y,w,h,dir){
  const sx=dir==='right'?x+w:x-w;
  const sy=dir==='down'?y+h:y-h;
  if(dir==='right'&&sx+w<=canvas.width)return {sx,sy:y};
  if(dir==='left'&&sx>=0)return {sx,sy:y};
  if(dir==='down'&&sy+h<=canvas.height)return {sx:x,sy};
  if(dir==='up'&&sy>=0)return {sx:x,sy};
  return null;
}

function heal(){
  if(!rect||rect.w<4||rect.h<4)return alert('First drag a rectangle tightly around the Gemini logo/watermark.');
  const x=Math.max(0,Math.min(canvas.width-1,Math.round(rect.x))),y=Math.max(0,Math.min(canvas.height-1,Math.round(rect.y)));
  const w=Math.max(1,Math.min(canvas.width-x,Math.round(rect.w))),h=Math.max(1,Math.min(canvas.height-y,Math.round(rect.h)));
  history.push(ctx.getImageData(0,0,canvas.width,canvas.height));
  const before=history[history.length-1];
  const src=document.createElement('canvas');src.width=canvas.width;src.height=canvas.height;src.getContext('2d').putImageData(before,0,0);
  const expand=parseFloat($('patchSize').value);
  const dirs=['right','left','down','up'];
  let patch=null;
  for(const d of dirs){patch=makePatch(src,x,y,w,h,d);if(patch)break}
  if(!patch){
    history.pop();
    return alert('The selected area is too large or too close to the image edges. Select a smaller watermark area.');
  }
  const px=Math.max(0,Math.round(w*(expand-1)/2)),py=Math.max(0,Math.round(h*(expand-1)/2));
  const sx=clamp(patch.sx-(patch.sx<x?px:0),0,canvas.width-w),sy=clamp(patch.sy-(patch.sy<y?py:0),0,canvas.height-h);
  ctx.drawImage(src,sx,sy,w,h,x,y,w,h);

  const feather=Number($('feather').value);
  if(feather>0){
    const after=ctx.getImageData(x,y,w,h),bd=before.data,ad=after.data;
    for(let yy=0;yy<h;yy++)for(let xx=0;xx<w;xx++){
      const edge=Math.min(xx,yy,w-1-xx,h-1-yy);
      const a=clamp(edge/feather,0,1);
      const i=((y+yy)*canvas.width+(x+xx))*4,j=(yy*w+xx)*4;
      for(let c=0;c<3;c++)ad[j+c]=Math.round(bd[i+c]*(1-a)+ad[j+c]*a);
      ad[j+3]=255;
    }
    ctx.putImageData(after,x,y);
  }
  rect=null;selection.hidden=true;$('undoBtn').disabled=false;
}

$('removeBtn').onclick=heal;
$('undoBtn').onclick=()=>{if(!history.length)return;ctx.putImageData(history.pop(),0,0);$('undoBtn').disabled=!history.length;rect=null;selection.hidden=true};
$('resetBtn').onclick=()=>{if(!original)return;history=[];ctx.putImageData(original,0,0);$('undoBtn').disabled=true;rect=null;selection.hidden=true};
$('downloadBtn').onclick=()=>{canvas.toBlob(blob=>{if(!blob)return;const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=(($('fileName').textContent||'image').replace(/\.[^.]+$/,'')||'image')+'-cleaned.png');document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(a.href),1000)},'image/png')};

const mobile=$('gb-mobile');mobile?.addEventListener('click',()=>{$('.gb-menu')?.classList.toggle('open')});
$('gb-search-input')?.addEventListener('keydown',e=>{if(e.key==='Enter'&&e.currentTarget.value.trim())location.href='/blog/?q='+encodeURIComponent(e.currentTarget.value.trim())});