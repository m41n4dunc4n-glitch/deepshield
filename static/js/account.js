document.querySelectorAll(".delete-btn").forEach(btn => {

btn.addEventListener("click", function(){

const id = this.dataset.id

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

this.closest("tr").remove()

}

})

})

})