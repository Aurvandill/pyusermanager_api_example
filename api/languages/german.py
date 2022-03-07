from .lang_dict import LangDict

class LangGer(LangDict):

    #parameter msgs
    parameter_password_confirm_error = "Passwörter stimmen nicht überein!"
    parameter_error = "Übergebene Werte sind ungültig."
    parameter_username_error = "Nutzername ist nicht gültig"
    parameter_generic_error = "Konnte angegebene Parameter nicht setzen"
    
    #user messages
    user_edit_perm_error = "Du darfst keine anderen Nutzer ändern"
    user_missing = "Nutzer existiert nicht"
    user_create_error = "Konnte Nutzer nicht anlegen."
    user_create_success = "Nutzer erfolgreich angelegt!"
    user_create_existing = "Nutzername bereits vergeben"
    user_delete_success = "Nutzer erfolgreich gelöscht"
    user_delete_error = "Konnte Nutzer nicht löschen"
    user_logout_success = "Logout erfolgreich"
    user_logout_error = "Logout war nicht erfolgreich"
    user_login_success = "Login war erfolgreich"
    user_login_error = "Login war nicht erfolgreich"

    #perm_stuff
    perm_misc_error = "Du hast nicht die erforderlichen Rechte"
    perm_admin_error = "Dafür musst du Administrator sein"
    perm_create = "Gruppe erfolgriech angelegt"
    perm_delete = "Gruppe erfolgriech gelöscht"

    #misc msgs
    misc_error = "Konnte Aktion nicht ausführen!?"
    registration_forbidden = "Registrierungen sind Deaktiviert."
    already_logged_in = "Du bist bereits eingeloggt."
    not_logged_in = "Du bist nicht eingeloggt."
    changes_success = "Änderungen erfolgreich übernommen"

    #avatar related msgs
    avatar_size_error = "Avatar ist zu groß"
    avatar_set_error = "Konnte Avatar nicht setzen"

    #file related msgs
    file_invalid_type = "Dateityp nicht unterstützt"