function login(){
    
    data = {"action":"login"};

    pw = document.getElementById("password").value;
    username = document.getElementById("username").value;
    remember_me = document.getElementById("remember_me").checked;

    data["password"]=pw;
    data["username"]=username;
    data["remember_me"]=remember_me;

    post("POST",data,'login')
}