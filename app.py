from flask import Flask, request, jsonify, render_template_string, send_file
import yt_dlp
import os
import uuid
import threading
import time
import requests

app = Flask(__name__)

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

jobs = {}
lock = threading.Lock()


HTML = r'''
<!DOCTYPE html>
<html>
<head>

<meta name="viewport"
content="width=device-width,initial-scale=1,maximum-scale=1">

<title>CRASHED DOWNLOADER</title>

<style>

*{
 box-sizing:border-box;
}

:root{
 --paper:#f3f0e8;
 --card:#faf8f2;
 --ink:#22231f;
 --muted:#77766f;
 --line:#d8d4c8;
 --accent:#b85c3c;
 --soft:#ebe7dc;
}

html,body{
 margin:0;
 padding:0;
 background:var(--paper);
 color:var(--ink);
 font-family:Georgia,"Times New Roman",serif;
}

body:before{
 content:"";
 position:fixed;
 inset:0;
 pointer-events:none;
 opacity:.12;
 background-image:
 radial-gradient(#777 0.45px,transparent .45px);
 background-size:7px 7px;
}

.app{
 width:min(94%,680px);
 margin:auto;
 padding:25px 0 50px;
}

header{
 display:flex;
 justify-content:space-between;
 align-items:flex-start;
 padding:5px 3px 25px;
 border-bottom:1px solid var(--line);
}

.brand{
 font-size:23px;
 font-weight:bold;
 letter-spacing:-1px;
}

.brand span{
 color:var(--accent);
}

.edition{
 font:9px Arial,sans-serif;
 letter-spacing:1.5px;
 color:var(--muted);
 text-align:right;
}

.intro{
 padding:27px 3px 22px;
}

.intro small{
 font:bold 9px Arial,sans-serif;
 letter-spacing:2px;
 color:var(--accent);
}

.intro h1{
 margin:9px 0 7px;
 font-size:43px;
 line-height:.95;
 letter-spacing:-2px;
}

.intro p{
 margin:0;
 max-width:470px;
 color:var(--muted);
 font:12px Arial,sans-serif;
 line-height:1.55;
}

.search{
 background:var(--card);
 border:1px solid var(--line);
 border-radius:16px;
 padding:10px;
 box-shadow:0 12px 35px #302b2110;
}

.searchrow{
 display:flex;
 gap:7px;
}

input{
 flex:1;
 min-width:0;
 height:49px;
 padding:0 13px;
 border:1px solid var(--line);
 border-radius:10px;
 background:white;
 color:var(--ink);
 outline:none;
 font:13px Arial,sans-serif;
}

input:focus{
 border-color:var(--accent);
}

.paste{
 width:70px;
 border:1px solid var(--line);
 border-radius:10px;
 background:var(--soft);
 color:#55534d;
 font:bold 9px Arial,sans-serif;
}

.analyze{
 width:100%;
 height:49px;
 margin-top:7px;
 border:0;
 border-radius:10px;
 background:var(--ink);
 color:white;
 font:bold 10px Arial,sans-serif;
 letter-spacing:1px;
}

.analyze:active,
.download:active,
.tool:active{
 transform:scale(.98);
}

.note{
 text-align:center;
 color:#99958b;
 margin-top:9px;
 font:8px Arial,sans-serif;
 letter-spacing:1px;
}

.result{
 display:none;
 margin-top:17px;
}

.card{
 background:var(--card);
 border:1px solid var(--line);
 border-radius:16px;
 padding:15px;
 margin-top:11px;
 box-shadow:0 9px 25px #302b2109;
}

.preview{
 padding:0;
 overflow:hidden;
}

.thumb{
 width:100%;
 aspect-ratio:16/9;
 object-fit:cover;
 display:block;
 background:#ddd;
}

.info{
 padding:14px;
}

.title{
 font-size:19px;
 line-height:1.25;
 font-weight:bold;
}

.meta{
 margin-top:6px;
 color:var(--muted);
 font:10px Arial,sans-serif;
}

.heading{
 display:flex;
 justify-content:space-between;
 align-items:center;
 margin-bottom:12px;
}

.heading strong{
 font:bold 10px Arial,sans-serif;
 letter-spacing:1.3px;
}

.heading span{
 color:#99958b;
 font:8px Arial,sans-serif;
}

.tabs{
 display:grid;
 grid-template-columns:1fr 1fr;
 gap:5px;
 background:var(--soft);
 padding:4px;
 border-radius:11px;
}

.tab{
 height:38px;
 border:0;
 border-radius:8px;
 background:transparent;
 color:#77736b;
 font:bold 10px Arial,sans-serif;
}

.tab.active{
 background:white;
 color:var(--ink);
 box-shadow:0 2px 8px #00000012;
}

.mode{
 display:none;
 padding-top:14px;
}

.mode.active{
 display:block;
}

.label{
 margin-bottom:7px;
 color:#89857c;
 font:bold 8px Arial,sans-serif;
 letter-spacing:1.3px;
}

.qualities{
 display:grid;
 grid-template-columns:repeat(4,1fr);
 gap:6px;
}

.q{
 height:48px;
 border:1px solid var(--line);
 border-radius:9px;
 background:#f1eee6;
 color:#66635c;
 font:bold 10px Arial,sans-serif;
}

.q small{
 display:block;
 margin-top:3px;
 color:#99958c;
 font:7px Arial,sans-serif;
}

.q.selected{
 background:var(--ink);
 border-color:var(--ink);
 color:white;
}

.q.selected small{
 color:#c7c4bc;
}

.download{
 width:100%;
 height:49px;
 margin-top:9px;
 border:0;
 border-radius:10px;
 background:var(--accent);
 color:white;
 font:bold 10px Arial,sans-serif;
 letter-spacing:.8px;
}

.subnote{
 display:flex;
 justify-content:space-between;
 margin-top:8px;
 color:#99958b;
 font:8px Arial,sans-serif;
}

.extra{
 border-top:1px solid var(--line);
 margin-top:13px;
 padding-top:13px;
}

.extra button{
 width:100%;
 height:42px;
 border:1px solid var(--line);
 border-radius:9px;
 background:var(--soft);
 color:#656159;
 font:bold 9px Arial,sans-serif;
}

.tools{
 display:none;
 grid-template-columns:1fr 1fr;
 gap:6px;
 margin-top:6px;
}

.tools.open{
 display:grid;
}

.tool{
 height:40px!important;
 background:white!important;
}

.description{
 display:none;
 margin-top:7px;
 padding:11px;
 max-height:160px;
 overflow:auto;
 border:1px solid var(--line);
 border-radius:9px;
 background:#f1eee6;
 color:#69665f;
 font:10px Arial,sans-serif;
 line-height:1.55;
 white-space:pre-wrap;
}

.downloadBox{
 display:none;
}

.downloadBox.show{
 display:block;
}

.progressTop{
 display:flex;
 justify-content:space-between;
 font:bold 9px Arial,sans-serif;
}

.bar{
 height:7px;
 margin-top:10px;
 border-radius:10px;
 background:#dfdbd0;
 overflow:hidden;
}

.fill{
 width:0%;
 height:100%;
 background:var(--accent);
 transition:.25s;
}

.progressBottom{
 display:flex;
 justify-content:space-between;
 align-items:center;
 margin-top:8px;
}

.percent{
 font:bold 18px Arial,sans-serif;
}

.cancel{
 height:30px;
 padding:0 11px;
 border:1px solid var(--line);
 border-radius:7px;
 background:var(--soft);
 color:#666;
 font:bold 8px Arial,sans-serif;
}

.history{
 display:none;
 margin-top:25px;
}

.historyHead{
 display:flex;
 justify-content:space-between;
 font:bold 9px Arial,sans-serif;
 letter-spacing:1px;
}

.clear{
 color:var(--accent);
 cursor:pointer;
}

.historyItem{
 display:flex;
 gap:9px;
 align-items:center;
 padding:9px 0;
 border-bottom:1px solid var(--line);
 cursor:pointer;
}

.historyItem img{
 width:60px;
 height:39px;
 object-fit:cover;
 border-radius:6px;
 background:#ddd;
}

.historyTitle{
 min-width:0;
 font:11px Arial,sans-serif;
 white-space:nowrap;
 overflow:hidden;
 text-overflow:ellipsis;
}

.historySub{
 color:#99958b;
 font:8px Arial,sans-serif;
 margin-top:4px;
}

footer{
 text-align:center;
 margin-top:35px;
 color:#9b978d;
 font:8px Arial,sans-serif;
 letter-spacing:2px;
}

.toast{
 position:fixed;
 left:50%;
 bottom:18px;
 transform:translate(-50%,30px);
 opacity:0;
 background:var(--ink);
 color:white;
 padding:10px 14px;
 border-radius:9px;
 font:bold 9px Arial,sans-serif;
 transition:.25s;
 z-index:50;
}

.toast.show{
 opacity:1;
 transform:translate(-50%,0);
}

@media(max-width:450px){

 .app{
  width:94%;
 }

 .intro h1{
  font-size:38px;
 }

 .qualities{
  grid-template-columns:repeat(2,1fr)!important;
 }

 .searchrow{
  display:grid;
  grid-template-columns:1fr 70px;
 }

}


.descToggle{
 width:100%;
 height:48px;
 border:1px solid #292929;
 border-radius:12px;
 background:#171717;
 color:#f5f5f5;
 display:flex;
 align-items:center;
 justify-content:space-between;
 padding:0 14px;
 font:bold 10px Arial,sans-serif;
 letter-spacing:1px;
 transition:.2s;
}

.descToggle:hover{
 background:#202020;
}

#descArrow{
 font-size:18px;
 font-weight:normal;
}

.description{
 margin-top:8px;
 background:#111;
 border:1px solid #292929;
 color:#aaa;
 border-radius:12px;
}

.extra{
 border-top:0!important;
 margin-top:14px!important;
 padding-top:0!important;
}

.tools{
 background:#111;
 border:1px solid #292929;
 border-radius:13px;
 padding:7px;
 gap:6px;
}

.tool{
 background:#1b1b1b!important;
 border:1px solid #303030!important;
 color:#ddd!important;
 border-radius:9px!important;
}

.tool:hover{
 background:#242424!important;
 border-color:#555!important;
}

.qualities{
 grid-template-columns:repeat(4,1fr)!important;
}

.q{
 background:#161616!important;
 border-color:#292929!important;
 color:#aaa!important;
}

.q small{
 color:#666!important;
}

.q.selected{
 background:#c7ff2e!important;
 color:#101010!important;
 border-color:#c7ff2e!important;
}

.q.selected small{
 color:#333!important;
}

.tabs{
 background:#111!important;
 border:1px solid #292929;
}

.tab{
 color:#777!important;
}

.tab.active{
 background:#c7ff2e!important;
 color:#111!important;
}

</style>

</head>

<body>

<div class="app">

<header>

 <div class="brand">
  CRASHED <span>DOWNLOADER</span>
 </div>

 <div class="edition">
  SIMPLE MEDIA<br>
  UTILITY
 </div>

</header>

<section class="intro">

 <small>DOWNLOAD WITHOUT THE NOISE</small>

 <h1>Your media.<br>One place.</h1>

 <p>
 Paste a link, inspect the video, choose a quality,
 and download. Nothing unnecessary on the screen.
 </p>

</section>

<div class="search">

 <div class="searchrow">

  <input
   id="url"
   placeholder="Paste video link..."
   autocomplete="off"
  >

  <button
   class="paste"
   onclick="pasteURL()"
  >
   PASTE
  </button>

 </div>

 <button
  class="analyze"
  id="analyze"
  onclick="analyze()"
 >
  ANALYZE LINK
 </button>

</div>

<div class="note">
 VIDEO • AUDIO • THUMBNAIL
</div>


<section
 class="result"
 id="result"
>

<div class="card preview">

 <img
  id="thumb"
  class="thumb"
 >

 <div class="info">

  <div
   id="title"
   class="title"
  ></div>

  <div
   id="meta"
   class="meta"
  ></div>

 </div>

</div>


<div class="card">

 <div class="heading">

  <strong>DOWNLOAD</strong>

  <span>SELECT FORMAT</span>

 </div>


 <div class="tabs">

  <button
   id="videoTab"
   class="tab active"
   onclick="mode('video')"
  >
   VIDEO
  </button>

  <button
   id="audioTab"
   class="tab"
   onclick="mode('audio')"
  >
   MP3
  </button>

 </div>


 <div
  id="videoMode"
  class="mode active"
 >

  <div class="label">
   AVAILABLE VIDEO QUALITY
  </div>

  <div
   id="qualities"
   class="qualities"
  ></div>

  <button
   class="download"
   onclick="startDownload('video')"
  >
   DOWNLOAD VIDEO
  </button>

  <div class="subnote">

   <span>
    MP4 • VIDEO + AUDIO
   </span>

   <span
    id="selectedText"
   >
    BEST
   </span>

  </div>

 </div>


 <div
  id="audioMode"
  class="mode"
 >

  <div class="label">
   AUDIO QUALITY
  </div>

  <div class="qualities">

   <button class="q selected">
    320K
    <small>HIGH</small>
   </button>

   <button class="q">
    192K
    <small>GOOD</small>
   </button>

  </div>

  <button
   class="download"
   onclick="startDownload('audio')"
  >
   DOWNLOAD MP3
  </button>

  <div class="subnote">

   <span>
    MP3 • AUDIO ONLY
   </span>

   <span>
    320 KBPS
   </span>

  </div>

 </div>


 <div class="extra">

  <button
   id="toolsToggle"
   onclick="toggleTools()"
  >
   SHOW EXTRA TOOLS
  </button>

  <div
   id="tools"
   class="tools"
  >

   <button
    class="tool"
    onclick="downloadThumbnail()"
   >
    SAVE THUMBNAIL
   </button>

   <button
    class="tool"
    onclick="copyValue(current.title)"
   >
    COPY TITLE
   </button>

   <button
    class="tool"
    onclick="copyValue(current.description)"
   >
    COPY DESCRIPTION
   </button>

   <button
    class="tool"
    onclick="copyValue(current.url)"
   >
    COPY LINK
   </button>

  </div>

 </div>

</div>


<div class="card">

 <div class="heading">

  <strong>DESCRIPTION</strong>

  <span>OPTIONAL</span>

 </div>

 <button
  id="descriptionButton"
  class="descToggle"
  onclick="toggleDescription()"
 >
  <span>DESCRIPTION</span>
  <span id="descArrow">＋</span>
 </button>

 <div
  id="description"
  class="description"
 ></div>

</div>


<div
 id="downloadBox"
 class="card downloadBox"
>

 <div class="progressTop">

  <span id="downloadStatus">
   PREPARING...
  </span>

  <span id="eta">
   --
  </span>

 </div>

 <div class="bar">

  <div
   id="fill"
   class="fill"
  ></div>

 </div>

 <div class="progressBottom">

  <div
   id="percent"
   class="percent"
  >
   0%
  </div>

  <button
   class="cancel"
   onclick="cancelDownload()"
  >
   CANCEL
  </button>

 </div>

</div>


</section>


<section
 id="history"
 class="history"
>

 <div class="historyHead">

  <span>RECENT LINKS</span>

  <span
   class="clear"
   onclick="clearHistory()"
  >
   CLEAR
  </span>

 </div>

 <div id="historyList"></div>

</section>


<footer>
 CRASHED // DOWNLOADER
</footer>

</div>


<div
 id="toast"
 class="toast"
></div>


<script>

let current={};
let selectedQuality="best";
let job=null;
let pollTimer=null;

const $=id=>document.getElementById(id);


function toast(text){

 const box=$("toast");

 box.textContent=text;

 box.classList.add("show");

 setTimeout(()=>{
  box.classList.remove("show");
 },2200);

}


async function pasteURL(){

 try{

  $("url").value=
   await navigator.clipboard.readText();

  toast("Link pasted");

 }catch(e){

  toast("Paste the link manually");

 }

}


async function analyze(){

 const url=
  $("url").value.trim();

 if(!url){

  toast("Paste a link first");
  return;

 }

 const button=$("analyze");

 button.textContent="READING...";
 button.disabled=true;

 try{

  const response=
   await fetch(
    "/info",
    {
     method:"POST",
     headers:{
      "Content-Type":
      "application/json"
     },
     body:JSON.stringify({
      url:url
     })
    }
   );

  const data=
   await response.json();

  if(data.error){
   throw Error(data.error);
  }

  current=data;

  $("thumb").src=
   data.thumbnail||"";

  $("title").textContent=
   data.title||"Untitled";

  $("meta").textContent=
   (data.uploader||"Unknown")+
   (data.duration?
    " • "+data.duration:"")+
   (data.views?
    " • "+
    Number(data.views)
    .toLocaleString()+
    " views":"");

  $("description").textContent=
   data.description||
   "No description available.";

  buildQualities(
   data.qualities||[]
  );

  $("result").style.display=
   "block";

  saveHistory(data);

  toast("Link ready");

  setTimeout(()=>{

   $("result").scrollIntoView({
    behavior:"smooth",
    block:"start"
   });

  },100);

 }catch(e){

  toast(
   "Couldn't read this link"
  );

 }

 button.textContent=
  "ANALYZE LINK";

 button.disabled=false;

}


function buildQualities(list){

 const box=
  $("qualities");

 box.innerHTML="";

 selectedQuality="best";

 addQuality(
  box,
  "BEST",
  "best",
  "AUTO"
 );

 list.forEach(q=>{

  addQuality(
   box,
   q+"p",
   String(q),
   "UP TO "+q+"P"
  );

 });

 updateSelectedText();

}


function addQuality(
 box,
 label,
 value,
 sub
){

 const button=
  document.createElement("button");

 button.className=
  "q"+
  (
   value==="best"
   ?" selected"
   :""
  );

 button.innerHTML=
  label+
  "<small>"+
  sub+
  "</small>";

 button.onclick=()=>{

  document
   .querySelectorAll(
    "#qualities .q"
   )
   .forEach(x=>{
    x.classList.remove(
     "selected"
    );
   });

  button.classList.add(
   "selected"
  );

  selectedQuality=
   value;

  updateSelectedText();

 };

 box.appendChild(button);

}


function updateSelectedText(){

 $("selectedText").textContent=
  selectedQuality==="best"
  ?"BEST"
  :selectedQuality+"P";

}


function mode(which){

 $("videoTab")
  .classList.toggle(
   "active",
   which==="video"
  );

 $("audioTab")
  .classList.toggle(
   "active",
   which==="audio"
  );

 $("videoMode")
  .classList.toggle(
   "active",
   which==="video"
  );

 $("audioMode")
  .classList.toggle(
   "active",
   which==="audio"
  );

}


function toggleTools(){

 const tools=
  $("tools");

 const open=
  tools.classList.toggle(
   "open"
  );

 $("toolsToggle")
  .textContent=
  open
  ?"HIDE EXTRA TOOLS"
  :"SHOW EXTRA TOOLS";

}


function toggleDescription(){

 const box=$("description");
 const arrow=$("descArrow");

 const open=
  box.style.display==="block";

 box.style.display=
  open?"none":"block";

 arrow.textContent=
  open?"＋":"−";

}


function startDownload(type){

 if(!current.url){

  toast(
   "Analyze a link first"
  );

  return;

 }

 $("downloadBox")
  .classList.add("show");

 $("fill").style.width="0%";

 $("percent").textContent=
  "0%";

 $("downloadStatus")
  .textContent=
  type==="audio"
  ?"PREPARING MP3..."
  :"PREPARING VIDEO...";

 $("eta").textContent="--";


 fetch(
  "/start",
  {
   method:"POST",
   headers:{
    "Content-Type":
    "application/json"
   },
   body:JSON.stringify({
    url:current.url,
    type:type,
    quality:
     type==="audio"
     ?"320"
     :selectedQuality
   })
  }
 )
 .then(r=>r.json())
 .then(data=>{

  if(data.error){
   throw Error(data.error);
  }

  job=data.id;

  poll();

 })
 .catch(()=>{

  $("downloadBox")
   .classList.remove("show");

  toast(
   "Download couldn't start"
  );

 });

}


async function poll(){

 if(!job)return;

 try{

  const data=
   await(
    await fetch(
     "/status/"+job
    )
   ).json();

  const p=
   Math.min(
    100,
    Number(
     data.percent||0
    )
   );

  $("fill").style.width=
   p+"%";

  $("percent").textContent=
   Math.round(p)+"%";

  $("downloadStatus")
   .textContent=
   data.status||
   "DOWNLOADING...";

  $("eta").textContent=
   data.eta||"--";


  if(
   data.status_code===
   "finished"
  ){

   $("fill").style.width=
    "100%";

   $("percent")
    .textContent="100%";

   $("downloadStatus")
    .textContent=
    "COMPLETE";

   const finishedJob=
    job;

   job=null;

   toast(
    "Download complete"
   );

   setTimeout(()=>{

    location.href=
     "/file/"+finishedJob;

   },300);

   return;

  }


  if(
   data.status_code===
   "error"
  ){

   job=null;

   $("downloadBox")
    .classList.remove(
     "show"
    );

   toast(
    "Download failed"
   );

   return;

  }


  if(
   data.status_code===
   "cancelled"
  ){

   job=null;

   $("downloadBox")
    .classList.remove(
     "show"
    );

   toast(
    "Download cancelled"
   );

   return;

  }

 }catch(e){}


 pollTimer=
  setTimeout(
   poll,
   700
  );

}


async function cancelDownload(){

 if(!job)return;

 await fetch(
  "/cancel/"+job,
  {
   method:"POST"
  }
 );

 toast(
  "Cancelling..."
 );

}


async function copyValue(value){

 try{

  await navigator.clipboard
   .writeText(
    value||""
   );

  toast("Copied");

 }catch(e){

  toast("Copy failed");

 }

}


function downloadThumbnail(){

 if(!current.url){

  toast(
   "Analyze a link first"
  );

  return;

 }

 location.href=
  "/thumbnail?url="+
  encodeURIComponent(
   current.url
  );

}


function saveHistory(data){

 let history=
  JSON.parse(
   localStorage.getItem(
    "crashedHistory"
   )||"[]"
  );

 history=
  history.filter(
   x=>x.url!==data.url
  );

 history.unshift({
  url:data.url,
  title:data.title,
  thumbnail:data.thumbnail
 });

 localStorage.setItem(
  "crashedHistory",
  JSON.stringify(
   history.slice(0,6)
  )
 );

 renderHistory();

}


function renderHistory(){

 const history=
  JSON.parse(
   localStorage.getItem(
    "crashedHistory"
   )||"[]"
  );

 const box=
  $("history");

 const list=
  $("historyList");

 list.innerHTML="";

 if(!history.length){

  box.style.display="none";

  return;

 }

 box.style.display="block";

 history.forEach(item=>{

  const row=
   document.createElement(
    "div"
   );

  row.className=
   "historyItem";

  row.innerHTML=
   '<img src="'+
   (item.thumbnail||"")+
   '">' +
   '<div>' +
   '<div class="historyTitle">'+
   (item.title||"Untitled")+
   '</div>' +
   '<div class="historySub">'+
   'TAP TO REOPEN'+
   '</div>' +
   '</div>';

  row.onclick=()=>{

   $("url").value=
    item.url;

   analyze();

  };

  list.appendChild(row);

 });

}


function clearHistory(){

 localStorage.removeItem(
  "crashedHistory"
 );

 renderHistory();

 toast(
  "History cleared"
 );

}


$("url").addEventListener(
 "keydown",
 e=>{
  if(e.key==="Enter"){
   analyze();
  }
 }
);


renderHistory();

</script>

</body>
</html>
'''


