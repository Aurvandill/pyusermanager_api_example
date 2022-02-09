from enum import Enum


class MODAL_TYPE(Enum):
    ERROR = "ModalERROR"
    SUCCESS = "ModalSUCCESS"
    WARNING = "ModalWARNING"
    PRIMARY = "ModalPRIMARY"


class ALERT_TYPE(Enum):
    PRIMARY = "alert-primary"
    SECONDARY = "alert-secondary"
    SUCCESS = "alert-success"
    DANGER = "alert-danger"
    WARNING = "alert-warning"
    INFO = "alert-info"
    LIGHT = "alert-light"
    DARK = "alert-dark"


class Alert:
    def __init__(self, message: str = "", type=ALERT_TYPE.SUCCESS):
        self.alert_type = type
        self.alert_msg = message

    def to_dict(self):
        tmp_dict = {"alert_type": self.alert_type.value, "alert_msg": self.alert_msg}
        return tmp_dict


class Modal:
    def __init__(
        self, message: str = "", type=MODAL_TYPE.SUCCESS, headline: str = "Hinweis"
    ):
        self.modal_type = type
        self.modal_msg = message
        self.modal_headline = headline

    def to_dict(self):
        tmp_dict = {
            "modal_type": self.modal_type.value,
            "modal_msg": self.modal_msg,
            "modal_headline": self.modal_headline,
        }
        return tmp_dict


class Redirect:
    def __init__(self, url: str = ""):
        self.redirect_url = url

    def to_dict(self):
        tmp_dict = {
            "redirect_url": self.redirect_url,
        }
        return tmp_dict


def get_json_from_args(*args):
    temp_dict = {}

    for arg in args:
        if type(arg) == Alert or type(arg) == Modal or type(arg) == Redirect:
            temp_dict.update({type(arg).__name__: arg.to_dict()})
        elif type(arg) == type({}):
            temp_dict.update(arg)
        else:
            print("got unsupported var o-o")

    return temp_dict
