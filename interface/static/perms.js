
var perm_new = document.getElementById("perm_name")

async function create_perm(){

    var perm_name = perm_new.value
    await post("POST",{"perm":perm_name},"perms")
    update_perms()
}

async function del_perm(del_perm){
    console.log(del_perm.value)
    await post("DELETE",{"perm":del_perm.value},"perms")
    update_perms()
}


async function update_perms(){
    var perm_container = document.getElementById("perm_container")
    //clear ocntainer
    var perms = await post("GET",{},"perms")
    var container = document.createElement("div")
    container.id = "perm_container"
    container.style.maxWidth="400px"
    for(var iter in perms){
        var perm = perms[iter]

        var perm_box = document.createElement("button")
        perm_box.textContent = perm
        perm_box.classList = "btn btn-info"
        perm_box.style.display = "flex"
        perm_box.style.flexDirection = "row"
        perm_box.style.marginBottom = "5px"
        perm_box.style.alignItems="center"
        perm_box.style.width="100%"
        perm_box.style.justifyContent = "space-between"

        let delete_perm = document.createElement("button")
        delete_perm.classList = "btn btn-outline-danger"
        delete_perm.textContent = "Delete"
        delete_perm.style.marginLeft="10px"
        delete_perm.value = perm

        //delete_perm.onclick=function(){del_perm(perm)}
        delete_perm.addEventListener("click",function(){del_perm(delete_perm)})

        perm_box.appendChild(delete_perm)
        container.appendChild(perm_box)

    }
    perm_container.innerHTML = "";
    perm_container.replaceWith(container)
}


update_perms()