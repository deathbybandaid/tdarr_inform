from browser import document, bind  # alert, window
from browser.widgets.dialog import InfoDialog
# import json


@bind("#settings_help", "click")
def settings_help(event):
    config_id = str(event.currentTarget.value)
    help_info = help_data(document.select(".help"), config_id)

    config_message = ""
    for config_item in ["Description", "Valid Options", "Default Value"]:
        if help_info[0][config_item]:
            config_message += "%s: %s\n" % (config_item, help_info[0][config_item])

    InfoDialog(config_id, config_message, ok="Got it")


def help_data(items, help_id):

    helplist = []
    helpdict = {}

    for element in items:
        if element.name == "id":
            if len(helpdict.keys()) >= 2 and "id" in list(helpdict.keys()):
                helplist.append(helpdict)
            helpdict = {"id": element.value}
        if element.name != "id":
            helpdict[element.name] = element.value

    helplist = [x for x in helplist if x["id"] == help_id]

    return helplist