def duration(seconds):

    if not seconds:
        return ""

    seconds=int(seconds)

    h=seconds//3600
    m=(seconds%3600)//60
    s=seconds%60

    if h:
        return f"{h}:{m:02d}:{s:02d}"

    return f"{m}:{s:02d}"


def speed(value):

    if not value:
        return "0 MB/s"

    return f"{value/1048576:.2f} MB/s"


def eta(value):

    if value is None:
        return "--"

    value=int(value)

    if value>=60:
        return f"{value//60}m {value%60}s"

    return f"{value}s"


@app.route("/")
def home():

    return render_template_string(
        HTML
    )


@app.route(
    "/info",
    methods=["POST"]
)
def info():

    try:

        data=request.get_json() or {}

        url=data.get(
            "url",
            ""
        ).strip()

        if not url:
            return jsonify(
                error="URL missing"
            )

        options={
            "quiet":True,
            "skip_download":True,
            "noplaylist":True,"js_runtimes":{"node":{}},"extractor_args":{"youtube":{"player_client":["android_vr"]}}
        }

        with yt_dlp.YoutubeDL(
            options
        ) as ydl:

            x=ydl.extract_info(
                url,
                download=False
            )

        available=set()

        for f in x.get(
            "formats",
            []
        ):

            h=f.get("height")

            if h:

                h=int(h)

                if h in (
                    2160,
                    1440,
                    1080,
                    720,
                    480,
                    360,
                    240,
                    144
                ):

                    available.add(h)

        qualities=sorted(
            available,
            reverse=True
        )

        return jsonify({

            "url":url,

            "title":
            x.get(
                "title",
                "Unknown"
            ),

            "description":
            x.get(
                "description",
                ""
            ),

            "thumbnail":
            x.get(
                "thumbnail",
                ""
            ),

            "uploader":
            x.get(
                "uploader",
                "Unknown"
            ),

            "duration":
            duration(
                x.get(
                    "duration"
                )
            ),

            "views":
            x.get(
                "view_count",
                0
            ),

            "qualities":
            qualities

        })

    except Exception:

        return jsonify(
            error=
            "Couldn't read this link"
        )


