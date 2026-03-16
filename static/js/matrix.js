const canvas=document.createElement("canvas")
document.body.appendChild(canvas)

canvas.style.position="fixed"
canvas.style.top=0
canvas.style.left=0
canvas.style.zIndex=-1

const ctx=canvas.getContext("2d")

canvas.width=window.innerWidth
canvas.height=window.innerHeight

const letters="01DEEPSHIELD#@$%"
const fontSize=16
const columns=canvas.width/fontSize

const drops=[]

for(let i=0;i<columns;i++){
drops[i]=Math.random()*canvas.height
}

function draw(){

ctx.fillStyle="rgba(0,0,0,0.05)"
ctx.fillRect(0,0,canvas.width,canvas.height)

ctx.fillStyle="#ff0000"
ctx.font=fontSize+"px monospace"

for(let i=0;i<drops.length;i++){

const text=letters[Math.floor(Math.random()*letters.length)]

ctx.fillText(text,i*fontSize,drops[i]*fontSize)

if(drops[i]*fontSize>canvas.height && Math.random()>0.95){
drops[i]=0
}

drops[i]++

}

}

setInterval(draw,33)