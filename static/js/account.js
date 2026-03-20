document.querySelectorAll(".delete-btn").forEach(btn => {

btn.addEventListener("click", function(){

const id = parseInt(this.dataset.id)

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
    const row = this.closest("tr")
    if(row) row.remove()
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