def worker(
    jid,
    url,
    media_type,
    quality
):

    def hook(d):

        with lock:

            job_data = jobs.get(jid)

            if not job_data:
                return

            if job_data.get(
                "cancel"
            ):

                raise yt_dlp.utils.DownloadCancelled(
                    "Cancelled"
                )

            if d.get(
                "status"
            )=="downloading":

                total=(
                    d.get(
                        "total_bytes"
                    )
                    or
                    d.get(
                        "total_bytes_estimate"
                    )
                    or 0
                )

                downloaded=d.get(
                    "downloaded_bytes",
                    0
                )

                percent=(
                    downloaded/
                    total*
                    100
                    if total
                    else 0
                )

                job_data.update({

                    "percent":
                    percent,

                    "speed":
                    speed(
                        d.get(
                            "speed"
                        )
                    ),

                    "eta":
                    eta(
                        d.get(
                            "eta"
                        )
                    ),

                    "status":
                    "Downloading..."

                })

            elif d.get(
                "status"
            )=="finished":

                job_data[
                    "percent"
                ]=100

                job_data[
                    "status"
                ]="Merging..."


    try:

        output=os.path.join(
            DOWNLOAD_DIR,
            jid+".%(ext)s"
        )


        if media_type=="audio":

            options={

                "format":
                "bestaudio/best",

                "outtmpl":
                output,

                "noplaylist":
                True,

                "progress_hooks":
                [hook],

                "postprocessors":[{

                    "key":
                    "FFmpegExtractAudio",

                    "preferredcodec":
                    "mp3",

                    "preferredquality":
                    quality

                }],

                "retries":
                10,

                "fragment_retries":
                10,

                "concurrent_fragment_downloads":
                4

            }


        else:

            if quality=="best":

                format_selector=(
                    "bestvideo*+bestaudio/"
                    "best"
                )

            else:

                q=int(quality)

                format_selector=(
                    f"bestvideo*[height<={q}]"
                    f"+bestaudio/"
                    f"best[height<={q}]/"
                    f"best"
                )


            options={

                "format":
                format_selector,

                "outtmpl":
                output,

                "merge_output_format":
                "mp4",

                "noplaylist":
                True,

                "js_runtimes":
                {"node":{}},

                "extractor_args":
                {"youtube":{"player_client":["android_vr"]}},

                "progress_hooks":
                [hook],

                "retries":
                10,

                "fragment_retries":
                10,

                "concurrent_fragment_downloads":
                4,

                "continuedl":
                True,

                "nopart":
                False

            }


        with yt_dlp.YoutubeDL(
            options
        ) as ydl:

            info_data = ydl.extract_info(url, download=True)

            filename = ydl.prepare_filename(info_data)


        if media_type=="audio":

            filename=(
                os.path.splitext(
                    filename
                )[0]
                +".mp3"
            )


        if not os.path.exists(
            filename
        ):

            base=os.path.splitext(
                filename
            )[0]

            candidates=[
                base+".mp4",
                base+".mkv",
                base+".webm",
                base+".mp3"
            ]

            for candidate in candidates:

                if os.path.exists(
                    candidate
                ):

                    filename=candidate
                    break


        with lock:

            if jobs[jid].get(
                "cancel"
            ):

                jobs[jid].update({

                    "status_code":
                    "cancelled",

                    "status":
                    "Cancelled"

                })

            elif os.path.exists(
                filename
            ):

                jobs[jid].update({

                    "percent":
                    100,

                    "file":
                    filename,

                    "status_code":
                    "finished",

                    "status":
                    "Complete"

                })

            else:

                jobs[jid].update({

                    "status_code":
                    "error",

                    "status":
                    "File not created"

                })


    except Exception as error:

        with lock:

            if jid in jobs:

                if jobs[jid].get(
                    "cancel"
                ):

                    jobs[jid].update({

                        "status_code":
                        "cancelled",

                        "status":
                        "Cancelled"

                    })

                else:

                    jobs[jid].update({

                        "status_code":
                        "error",

                        "status":
                        "Failed",

                        "error":
                        str(error)

                    })


