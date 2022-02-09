var user_container = document.getElementById("usercontainer")

async function get_users(){
    json_ = {}
    let data = await post("GET",{},"users")

    for (user in data.Users){

        let userlink = document.createElement('a')
        userlink.href = "/user/"+data.Users[user].username
        
        let userbox = document.createElement('button')
        userbox.classList = "btn btn-primary"

        useravatar = await get_img(data.Users[user].avatar)
        useravatar.style.height = "50px"
        useravatar.style.borderRadius = "100%"
        useravatar.style.marginRight ="10px"
        useravatar.style.marginLeft ="-5px"
        
        let username = document.createElement('span')
        username.textContent = data.Users[user].username

        userlink.append(userbox)
        userbox.appendChild(useravatar)
        userbox.appendChild(username)

        user_container.appendChild(userlink)
        userlink.style.margin="5px"
    }
}

get_users()