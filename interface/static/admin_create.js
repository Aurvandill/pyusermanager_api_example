
async function get_user_data(){

    url = window.location.href.split("/")
    username_url= url.pop().split("?")[0];

    let selfdata = await post("GET",{},"header")

    if(selfdata.admin){
        var perms = await post("GET",{},"perms")

        var perm_holder = document.getElementById("perm_container")
        perm_holder.innerHTML = "<h3>Perms</h3>"

        for(var iter in perms){
            var perm = perms[iter]
            var checkbox_div = document.createElement("div")
            checkbox_div.classList = "checkbox mb-3"
            checkbox_div.innerHTML ="<label><input class=\"change_perms\" autocomplete=\"false\" type=\"checkbox\" value=\""+perm+"\"> "+perm+"</label>"
            perm_holder.appendChild(checkbox_div)
        }
    } else {
        window.location.replace("/?alert_msg=you+are+not+allowed+to+do+this&alert_type=alert-danger")
    }
    
}

get_user_data()

async function create_user(){
    //alert("would change stuff if that would be implemented lol")

    var dict = {}

    username = document.getElementById("username").value
    pw = document.getElementById("password").value
    email = document.getElementById("email").value

    dict["username"] = username
    dict["password"] = pw
    dict["email"] = email

    await handle_perms(dict)

    console.log(dict)

    post("POST",dict,"admin/create")

}


function handle_perms(work_dict){

    perms = document.querySelectorAll(".change_perms")
    perm_dict = {}
    perms.forEach(function(currentValue, currentIndex, listObj){perm_dict[currentValue.value] = currentValue.checked})

    if(Object.keys(perm_dict).length > 0){
        work_dict["perms"] = perm_dict
    }
    
}