@app.route(
    "/start",
    methods=["POST"]
)
def start():

    data=request.get_json() or {}

    url=data.get(
        "url",
        ""
    ).strip()

    if not url:

        return jsonify(
            error="URL missing"
        )

    jid=uuid.uuid4().hex

    with lock:

        jobs[jid]={

            "percent":
            0,

            "speed":
            "0 MB/s",

            "eta":
            "--",

            "status":
            "Queued",

            "status_code":
            "running",

            "cancel":
            False,

            "file":
            None

        }


    threading.Thread(

        target=worker,

        args=(

            jid,

            url,

            data.get(
                "type",
                "video"
            ),

            data.get(
                "quality",
                "best"
            )

        ),

        daemon=True

    ).start()


    return jsonify(
        id=jid
    )


@app.route(
    "/status/<jid>"
)
def status(jid):

    with lock:

        data=jobs.get(
            jid
        )

    return jsonify(
        data or
        {
            "error":
            "Job not found"
        }
    )


@app.route(
    "/cancel/<jid>",
    methods=["POST"]
)
def cancel(jid):

    with lock:

        if jid in jobs:

            jobs[jid][
                "cancel"
            ]=True

    return jsonify(
        ok=True
    )


@app.route(
    "/file/<jid>"
)
def file(jid):

    with lock:

        data=jobs.get(
            jid
        )

    if not data:

        return "File not found"

    path=data.get(
        "file"
    )

    if (
        not path
        or
        not os.path.exists(path)
    ):

        return "File not ready"

    if path.endswith(
        ".mp3"
    ):

        name = "CRASHED_AUDIO.mp3"

    else:

        name = "CRASHED_VIDEO.mp4"


    return send_file(

        path,

        as_attachment=True,

        download_name=name

    )


