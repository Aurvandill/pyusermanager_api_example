
var site_alert = document.getElementById("site_alert");
var header = document.getElementById("header_replace");

var api_url = document.getElementById("api_url").innerHTML

function check_status(){
    const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);
    //console.log(urlParams);
    //console.log(urlParams.get("modal_status"))
    //console.log(urlParams.get("error"));
    if (urlParams.get("alert_msg") && urlParams.get("alert_type")){
        //cahnge Modal
        site_alert.textContent = urlParams.get("alert_msg");
        site_alert.classList = "alert "+urlParams.get("alert_type");
        //remove vars from url
        //open alert
        showAlert();
    }

    var newURL = window.location.href.split("?")[0];
    window.history.pushState('object', document.title, newURL);
}

function showAlert(){
    site_alert.style.display ="inline-block";
    site_alert.style.opacity = 1;
    setTimeout(
        function() {
          fade_alert();
        }, 3000);
    
}
function fade_alert(){
    opacity = site_alert.style.opacity
    site_alert.style.opacity -= 0.02
    if (opacity > 0.1){
        setTimeout(function() {fade_alert();}, 50);
    } else {
        hide_alert();
    }
    
}
function hide_alert(){
    site_alert.style.opacity = 0;
    site_alert.style.display ="none";
}

function copy_to_clipboard(obj){
    console.log(obj)
    /* Get the text field */
      
    /* Copy the text inside the text field */
    navigator.clipboard.writeText(obj.textContent);

    site_alert.textContent = "copied to clipboard!";
    site_alert.classList = "alert alert-success";

    showAlert()

}


// Cookies
function createCookie(name, value, days) {
    if (days) {
        var today = new Date();
        var valid_until = new Date();
        valid_until.setDate(today.getDate()+days);
        var expires = "; expires=" + valid_until.toUTCString();
    } else {
        var expires = "";
    }              

    document.cookie = name + "=" + value + expires + "; path=/";
}

function getCookie(name) {
    var nameEQ = name + "=";
    var ca = document.cookie.split(';');
    for (var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') c = c.substring(1, c.length);
        if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length, c.length);
    }
    return null;
}

function deleteCookie(name) {
    createCookie(name, "", -1);
}

// Misc
async function post(type, input_object = Object(), api_endpoint,include_token = true) {

    const requestOptions = {
        method: type,
        headers: { 
            "Content-Type": "application/json"
        },
    };

    if(include_token){
        token_cookie = getCookie("token");
        if(token_cookie){
            if (token_cookie.length < 2){
                console.log("did not append cookie to json")
            } else {
                requestOptions.headers["Authorization"] = "Token "+getCookie("token");
            }
        } 
    }

    //console.log(requestOptions)
    

    if(type != "GET"){
        //create json from object
        requestOptions.body = JSON.stringify(input_object)
    }


    const response = await fetch(api_url+"/"+api_endpoint, requestOptions);
    const data = await response.json().catch(error => {
        console.log(response)
        console.log('There was an error!', error);
    });

    console.log(response.status)
    console.log(data)

    process_response(data)

    return data
}

function process_response(json_obj){

    var redirect_params = new URLSearchParams()
    //handle login!
    if(json_obj.Login){
        createCookie("token",json_obj.Login.token,json_obj.Login.valid_days)
    }
    //handle login!
    if(json_obj.Logout){
        deleteCookie("token")
    }
    //handle alerts
    if(json_obj.Alert){
        site_alert.innerHTML = json_obj.Alert.alert_msg;
        site_alert.classList = "alert "+json_obj.Alert.alert_type;
        
        redirect_params.append("alert_type", json_obj.Alert.alert_type);
        redirect_params.append("alert_msg", json_obj.Alert.alert_msg);

        showAlert();
    }
    //handle Redirects
    if (json_obj.Redirect){
        console.log(redirect_params)
        console.log(redirect_params.toString())
        //redirect!
        window.location.replace(json_obj.Redirect.redirect_url+"?"+redirect_params)
    }
}


async function update_header(){

    var data = await post("GET",{},"header")

    console.log(data)

    var logged_in = false;

    if(data.username != undefined){
        logged_in = true;
    }

    if(logged_in){

        header.innerHTML = '<button style="margin-left: 5px;" type="button" onclick="post(\'GET\',{},\'logout\')" class="btn btn-outline-light">Logout</button>'
        header.innerHTML += '<a style="margin-left: 5px;" href="/users"><button type="button" class="btn btn-outline-light">Users</button></a>'

        if(data.admin == true){
            header.innerHTML += '<a style="margin-left: 5px;" href="/create_user"><button type="button" class="btn btn-outline-light">create user</button></a>'
            header.innerHTML += '<a style="margin-left: 5px;" href="/perms"><button type="button" class="btn btn-outline-light">Permissions</button></a>'
        }

        //usersymbol
        img = await get_img(data.avatar)
        img.style ="height:30px;margin-top: -2px;margin-left: -5px;margin-right: 10px; border-radius: 100%;"
        header.innerHTML += '<a style="margin-left: 5px;" href="/user/'+data.username+'"><button id="user_icon" class="btn btn-outline-light" style="height: 38px;"><div id="usersymbol" style="display: flex;flex-direction: row;"></div></button></a>'
        username = document.createElement("p")
        username.textContent = data.username
        document.getElementById("usersymbol").appendChild(img)
        document.getElementById("usersymbol").appendChild(username)
    } else {

        header.innerHTML = '<a href="/login"><button type="button" class="btn btn-outline-light me-2">Login</button></a>'
        if (data.registration){
            header.innerHTML += '<a href="/register"><button type="button" class="btn btn-outline-light me-2">Register</button></a>' 
        }

    }
}

async function get_img(filename){

    const requestOptions = {
        method: "GET",
    };
    let response = await fetch(api_url+"/avatar/"+filename, requestOptions);

    let blob = await response.blob()
    console.log(blob)
    let img = await blobToImage(blob)

    return img
}


const blobToImage = (blob) => {
    return new Promise(resolve => {
      const url = URL.createObjectURL(blob)
      let img = new Image()
      img.onload = () => {
        URL.revokeObjectURL(url)
        resolve(img)
      }
      img.src = url
    })
}

update_header();
check_status();