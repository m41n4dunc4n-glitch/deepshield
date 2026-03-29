let type = "image"
let scan = null

const fileInput = document.getElementById("file")
const preview = document.getElementById("preview")
const drop = document.getElementById("drop")

const analyzeBtn = document.getElementById("analyzeBtn")
const comingSoonText = document.getElementById("comingSoonText")

// ---------------- TYPE SWITCH ----------------
function selectType(t){
    type = t

    const msg = document.getElementById("upload-message")
    const formats = document.getElementById("formats")
    const textBox = document.getElementById("text-mode")

    preview.innerHTML = ""
    fileInput.value = ""

    msg.style.display = "block"
    formats.style.display = "block"
    textBox.style.display = "none"

    // TEXT MODE
    if(t === "text"){
        msg.style.display = "none"
        formats.style.display = "none"
        textBox.style.display = "block"
    }

    // IMAGE
    else if(t === "image"){
        msg.innerHTML = "Drag & Drop Image<br>or Click to Upload"
        formats.innerText = "(.jpg .jpeg .png)"
    }

    // VIDEO
    else if(t === "video"){
        msg.innerHTML = "Drag & Drop Video<br>or Click to Upload"
        formats.innerText = "(.mp4 .mov .avi)"
    }

    // AUDIO
    else if(t === "audio"){
        msg.innerHTML = "Drag & Drop Audio<br>or Click to Upload"
        formats.innerText = "(.mp3 .wav)"
    }

    // 🔥 DISABLE BUTTON FOR VIDEO/AUDIO
    if(t === "video" || t === "audio"){
        analyzeBtn.disabled = true
        comingSoonText.style.display = "block"
    } else {
        analyzeBtn.disabled = false
        comingSoonText.style.display = "none"
    }
}

// ---------------- FILE PREVIEW ----------------
fileInput.addEventListener("change", function(){

    const file = this.files[0]
    if(!file) return

    const url = URL.createObjectURL(file)

    preview.innerHTML = ""

    document.getElementById("upload-message").style.display = "none"
    document.getElementById("formats").style.display = "none"

    if(type === "image"){
        preview.innerHTML = `<img src="${url}" class="media-preview">`
    }

    if(type === "video"){
        preview.innerHTML = `<video src="${url}" controls class="media-preview"></video>`
    }

    if(type === "audio"){
        preview.innerHTML = `<audio src="${url}" controls class="media-preview"></audio>`
    }
})

// ---------------- ANALYZE ----------------
function analyze(){

    const status = document.getElementById("status")

    // 🚫 BLOCK VIDEO/AUDIO
    if(type === "video" || type === "audio"){
        return
    }

    status.innerText = "Initializing neural network..."

    if(type !== "text" && preview.innerHTML !== ""){
        scan = document.createElement("div")
        scan.className = "scan-line"
        preview.appendChild(scan)
    }

    setTimeout(()=> status.innerText = "Scanning media artifacts...",1500)
    setTimeout(()=> status.innerText = "Detecting GAN fingerprints...",3000)

    const file = fileInput.files[0]
    const textInput = document.getElementById("textinput")
    const text = textInput ? textInput.value : ""

    // -------- TEXT MODE --------
    if(type === "text"){

        if(!text || text.trim() === ""){
            alert("Enter text")
            return
        }

        setTimeout(()=>{

    const labelBox = document.getElementById("label")

    // 🔁 Show analyzing state
    labelBox.innerText = "Analyzing..."

    fetch("/detect", { method:"POST", body:fd })
    .then(r=>r.json())
    .then(d=>{

        if(scan) scan.remove()

        if(type === "image"){
            showHeatmap()
        }

        let msg = `${d.label} (${d.confidence}%)`

        // 🔁 Show retry info if backend sends it
        if(d.retries && d.retries > 0){
            msg += ` ⚠️ Retried ${d.retries}x`
        }

        labelBox.innerText = msg
        document.getElementById("bar").style.width = d.confidence + "%"

        status.innerText = "Analysis Complete"
    })
    .catch(err=>{
        labelBox.innerText = "Error analyzing file"
        status.innerText = "Failed"
    })

},4000)

        return
    }

    // -------- FILE MODE --------
    if(!file){
        alert("Select a file first")
        return
    }

    let fd = new FormData()
    fd.append("file", file)
    fd.append("type", type)

    setTimeout(()=>{

        fetch("/detect",{ method:"POST", body:fd })
        .then(r=>r.json())
        .then(d=>{

            if(scan) scan.remove()

            if(type === "image"){
                showHeatmap()
            }

            document.getElementById("label").innerText = d.label
            document.getElementById("bar").style.width = d.confidence + "%"
            status.innerText = "Analysis Complete"
        })

    },4000)
}

// ---------------- DRAG & DROP FIX ----------------
drop.onclick = () => {
    if(type !== "text"){
        fileInput.click()
    }
}

drop.addEventListener("dragover", (e)=>{
    e.preventDefault()
})

drop.addEventListener("drop", (e)=>{
    e.preventDefault()

    const files = e.dataTransfer.files
    if(files.length > 0){
        fileInput.files = files
        fileInput.dispatchEvent(new Event("change"))
    }
})

// ---------------- HEATMAP ----------------
function showHeatmap(){

    const heat = document.getElementById("heatmap")
    heat.innerHTML = ""

    for(let i=0;i<4;i++){
        const dot = document.createElement("div")
        dot.className = "heatspot"
        dot.style.top = (20 + Math.random()*60) + "%"
        dot.style.left = (20 + Math.random()*60) + "%"
        heat.appendChild(dot)
    }
}