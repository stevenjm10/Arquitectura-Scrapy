"""Build the local dashboard from saved extraction runs."""
import argparse
import base64
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent

TEMPLATE = r"""<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>scrapy instagram · Dashboard</title>
<style>
:root{font-family:"Segoe UI",system-ui,sans-serif;color:#24233c;background:#f5f3fc;font-synthesis:none}*{box-sizing:border-box}body{margin:0;background:radial-gradient(ellipse at 5% 50%,#ede7ff,transparent 45%),#f7f6fc}a{color:#6950d8;text-decoration:none}a:hover{text-decoration:underline}button,input,select{font:inherit}button,a,input,select,summary{outline-offset:4px}button:focus-visible,a:focus-visible,input:focus-visible,select:focus-visible,summary:focus-visible{outline:3px solid #ae74ff}button,.download{cursor:pointer;transition:transform .18s,box-shadow .18s}button:hover:not(:disabled),.download:hover{transform:translateY(-2px);box-shadow:0 5px 15px #33205d18}button:disabled{opacity:.4;cursor:default}header{position:relative;overflow:hidden;background:#211738;color:#fff;padding:25px max(calc((100vw - 1232px)/2),28px) 67px}header:after{content:"";position:absolute;width:470px;height:470px;right:-90px;top:-260px;border:75px solid #7a4cdd33;border-radius:50%;pointer-events:none}.topline{display:flex;align-items:center;justify-content:space-between;position:relative;z-index:1}.brand{display:flex;align-items:center;gap:11px;font-size:19px;font-weight:750;letter-spacing:-.5px}.brandmark{display:grid;place-items:center;width:34px;height:34px;border-radius:11px;background:linear-gradient(135deg,#ffb385,#ee679d 45%,#9771ff);color:#281638;font-size:23px}.local{display:flex;align-items:center;gap:8px;border:1px solid #ffffff24;border-radius:30px;padding:7px 12px;font-size:12px;color:#ddd3ef}.local:before{content:"";width:6px;height:6px;border-radius:50%;background:#7ce4cc}.hero{position:relative;z-index:1;display:flex;align-items:center;justify-content:space-between;gap:30px;padding-top:43px}.eyebrow{color:#c6a7ff;font-size:11px;font-weight:700;letter-spacing:3px}h1{font-size:clamp(32px,4vw,50px);font-weight:750;letter-spacing:-2px;line-height:1.08;margin:15px 0 16px}h1 em{font-style:normal;color:#c1a1ff}header p{font-size:14px;color:#c3b8d6;line-height:1.7;max-width:490px;margin:0}.hero-art{width:205px;height:150px;position:relative;flex-shrink:0;margin-right:30px}.orbit{position:absolute;inset:0;border:1px solid #ffffff20;border-radius:50%;transform:rotate(-25deg)}.orbit:nth-child(2){inset:20px -20px;transform:rotate(25deg)}.orbit-core{position:absolute;inset:25px 52px;display:grid;place-items:center;border-radius:28px;background:linear-gradient(145deg,#b78cff,#7253d4);box-shadow:0 15px 40px #0004;font-size:48px;color:#fff;transform:rotate(-12deg)}.satellite{position:absolute;width:17px;height:17px;background:#79dfcd;border-radius:6px;right:0;top:40px;transform:rotate(20deg)}.satellite:last-child{width:24px;height:24px;background:#ffb095;left:12px;top:104px}main{position:relative;max-width:1280px;margin:-25px auto 0;padding:0 24px}.toolbar{display:flex;gap:12px;flex-wrap:wrap;align-items:center}.runbar{padding:16px 20px;background:#fff;border:1px solid #ebe6f4;border-radius:16px;box-shadow:0 9px 25px #29194d09}.toolbar label{font-size:12px;font-weight:700;color:#857596;text-transform:uppercase;letter-spacing:1px}select,input,button,.download{padding:11px 15px;border:1px solid #e5dff0;border-radius:10px;background:white;color:#403753;font-size:13px}select{max-width:100%;min-width:0}#run{flex:1;background:#f8f6fd;font-weight:600}.download{background:#7251d3;color:white;border-color:#7251d3;text-decoration:none;font-weight:600}.download:hover{text-decoration:none}input{flex:1;min-width:150px}#notice{font-size:12px;color:#806229;margin:20px 2px;line-height:1.6;display:flex;gap:10px;align-items:center}#notice:before{content:"i";flex-shrink:0;display:grid;place-items:center;background:#f8e8bb;color:#74531d;width:20px;height:20px;border-radius:50%;font-weight:bold}.metrics{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:16px;margin:0 0 25px}.metric{position:relative;overflow:hidden;border-radius:17px;padding:23px 21px;min-height:155px;background:#e9ddff;color:#432772;border:1px solid #dfcef7}.metric:nth-child(2){background:#d6f3ed;border-color:#c3e9df;color:#175e53}.metric:nth-child(3){background:#ffe4d9;border-color:#f7d4c3;color:#813c29}.metric:nth-child(4){background:#e2e7ff;border-color:#d3daf8;color:#394477}.metric:after{content:"";position:absolute;right:-12px;top:-20px;width:82px;height:82px;border:15px solid currentColor;border-radius:50%;opacity:.055}.metric strong{display:block;font-size:clamp(24px,2.5vw,34px);letter-spacing:-1px;font-weight:750;line-height:1.2;margin:16px 0 9px;overflow-wrap:anywhere}.muted{color:#898197;font-size:12px}.metric .muted{color:inherit;opacity:.85}.metric>span:first-child{font-size:12px;font-weight:650}.metric>span:last-child{font-size:11px}.columns{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.75fr);gap:22px}.panel{background:white;border:1px solid #e8e2f1;border-radius:18px;padding:26px;min-width:0}h2{font-size:18px;letter-spacing:-.4px;margin:0 0 13px}.profile-panel{position:relative;background:#302143;color:#fff;border:0;overflow:hidden}.profile-panel:before{content:"";position:absolute;width:180px;height:180px;right:-90px;bottom:-90px;border:35px solid #aa73eb22;border-radius:50%;pointer-events:none}.avatar{width:43px;height:43px;display:grid;place-items:center;background:#a981e8;color:#fff;border-radius:14px;font-size:22px;font-weight:650;margin-bottom:18px}.profile-panel .badge{background:#ffffff12;color:#dbc6ff;font-size:10px;border:1px solid #ffffff15}.profile-panel a{display:inline-block;color:#bcecdf;font-size:12px;margin-top:12px;font-weight:650}.bio{white-space:pre-wrap;line-height:1.8;font-size:13px;overflow-wrap:anywhere}.section-kicker{text-transform:uppercase;letter-spacing:2px;font-size:10px;font-weight:700;color:#9482a9;margin:0 0 9px}.badge{display:inline-block;background:#fff2d9;color:#886027;border-radius:6px;padding:6px 9px;font-size:10px;overflow-wrap:anywhere}.bar{margin:23px 0}.bar label{display:flex;justify-content:space-between;gap:10px;font-size:12px;margin-bottom:10px;color:#675c79}.bar label span:last-child{font-weight:750;color:#6543b0}progress{width:100%;height:9px;appearance:none;border:none;border-radius:15px;overflow:hidden;background:#efebf6;accent-color:#9872e2}progress::-webkit-progress-bar{background:#efebf6;border-radius:15px}progress::-webkit-progress-value{background:linear-gradient(90deg,#b795f4,#7550cc);border-radius:15px}progress::-moz-progress-bar{background:#8960d7;border-radius:15px}.bar:nth-child(2) progress::-webkit-progress-value{background:linear-gradient(90deg,#7bd9c7,#3c9e8b)}details{border-top:1px solid #f0ebf6;padding-top:17px;margin-top:23px;font-size:11px;color:#93869f}summary{cursor:pointer}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#f6f3fb;padding:15px;border-radius:8px;line-height:1.7}.explore-heading{display:flex;align-items:center;gap:12px;margin:32px 0 18px}.explore-heading h2{margin:0}.explore-heading span{color:#9585a7;font-size:12px}.tabs{display:flex;gap:5px;flex-wrap:wrap;margin:0 0 18px;padding:5px;background:#ebe6f5;border-radius:12px;width:fit-content}.tabs button{background:none;border-color:transparent;padding:10px 22px;color:#82728f;font-weight:600}.tabs button[aria-selected=true]{background:#fff;color:#6c42c0;box-shadow:0 2px 6px #30204312}#search{padding-left:18px;background:#fff}#count{border:1px solid #e3daf0;background:#eee8fa;color:#7654ac;padding:7px 10px;border-radius:7px;font-size:11px}.posts{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}.post{position:relative;display:flex;flex-direction:column;background:white;border:1px solid #e7e0ef;border-radius:16px;padding:21px;min-height:240px;transition:transform .2s,box-shadow .2s}.post:hover{transform:translateY(-4px);box-shadow:0 12px 24px #36234e0d}.post>span:first-child{width:fit-content;background:#f1e8ff;color:#8456be;font-size:9px;letter-spacing:1.5px;font-weight:700;border-radius:5px;padding:6px 9px}.post>p{white-space:pre-wrap;overflow-wrap:anywhere;line-height:1.7;font-size:13px}.post>p:nth-child(2){flex:1}.post>p.muted{font-size:11px;color:#8f849b}.post>.badge{align-self:flex-start;font-size:9px;max-width:100%}.post>p:last-child{border-top:1px solid #f0ecf5;padding-top:13px;margin-bottom:0;font-size:11px;font-weight:650}.tablewrap{overflow:auto;background:white;border:1px solid #e7dfef;border-radius:16px}table{width:100%;border-collapse:collapse}td,th{text-align:left;padding:16px 22px;border-bottom:1px solid #f0eaf7;font-size:13px}th{font-size:10px;letter-spacing:1px;text-transform:uppercase;color:#9074af;background:#f5f0fc}tbody tr:hover{background:#faf7ff}td:first-child{font-weight:600}td:first-child:before{content:"@";display:inline-grid;place-items:center;width:28px;height:28px;background:#ece1fb;color:#9365c6;border-radius:9px;margin-right:12px;font-weight:700}td a{font-size:11px}.empty{padding:60px 20px;text-align:center;color:#8a7b99;background:#ffffff80;border:1px dashed #d6c7e9;border-radius:16px;font-size:13px}.pagination{display:flex;gap:16px;justify-content:center;align-items:center;margin:26px;font-size:12px;color:#9b8ba9}.pagination button{font-size:11px;padding:8px 13px}footer{border-top:1px solid #e6dfef;padding:22px 0;margin:30px 0 0;color:#9b8da9;font-size:10px;line-height:1.8}
@media(min-width:1400px){.hero-art{margin-right:80px}}
@media(max-width:950px){.posts{grid-template-columns:repeat(2,minmax(0,1fr))}.metric strong{font-size:26px}.metric{padding:20px 16px}.hero-art{margin-right:0}.columns{grid-template-columns:minmax(0,1fr) minmax(0,1.5fr)}}
@media(max-width:650px){header{padding:22px 20px 58px}.hero{padding-top:30px}.hero-art{display:none}h1{letter-spacing:-1px}main{padding:0 16px}.runbar{gap:10px;padding:14px}.runbar label{width:100%}#run{flex-basis:100%}#load,.download{flex:1;text-align:center;font-size:11px}.metrics{grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}.metric strong{font-size:25px}.metric{min-height:142px;padding:18px 14px}.metric>span:first-child{font-size:11px}.columns,.posts{grid-template-columns:1fr}.panel{padding:22px}.tabs{width:100%;flex-wrap:nowrap}.tabs button{flex:1;padding:10px 8px;font-size:12px}.explore-heading{gap:10px}.explore-heading span{font-size:10px}#sort{max-width:65%}.local{font-size:10px}.post{min-height:220px}}
@media(prefers-reduced-motion:reduce){*{transition:none!important}}

.collection-counts{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;margin:28px 0}.collection-counts div{border-radius:13px;padding:18px 12px;background:#f0e9fb;text-align:center}.collection-counts div:nth-child(2){background:#dff5ef}.collection-counts div:nth-child(3){background:#ffede3}.collection-counts strong{display:block;font-size:26px;color:#54416c}.collection-counts span{font-size:11px;color:#736282}.post{padding:0;overflow:hidden;min-height:340px}.post>p,.post>span:first-child{margin-left:18px;margin-right:18px}.post>span:first-child{margin-top:18px;order:0}.post .preview{display:block;order:-1;background:#eae2f4;height:230px;flex-shrink:0;overflow:hidden}.preview img{display:block;width:100%;height:100%;object-fit:contain;background:#1f172b}.preview-empty{order:-1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:10px;height:210px;background:linear-gradient(135deg,#eee3ff,#fce6e2);color:#9b7bad;font-size:11px}.preview-empty span{font-size:43px;color:#b79acc}.post>p:last-child{padding-bottom:17px}.post p{margin-top:9px;margin-bottom:9px}.post:hover{transform:translateY(-3px)}

/* Media gallery using the original light palette. */
.post .preview{height:auto;aspect-ratio:4/5}.preview img{object-fit:contain;background:#f1edf7}.post>.card-actions{display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;margin-top:auto}.post>span.muted{background:#f1e8ff;color:#8456be;border-radius:5px;padding:6px 9px;margin:14px 18px 0;align-self:flex-start;font-size:10px}.preview-empty{aspect-ratio:4/5;height:auto}button:disabled{opacity:.45}a:focus-visible,button:focus-visible,input:focus-visible,select:focus-visible{outline:3px solid #9872e2;outline-offset:3px}
.engagement{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;margin:12px 18px}.engagement div{background:#f5f0fc;border-radius:8px;padding:10px 6px;text-align:center}.engagement small{display:block;color:#75658a;font-size:10px;margin-bottom:5px}.engagement strong{font-size:12px;color:#54377a}.interaction-note{margin:0 18px 14px;color:#75658a;font-size:11px;line-height:1.6}.comment-thread{font-size:12px;color:#675c79}.comment-thread summary{color:#6950d8;font-weight:600}.comment-entry{padding:12px 0;border-bottom:1px solid #eee8f6}.comment-entry p{white-space:pre-wrap;overflow-wrap:anywhere;line-height:1.6;margin:7px 0}.comment-entry a{display:block;margin-top:6px}</style></head><body><header><div class="topline"><div class="brand"><span class="brandmark" aria-hidden="true">◎</span>scrapy instagram<span style="color:#a987d3;font-weight:400">.</span></div><span class="local">Espacio local</span></div><div class="hero"><div><span class="eyebrow">INSTAGRAM · OBSERVATORIO</span><h1>Una nueva mirada<br>a <em>tus datos.</em></h1></div><div class="hero-art" aria-hidden="true"><div class="orbit"></div><div class="orbit"></div><div class="orbit-core">◎</div><div class="satellite"></div><div class="satellite"></div></div></div></header><main>
<div class="toolbar runbar"><label for="run">Extracción</label><select id="run"></select><a id="download" class="download">Descargar JSON</a></div>
<div id="notice" role="status"></div><section id="metrics" class="metrics"></section><div class="columns"><section class="panel profile-panel"><div class="avatar" id="avatar" aria-hidden="true">@</div><h2 id="profile">Perfil</h2><p class="bio" id="bio"></p><a id="profilelink" target="_blank" rel="noopener noreferrer">Ver en Instagram ↗</a></section><section class="panel collection-panel"><p class="section-kicker">TU COLECCIÓN</p><h2>Publicaciones, en imágenes.</h2><p class="muted">Fotos, descripciones y enlaces de tus publicaciones, reunidos en una galería.</p><div id="collection" class="collection-counts"></div><p class="muted">Los reels muestran una portada o un fotograma. Abre Instagram para reproducirlos.</p></section></div>
<div class="explore-heading"><h2>Explora tu extracción</h2><span>Publicaciones y conexiones</span></div><div class="tabs" role="tablist" aria-label="Datos"><button role="tab" data-tab="posts">Publicaciones</button><button role="tab" data-tab="followers">Seguidores</button><button role="tab" data-tab="following">Seguidos</button></div><div class="toolbar"><input id="search" type="search" aria-label="Buscar en los datos" placeholder="Buscar descripción o usuario…"><select id="sort" aria-label="Orden"><option value="original">Orden de extracción</option><option value="recent">Más recientes / A–Z</option></select><span id="count" class="muted"></span></div><section id="content" style="margin-top:18px"></section><div class="pagination"><button id="prev">Anterior</button><span id="page"></span><button id="next">Siguiente</button></div><footer>scrapy instagram · Colección local de publicaciones y conexiones. Las listas pueden ser parciales.</footer></main>
<script>
'use strict';
const runs=/* DATA */[];
const $=id=>document.getElementById(id);
let data={}, tab='posts', page=0, downloadUrl;
function node(tag,text,className){const element=document.createElement(tag);if(text!==undefined)element.textContent=text;if(className)element.className=className;return element;}
function safeURL(value){try{const url=new URL(value);return url.protocol==='https:'&&['instagram.com','www.instagram.com'].includes(url.hostname)?url.href:null;}catch{return null;}}
function link(url,label){const element=node('a',label);const safe=safeURL(url);if(safe){element.href=safe;element.target='_blank';element.rel='noopener noreferrer';}return element;}
function rows(key){return Array.isArray(data[key])?data[key].filter(item=>item&&typeof item==='object'):[];}
function formatDate(value){const date=new Date(value);return value&&!isNaN(date)?date.toLocaleDateString('es'):'Fecha no disponible';}
function metric(label,value,note){const element=node('div',undefined,'metric');element.append(node('span',label,'muted'),node('strong',typeof value==='number'?new Intl.NumberFormat('es-EC').format(value):String(value)),node('span',note,'muted'));$('metrics').append(element);}
function previewURL(value){return typeof value==='string'&&/^data:image\/(jpeg|png|webp);base64,[A-Za-z0-9+/=]+$/.test(value)?value:null;}
function selectRun(){
 data=runs[$('run').value]?.data||{};page=0;
 const profile=data.profile||{},posts=rows('posts'),captured=posts.filter(post=>previewURL(post.preview)).length;
 $('metrics').replaceChildren();
 metric('Publicaciones',posts.length,'En tu colección');
 metric('Seguidores del perfil',profile.followers_total??profile.followers_visible??'Sin dato',`${rows('followers').length} perfiles guardados`);
 metric('Seguidos del perfil',profile.following_total??profile.following_visible??'Sin dato',`${rows('following').length} perfiles guardados`);
 metric('Imágenes guardadas',captured,formatDate(data.resumed_utc||data.extracted_utc));
 $('profile').textContent=profile.username?'@'+profile.username:'Sin perfil';
 $('avatar').textContent=(profile.username||'@').slice(0,1).toUpperCase();
 $('bio').textContent=profile.bio||'Biografía no disponible.';
 $('profilelink').removeAttribute('href');const url=safeURL(profile.url);if(url)$('profilelink').href=url;
 $('collection').replaceChildren();
 for(const [value,label] of [[posts.length,'Publicaciones'],[captured,'Imágenes'],[posts.filter(post=>post.url?.includes('/reel/')).length,'Reels']]){const element=node('div');element.append(node('strong',String(value)),node('span',label));$('collection').append(element);}
 $('notice').textContent=runs.length?'Tu colección de publicaciones y conexiones. Las listas pueden ser parciales.':'Ejecuta el scraper para generar tu colección automáticamente.';
 if(downloadUrl)URL.revokeObjectURL(downloadUrl);downloadUrl=URL.createObjectURL(new Blob([JSON.stringify(data,null,2)],{type:'application/json'}));$('download').href=downloadUrl;$('download').download='data.json';render();
}
function countText(value,approximate=false){return typeof value==='number'&&Number.isFinite(value)&&value>=0?(approximate?'≈ ':'')+new Intl.NumberFormat('es-EC').format(value):'No disponible';}
function render(){
 document.querySelectorAll('[data-tab]').forEach(button=>button.setAttribute('aria-selected',String(button.dataset.tab===tab)));
 const query=$('search').value.toLocaleLowerCase();
 let items=rows(tab).filter(item=>String(tab==='posts'?(item.caption||'')+' '+(item.url||''):item.username||'').toLocaleLowerCase().includes(query));
 if($('sort').value==='recent')items.sort((first,second)=>tab==='posts'?(Date.parse(second.date)||0)-(Date.parse(first.date)||0):String(first.username).localeCompare(String(second.username)));
 const pages=Math.max(1,Math.ceil(items.length/12));page=Math.min(page,pages-1);
 $('count').textContent=items.length+' resultados';$('page').textContent=`${page+1} / ${pages}`;$('prev').disabled=page===0;$('next').disabled=page>=pages-1;
 const root=$('content');root.replaceChildren();if(!items.length){root.append(node('div','No hay registros para esta vista o búsqueda.','empty'));return;}
 const visible=items.slice(page*12,page*12+12);
 if(tab==='posts'){
  const grid=node('div',undefined,'posts');
  for(const post of visible){
   const card=node('article',undefined,'post'),imageURL=previewURL(post.preview);
   if(imageURL){const anchor=link(post.url);anchor.className='preview';const image=node('img');image.src=imageURL;image.alt=post.caption?'Imagen de la publicación: '+post.caption.slice(0,120):'Imagen de la publicación';image.loading='lazy';anchor.append(image);card.append(anchor);}
   else{const placeholder=node('div',undefined,'preview-empty');placeholder.append(node('span','◎'),node('small','Imagen pendiente de extracción'));card.append(placeholder);}
   card.append(node('span',post.url?.includes('/reel/')?'REEL':'PUBLICACIÓN','muted'),node('p',post.caption||'Sin descripción disponible.'),node('p',formatDate(post.date),'muted'));
   const engagement=node('div',undefined,'engagement');
   for(const [key,label] of [['likes','Likes'],['comments','Comentarios'],['reposts','Reposts']]){const cell=node('div');cell.append(node('small',label),node('strong',countText(post[key],post.interaction_approximations?.[key])));engagement.append(cell);}card.append(engagement);
   const counters=['likes','comments','reposts'],known=counters.map(key=>post[key]).filter(value=>typeof value==='number'&&Number.isFinite(value)&&value>=0);
   const total=known.length?known.reduce((sum,value)=>sum+value,0):null;
   const totalLabel=known.length===3?'Interacciones · likes + comentarios + reposts: ':'Interacciones observadas · suma parcial: ';
   card.append(node('div',totalLabel+countText(total,counters.some(key=>post.interaction_approximations?.[key]))+(post.interactions_checked_utc?' · Consultado '+formatDate(post.interactions_checked_utc):' · Pendiente de extracción'),'interaction-note'));
   const comments=Array.isArray(post.comments_list)?post.comments_list.filter(comment=>comment&&typeof comment.text==='string'&&comment.text.trim()):[];
   const thread=node('details',undefined,'comment-thread');thread.append(node('summary',`Comentarios guardados (${comments.length})`));
   if(!comments.length)thread.append(node('p','No se recuperaron textos de comentarios en esta extracción.','muted'));
   for(const comment of comments){const entry=node('div',undefined,'comment-entry');entry.append(node('strong',comment.username?'@'+comment.username:'Usuario no disponible'),node('p',comment.text));if(comment.date)entry.append(node('small',formatDate(comment.date)));if(comment.url)entry.append(link(comment.url,'Ver comentario ↗'));thread.append(entry);}card.append(thread);
   const action=node('p',undefined,'card-actions');if(imageURL){const save=node('a','Descargar imagen');save.href=imageURL;save.download=(post.url?.split('/').filter(Boolean).pop()||'publication')+'.'+(imageURL.startsWith('data:image/png')?'png':imageURL.startsWith('data:image/webp')?'webp':'jpg');action.append(save);}action.append(link(post.url,'Instagram ↗'));card.append(action);grid.append(card);
  }root.append(grid);
 }else{
  const wrap=node('div',undefined,'tablewrap'),table=node('table'),head=node('thead'),heading=node('tr');heading.append(node('th','Usuario'),node('th','Perfil'));head.append(heading);table.append(head);
  const body=node('tbody');for(const item of visible){const row=node('tr'),cell=node('td');cell.append(link(item.url,'Ver perfil ↗'));row.append(node('td','@'+item.username),cell);body.append(row);}table.append(body);wrap.append(table);root.append(wrap);
 }
}
function options(){ $('run').replaceChildren();runs.forEach((run,index)=>{const option=node('option',(run.data.profile?.username||'Sin perfil')+' · '+run.name);option.value=index;$('run').append(option);});selectRun();}
$('run').onchange=selectRun;
document.querySelectorAll('[data-tab]').forEach(button=>button.onclick=()=>{tab=button.dataset.tab;page=0;render();});
$('search').oninput=()=>{page=0;render();};$('sort').onchange=()=>{page=0;render();};
$('prev').onclick=()=>{page--;render();};$('next').onclick=()=>{page++;render();};
options();
</script></body></html>
"""


