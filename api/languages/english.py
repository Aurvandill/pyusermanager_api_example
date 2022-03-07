from .lang_dict import LangDict

class LangEng(LangDict):

    #parameter msgs
    parameter_password_confirm_error = "passwords do not match!"
    parameter_error = "Supplied Parameters are not valid"
    parameter_username_error = "Supplied Username is not valid"
    parameter_generic_error = "Could not set specified Parameters"
    
    #user messages
    user_edit_perm_error = "you are not allowed to change other users!"
    user_missing = "User does not exist"
    user_create_error = "could not create User!"
    user_create_success = "successfully created User"
    user_create_existing = "the username is already taken"
    user_delete_success = "User successfully deleted"
    user_delete_error = "Could not delete User"
    user_logout_success = "Successfull Logout"
    user_logout_error = "Logout unsuccessfull"
    user_login_success = "Login was successfull"
    user_login_error = "Login was mot successfull"

    #perm_stuff
    perm_misc_error = "You don't have the needed permissions."
    perm_admin_error = "You must be an admin"
    perm_create = "Perm created"
    perm_delete = "Perm deleted"

    #misc msgs
    misc_error = "something went wrong"
    registration_forbidden = "registering is prohibited"
    already_logged_in = "you are logged in already"
    not_logged_in = "not logged in!"
    changes_success = "Changes successfull"

    #avatar related msgs
    avatar_size_error = "Supplied avatar is to large"
    avatar_set_error = "Something went wrong while wanted to set the avatar"

    #file related msgs
    file_invalid_type = "uploaded file not supported"