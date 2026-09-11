const $=id=>document.getElementById(id);
const input=$('fileInput'),drop=$('dropzone'),editor=$('editor'),canvas=$('canvas'),ctx=canvas.getContext('2d',{willReadFrequently:true});
const selection=$('selection'),wrap=$('canvasWrap');
let original=null,history=[],dragging=false,startX=0,startY=0,rect=null,displayScale=1;
$('year').textContent=new Date().getFullYear();
function openPicker(){input.click()}
$('chooseBtn').onclick=openPicker;
drop.addEventListener('click',e=>{if(e.target.closest('button')===null)openPicker()});
['dragenter','dragover'].forEach(ev=>drop.addEventListener(ev,e=>{e.preventDefault();drop.classList.add('drag')}));
['dragleave','drop'].forEach(ev=>drop.addEventListener(ev,e=>{e.preventDefault();drop.classList.remove('drag')}));
drop.addEventListener('drop',e=>{const f=e.dataTransfer.files[0];if(f)loadFile(f)});
input.addEventListener('change',()=>{if(input.files[0])loadFile(input.files[0]);input.value='' });
function loadFile(file){if(!file.type.startsWith('image/'))return alert('Please choose an image file.');const r=new FileReader();r.onload=()=>{const im=new Image();im.onload=()=>{canvas.width=im.naturalWidth;canvas.height=im.naturalHeight;ctx.drawImage(im,0,0);original=ctx.getImageData(0,0,canvas.width,canvas.height);history=[];$('undoBtn').disabled=true;$('fileName').textContent=file.name;$('imageInfo').textContent=` · ${im.naturalWidth} × ${im.naturalHeight}`;drop.hidden=true;editor.hidden=false;rect=null;selection.hidden=true;requestAnimationFrame(updateScale)};im.src=r.result};r.readAsDataURL(file)}
function updateScale(){displayScale=canvas.getBoundingClientRect().width/canvas.width}
window.addEventListener('resize',updateScale);
function pointerPos(e){const b=canvas.getBoundingClientRect();return {x:Math.max(0,Math.min(canvas.width,(e.clientX-b.left)/b.width*canvas.width)),y:Math.max(0,Math.min(canvas.height,(e.clientY-b.top)/b.height*canvas.height))}}
canvas.addEventListener('pointerdown',e=>{if(canvas.width===0)return;dragging=true;canvas.setPointerCapture(e.pointerId);const p=pointerPos(e);startX=p.x;startY=p.y;rect={x:p.x,y:p.y,w:0,h:0};drawSelection()});
canvas.addEventListener('pointermove',e=>{if(!dragging)return;const p=pointerPos(e);rect={x:Math.min(startX,p.x),y:Math.min(startY,p.y),w:Math.abs(p.x-startX),h:Math.abs(p.y-startY)};drawSelection()});
canvas.addEventListener('pointerup',()=>{dragging=false;if(rect&&rect.w<4||rect&&rect.h<4){rect=null;selection.hidden=true}});
function drawSelection(){if(!rect){selection.hidden=true;return}const b=canvas.getBoundingClientRect();const wb=wrap.getBoundingClientRect();selection.hidden=false;selection.style.left=(canvas.offsetLeft+rect.x/canvas.width*canvas.clientWidth)+'px';selection.style.top=(canvas.offsetTop+rect.y/canvas.height*canvas.clientHeight)+'px';selection.style.width=(rect.w/canvas.width*canvas.clientWidth)+'px';selection.style.height=(rect.h/canvas.height*canvas.clientHeight)+'px'}
$('feather').oninput=e=>$('featherOut').textContent=e.target.value;
$('patchSize').oninput=e=>$('patchOut').textContent=e.target.value;
function clamp(v,a,b){return Math.max(a,Math.min(b,v))}
function copyRegion(src,sx,sy,sw,sh,dx,dy){ctx.save();ctx.globalAlpha=1;ctx.drawImage(src,sx,sy,sw,sh,dx,dy,sw,sh);ctx.restore()}
function heal(){if(!rect||rect.w<4||rect.h<4)return alert('First drag a rectangle around the Gemini logo/watermark.');history.push(ctx.getImageData(0,0,canvas.width,canvas.height));
const x=Math.round(rect.x),y=Math.round(rect.y),w=Math.round(rect.w),h=Math.round(rect.h),expand=parseFloat($('patchSize').value),padX=Math.max(2,Math.round(w*(expand-1)/2)),padY=Math.max(2,Math.round(h*(expand-1)/2));
const sx=clamp(x-padX,0,canvas.width-w),sy=clamp(y-padY,0,canvas.height-h);
const source=document.createElement('canvas');source.width=canvas.width;source.height=canvas.height;source.getContext('2d').putImageData(ctx.getImageData(0,0,canvas.width,canvas.height),0,0);
let fromX=x+w+padX;if(fromX+w>canvas.width)fromX=x-w-padX;let fromY=y+h+padY;if(fromY+h>canvas.height)fromY=y-h-padY;
if(fromX>=0&&fromX+w<=canvas.width){copyRegion(source,fromX,y,w,h,x,y)}else if(fromY>=0&&fromY+h<=canvas.height){copyRegion(source,x,fromY,w,h,x,y)}else{const p=ctx.getImageData(sx,sy,w,h);ctx.putImageData(p,x,y)}
const feather=Number($('feather').value);if(feather>0){const after=ctx.getImageData(x,y,w,h);const before=history[history.length-1];const bd=before.data,ad=after.data;for(let yy=0;yy<h;yy++)for(let xx=0;xx<w;xx++){const edge=Math.min(xx,yy,w-1-xx,h-1-yy);const a=clamp(edge/feather,0,1);const i=((y+yy)*canvas.width+(x+xx))*4;const j=(yy*w+xx)*4;for(let c=0;c<3;c++)ad[j+c]=Math.round(bd[i+c]*(1-a)+ad[j+c]*a)}}ctx.putImageData(after,x,y);selection.hidden=true;rect=null;$('undoBtn').disabled=false}
$('removeBtn').onclick=heal;
$('undoBtn').onclick=()=>{if(!history.length)return;ctx.putImageData(history.pop(),0,0);$('undoBtn').disabled=history.length===0;rect=null;selection.hidden=true};
$('resetBtn').onclick=()=>{if(!original)return;history=[];ctx.putImageData(original,0,0);$('undoBtn').disabled=true;rect=null;selection.hidden=true};
$('downloadBtn').onclick=()=>{canvas.toBlob(blob=>{const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=(($('fileName').textContent||'image').replace(/\.[^.]+$/,'')||'image')+'-cleaned.png');a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000)},'image/png')};
const mobile=$('gb-mobile');mobile?.addEventListener('click',()=>{$('.gb-menu')?.classList.toggle('open')});
$('gb-search-input')?.addEventListener('keydown',e=>{if(e.key==='Enter'&&e.currentTarget.value.trim())location.href='/blog/?q='+encodeURIComponent(e.currentTarget.value.trim())});