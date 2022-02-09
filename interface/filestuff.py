def get_template(filename, **passed_vars):
    try:
        with open(f"./template/{filename}", "r", encoding="utf-8") as file:
            # return f"{file.read()}".format(**passed_vars)
            return f"{file.read()}".format_map(SafeDict(**passed_vars))
    # falls datei nicht existiert!
    except Exception as err:
        print(err)
        return "could not open template\n"


# falls ein eintrag nicht gefunden wird soll er durch ein leeres feld ersetzt werden!
class SafeDict(dict):
    def __missing__(self, key):
        return ""
