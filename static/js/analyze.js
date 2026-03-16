let type="image"
let scan

const fileInput=document.getElementById("file")
const preview=document.getElementById("preview")

function selectType(t){

type=t

const msg=document.getElementById("upload-message")
const formats=document.getElementById("formats")
const text=document.getElementById("text-mode")
const preview=document.getElementById("preview")

preview.innerHTML=""
document.getElementById("file").value=""

msg.style.display="block"
formats.style.display="block"

text.style.display="none"

if(t==="image"){
msg.innerHTML="Drag & Drop Image<br>or Click to Upload"
formats.innerText="(.jpg .jpeg .png)"
}

if(t==="video"){
msg.innerHTML="Drag & Drop Video<br>or Click to Upload"
formats.innerText="(.mp4 .mov .avi)"
}

if(t==="audio"){
msg.innerHTML="Drag & Drop Audio<br>or Click to Upload"
formats.innerText="(.mp3 .wav)"
}

if(t==="text"){
msg.innerHTML="Paste text or upload document"
formats.innerText=""
text.style.display="block"
}

}

fileInput.addEventListener("change",function(){

const file=this.files[0]
if(!file) return

const url=URL.createObjectURL(file)

preview.innerHTML=""

document.getElementById("upload-message").style.display="none"
document.getElementById("formats").style.display="none"

if(type==="image"){
preview.innerHTML=`<img src="${url}" class="media-preview">`
}

if(type==="video"){
preview.innerHTML=`<video src="${url}" controls class="media-preview"></video>`
}

if(type==="audio"){
preview.innerHTML=`<audio src="${url}" controls class="media-preview"></audio>`
}

})

function analyze(){

const status=document.getElementById("status")
const preview=document.getElementById("preview")

status.innerText="Initializing neural network..."

if(type !== "text" && preview){

scan=document.createElement("div")
scan.className="scan-line"

preview.appendChild(scan)

}

setTimeout(()=>{
status.innerText="Scanning media artifacts..."
},1500)

setTimeout(()=>{
status.innerText="Detecting GAN fingerprints..."
},3000)

let fd=new FormData()

const file=document.getElementById("file").files[0]
const text=document.getElementById("textinput").value

if(file) fd.append("file",file)
if(text) fd.append("text",text)

fd.append("type",type)

setTimeout(()=>{

fetch("/detect",{method:"POST",body:fd})
.then(r=>r.json())
.then(d=>{

if(scan){
scan.remove()
}

if(type==="image"){
showHeatmap()
}

document.getElementById("label").innerText=d.label
document.getElementById("bar").style.width=d.confidence+"%"
status.innerText="Analysis Complete"

})

},4000)

}



const drop=document.getElementById("drop")

drop.addEventListener("dragover",e=>{
e.preventDefault()
})

drop.addEventListener("drop",e=>{

e.preventDefault()

const files=e.dataTransfer.files

fileInput.files=files

fileInput.dispatchEvent(new Event("change"))

})

function showHeatmap(){

const heat=document.getElementById("heatmap")

heat.innerHTML=""

for(let i=0;i<4;i++){

const dot=document.createElement("div")

dot.className="heatspot"

dot.style.top=(20+Math.random()*60)+"%"
dot.style.left=(20+Math.random()*60)+"%"

heat.appendChild(dot)

}

}

if(type==="text"){
formats.innerText="(.txt .pdf .doc .docx)"
}