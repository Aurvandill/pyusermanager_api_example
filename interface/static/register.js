function register(){
    
    data = {"action":"register"};

    pw = document.getElementById("password").value;
    pw_confirm = document.getElementById("passwordconfirm").value;
    username = document.getElementById("username").value;
    email = document.getElementById("email").value;

    data["password"]=pw;
    data["passwordconfirm"]=pw_confirm;
    data["username"]=username;
    data["email"]=email;

    post("POST",data,'register')
}