def generate_dashboard(results=None, output=BASE / 'dashboard.html'):
    roots = [results] if results is not None else [BASE / 'results', BASE / 'resultados']
    runs = []
    for root in roots:
        for file in root.glob('*/data.json'):
            try:
                data = json.loads(file.read_text(encoding='utf-8'))
                if not isinstance(data, dict) or not isinstance(data.get('posts'), list):
                    continue
                for post in data['posts']:
                    post.pop('preview', None)
                    if post.get('screenshot'):
                        image = (file.parent / post['screenshot']).resolve()
                        if image.is_relative_to(file.parent.resolve()) and image.suffix.lower() in {'.jpg', '.jpeg', '.png', '.webp'} and image.is_file():
                            mime = {'.png': 'png', '.webp': 'webp'}.get(image.suffix.lower(), 'jpeg')
                            post['preview'] = f'data:image/{mime};base64,' + base64.b64encode(image.read_bytes()).decode('ascii')
                runs.append({'name': file.parent.name, 'data': data})
            except (OSError, ValueError, TypeError):
                continue
    runs.sort(key=lambda run: run['name'], reverse=True)
    content = json.dumps(runs, ensure_ascii=True).replace('<', '\\u003c')
    output.write_text(TEMPLATE.replace('/* DATA */[]', content), encoding='utf-8')
    return output


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--results', type=Path, help='Directory containing extraction runs.')
    parser.add_argument('--output', type=Path, default=BASE / 'dashboard.html')
    args = parser.parse_args()
    print(generate_dashboard(args.results, args.output))
