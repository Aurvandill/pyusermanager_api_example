var userpage_username = document.getElementById("userpage_username");

function del_user(){

    if (confirm("are ya sure about that?")){
        post("DELETE",{},"user/"+userpage_username.textContent)
    }
}

function* entries(obj) {
    for (let key of Object.keys(obj)) {
      yield [key, obj[key]];
    }
 }

async function get_user_data(){

    url = window.location.href.split("/")
    username_url= url.pop().split("?")[0];

    let data = await post("GET",{},"user/"+username_url)
    let selfdata = await post("GET",{},"header")
    console.log("----------------")
    console.log(data)
    console.log("----------------")

    if(data.username){
        userpage_username.textContent = data.username;

        userpage_avatar = await get_img(data.avatar)
        userpage_avatar.style = "height:200px;border-radius:100%;border-style:solid;border-width: 2px"
        document.getElementById("userpage_avatar").replaceWith(userpage_avatar);
        new_obj = data;

        userinfo_list = document.createElement("ul");
        for(iterator in Object.keys(new_obj)){
            key = Object.keys(new_obj)[iterator];
            if(key != "token"){
                li_item = document.createElement("li");
                li_item.innerHTML = key+": "+new_obj[key];
                userinfo_list.appendChild(li_item) ;
            }   
        }

        document.getElementById("user_info").innerHTML = ""
        document.getElementById("user_info").appendChild(userinfo_list);      

    }

    if(data.username ==  selfdata.username){
        document.getElementById("edit_button").style.display="inline"
        document.getElementById("delete").style.display="inline"
    }

    if(selfdata.admin){
        document.getElementById("edit_button").style.display="inline"
        document.getElementById("delete").style.display="inline"
        document.getElementById("extended_info_button").style.display="inline"
        document.getElementById("token_info").innerHTML = "<ul><li>Last_Token_Creation: "+data.token.last_login+"</li><li>valid_for: "+data.token.valid_for+"</li><li>valid_until: "+data.token.valid_until+"</li><li>Token: <code>"+data.token.token+"</code></li></ul>"
        var perms = await post("GET",{},"perms")

        var perm_holder = document.getElementById("perm_container")
        perm_holder.innerHTML = "<h3>Perms</h3>"

        for(var iter in perms){
            var perm = perms[iter]
            var checkbox_div = document.createElement("div")
            checkbox_div.classList = "checkbox mb-3"
            if(data.perms.includes(perm)){
                checkbox_div.innerHTML ="<label><input class=\"change_perms\" autocomplete=\"false\" type=\"checkbox\" value=\""+perm+"\" checked> "+perm+"</label>"
            }else {
                checkbox_div.innerHTML ="<label><input class=\"change_perms\" autocomplete=\"false\" type=\"checkbox\" value=\""+perm+"\"> "+perm+"</label>"
            }
            perm_holder.appendChild(checkbox_div)
            //<div class="checkbox mb-3">
            //    <label>
            //        <input id="remember_me" type="checkbox" value="remember-me"> remember-me
            //    </label>
            //</div>
        }
    }
    
}

get_user_data()


function change(){
    //alert("would change stuff if that would be implemented lol")

    var dict = {}

    pw = document.getElementById("password").value
    pw_confirm = document.getElementById("password_confirm").value
    email = document.getElementById("email").value

    if(pw != pw_confirm){
        site_alert.textContent = "passwords do not match!";
        site_alert.classList = "alert alert-danger";
        showAlert()
        return
    }

    console.log(pw.length)

    if (pw.length>0){
        dict["password"] = pw
    }
    if (pw_confirm.length>0){
        dict["passwordconfirm"] = pw_confirm
    }
    if (email.length>0){
        dict["email"] = email
    }

    handle_perms(dict)
    handle_avatar(dict)
    console.log(dict)

    
}


function handle_perms(work_dict){

    perms = document.querySelectorAll(".change_perms")
    perm_dict = {}
    perms.forEach(function(currentValue, currentIndex, listObj){perm_dict[currentValue.value] = currentValue.checked})

    if(Object.keys(perm_dict).length > 0){
        work_dict["perms"] = perm_dict
    }
    
}

function handle_avatar(work_dict){

    console.log("not implemented yet q.q")
    
}