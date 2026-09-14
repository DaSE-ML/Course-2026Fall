/* Accessible image enlargement. Native dialog traps focus and restores it on close. */
(()=>{
 const images=[...document.querySelectorAll('.figure img,.body img')];
 if(!images.length)return;
 const dialog=document.createElement('dialog');
 dialog.className='image-viewer';
 dialog.setAttribute('aria-label','放大查看图表');
 dialog.innerHTML='<header><p>图表放大 · 可放大至 200% 并滚动查看</p><button type="button" class="zoom">放大至 200%</button><button type="button" class="close">关闭（Esc）</button></header><div class="image-stage"><img alt=""></div>';
 document.body.append(dialog);
 const stage=dialog.querySelector('.image-stage'),large=dialog.querySelector('img');
 function open(img){large.src=img.src;large.alt=img.alt;large.style.setProperty("--detail-width",`${img.naturalWidth*2}px`);stage.classList.remove('detail');dialog.querySelector('.zoom').textContent='放大至 200%';dialog.showModal();document.body.classList.add('image-open')}
 for(const img of images){img.tabIndex=0;img.setAttribute('role','button');img.setAttribute('aria-label',`${img.alt}；点击放大`);img.title='点击放大图表';img.addEventListener('click',()=>open(img));img.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();e.stopPropagation();open(img)}})}
 const zoom=()=>{const detail=stage.classList.toggle('detail');dialog.querySelector('.zoom').textContent=detail?'适应屏幕':'放大至 200%'};
 large.onclick=zoom;
 dialog.querySelector('.zoom').onclick=zoom;
 const unlock=()=>document.body.classList.remove('image-open');
 dialog.querySelector('.close').onclick=()=>{unlock();dialog.close()};
 dialog.addEventListener('cancel',unlock);
 dialog.addEventListener('close',()=>{if(!dialog.open)unlock()});
 // Prevent the slideshow's document shortcuts from changing a page behind the dialog.
 document.addEventListener('keydown',e=>{if(dialog.open&&e.key!=='Escape')e.stopImmediatePropagation()},true);
})();
(()=>{
 const details=[...document.querySelectorAll('.body details')];
 if(!details.length)return;
 let closed=[];
 const openAll=()=>{closed=details.filter(d=>!d.open);for(const d of closed)d.open=true};
 const restore=()=>{for(const d of closed)d.open=false;closed=[]};
 window.addEventListener('beforeprint',openAll);
 window.addEventListener('afterprint',restore);
 if(typeof matchMedia==='function'){
  const mq=matchMedia('print');
  if(mq.addEventListener){
   mq.addEventListener('change',e=>{if(e.matches)openAll();else restore()});
  }else if(mq.addListener){
   mq.addListener(e=>{if(e.matches)openAll();else restore()});
  }
 }
})();
