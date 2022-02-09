

function create_token(){
    var today = new Date();
    var valid_until = new Date();
    valid_until.setDate(today.getDate()+365);
    document.cookie = "token=1234asdas1234; expires="+valid_until.toUTCString()+"; path=/";
}

function delete_token(){
    var today = new Date();
    var valid_until = new Date();
    valid_until.setDate(today.getDate()-999);
    document.cookie = "token=1234asdas; expires="+valid_until.toUTCString()+"; path=/";
}