@app.route(
    "/thumbnail"
)
def thumbnail():

    try:

        url=request.args.get(
            "url",
            ""
        ).strip()

        options={

            "quiet":
            True,

            "skip_download":
            True,

            "noplaylist":
            True

        }

        with yt_dlp.YoutubeDL(
            options
        ) as ydl:

            x=ydl.extract_info(
                url,
                download=False
            )

        image=x.get(
            "thumbnail"
        )

        if not image:

            return "Thumbnail unavailable"

        r=requests.get(

            image,

            headers={
                "User-Agent":
                "Mozilla/5.0"
            },

            timeout=20

        )

        r.raise_for_status()

        content=r.headers.get(
            "content-type",
            "image/jpeg"
        ).lower()


        if "png" in content:

            ext=".png"

        elif "webp" in content:

            ext=".webp"

        else:

            ext=".jpg"


        path=os.path.join(

            DOWNLOAD_DIR,

            "CRASHED_THUMBNAIL"
            +ext

        )


        with open(
            path,
            "wb"
        ) as f:

            f.write(
                r.content
            )


        return send_file(

            path,

            as_attachment=True,

            download_name=
            "CRASHED_THUMBNAIL"
            +ext

        )


    except Exception:

        return (
            "Thumbnail download failed"
        )


def cleanup():

    while True:

        try:

            now=time.time()

            for name in os.listdir(
                DOWNLOAD_DIR
            ):

                path=os.path.join(
                    DOWNLOAD_DIR,
                    name
                )

                if (

                    os.path.isfile(
                        path
                    )

                    and

                    now-
                    os.path.getmtime(
                        path
                    )
                    >1800

                ):

                    try:

                        os.remove(
                            path
                        )

                    except:

                        pass

        except:

            pass


        time.sleep(
            600
        )


threading.Thread(
    target=cleanup,
    daemon=True
).start()


if __name__=="__main__":

    app.run(
        host="0.0.0.0",
        port=8080
    )

