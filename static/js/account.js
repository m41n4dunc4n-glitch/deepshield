document.querySelectorAll(".delete-btn").forEach(btn => {

btn.addEventListener("click", function(){

const id = parseInt(this.dataset.id)
const row = this.closest("tr")

// get result BEFORE deleting row
const result = row.querySelector("td:nth-child(4)").innerText.trim()

fetch("/delete_upload",{
method:"POST",
headers:{
"Content-Type":"application/json"
},
body:JSON.stringify({
id:id
})
})
.then(res=>res.json())
.then(data=>{

if(data.status==="deleted"){

    // remove row
    if(row) row.remove()

    // update total
    const total = document.getElementById("total-count")
    total.innerText = parseInt(total.innerText) - 1

    // update specific stat
    if(result === "Fake"){
        const fake = document.getElementById("fake-count")
        fake.innerText = parseInt(fake.innerText) - 1
    }
    else if(result === "Real"){
        const real = document.getElementById("real-count")
        real.innerText = parseInt(real.innerText) - 1
    }
    else{
        const suspicious = document.getElementById("suspicious-count")
        suspicious.innerText = parseInt(suspicious.innerText) - 1
    }

}else{
    alert("Delete failed")
}

})
.catch(err=>{
console.error(err)
alert("Server error")
})

})

})