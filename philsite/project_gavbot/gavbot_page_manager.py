import re
import json

class PageManager:
    def __init__(self):
        self.page_data = ["No page data here", []]

    def interpret_page(self, page, gavbot):
        split = re.split("<title>", page)
        title = "<b>" + split[1] + "</b>"
        split = re.split("<text>", split[2])
        text = split[1]
        text = re.sub("\n\n", "<p>", text)
        text = "<p>" + text
        split = re.split("<items>", split[2])
        items = split[1]
        choices = re.split("<choice>", split[2])
        choices.pop(0) #now we have choices serialised
        for i in range(len(choices)):
            choices[i] = re.sub("\n", "", choices[i])
            choices[i] = re.sub("<page>", "<>", choices[i])
            choices[i] = re.sub("<req>", "<>", choices[i])
            choices[i] = re.split("<>", choices[i])
        page_data = [title, text, items, choices]
        return page_data

    def load_page(self, gavbot):
        print("???")
        file_path = "{}pages/act_{}/{}.txt".format(gavbot.path, str(gavbot.current_act), str(gavbot.current_page))
        with open(file_path, "r") as file:
            raw_text = file.read()
        page_data = self.interpret_page(raw_text, gavbot)
        return page_data

class Gavbot:
    def __init__(self, owner, path="philsite/project_gavbot/"):
        self.path = path
        self.manager = PageManager()
        try:
            self.load_gav(owner)
        except FileNotFoundError:
            self.owner = owner
            self.health = 3
            self.meta = []
            self.traits = []
            self.inventory = []
            self.current_act = 1
            self.current_page = "intro"
            self.manual_update_page()
            self.save_gav()
        self.pic = "/gavbot_static/images/gavbot.jpg"
        self.health_pic = "/gavbot_static/images/heart.jpg"
        self.item_lists = {
            "meta": self.meta,
            "trait": self.traits,
            "inventory": self.inventory
            }
        self.manual_update_page()

    def refine_choices(self, choices):
        choices = [[x[0], x[1], re.split("/", x[2])] if re.split("/", x[2]) != [""] else [x[0], x[1], []] for x in choices]
        choices = [x for x in choices if set(x[2]).issubset(set(self.traits + self.inventory))]
        return(choices)

    def manual_update_page(self):
        print("???")
        page_data = self.manager.load_page(self)
        self.page_title = page_data[0]
        self.page_text = page_data[1]
        self.page_items = page_data[2]
        if self.page_items: self.update_items()
        self.page_choices = self.refine_choices(page_data[3])
        self.valid_choices = [x[1] for x in self.page_choices]
        self.save_gav()

    def update_page(self, page_name):
        if page_name in self.valid_choices:
            self.current_page = page_name
            self.manual_update_page()
        else:
            print("NOT VALID PAGE CHOICE")

    def update_items(self):
        item_list = re.split("\|", self.page_items)
        print(item_list)
        for item in item_list:
            item_commands = re.split("\_", item)
            item_name = item_commands[2]
            print(item_commands)
            if item_commands[0] == "gain":
                if item_name not in self.item_lists[item_commands[1]]:
                    self.item_lists[item_commands[1]].append(item_name)
            elif item_commands[0] == "lose":
                if item_name in self.item_lists[item_commands[1]]:
                    self.item_lists[item_commands[1]].pop(item_name)


    def reset_gavbot(self):
        self.manager = PageManager()
        self.health = 3
        self.pic = "/static/images/project_gavbot/gavbot.jpg"
        self.health_pic = "/static/images/project_gavbot/heart.jpg"
        self.meta = []
        self.traits = []
        self.inventory = []
        self.current_act = 1
        self.current_page = "intro"
        self.manual_update_page()
        self.save_gav()

    def save_gav(self):
        file_name = "{}saved_gavbots/{}.json".format(self.path, self.owner)
        data = {
            "owner": self.owner,
            "health": self.health,
            "meta": self.meta,
            "traits": self.traits,
            "inventory": self.inventory,
            "act": self.current_act,
            "page": self.current_page}
        data_dumps = json.dumps(data)
        with open (file_name, "w") as file:
            file.write(data_dumps)

    def load_gav(self, owner):
        file_name = "{}saved_gavbots/{}.json".format(self.path, owner)
        with open(file_name, "r") as file:
            data = json.loads(file.read())
        self.owner = data["owner"]
        self.health = data["health"]
        self.meta = data["meta"]
        self.traits = data["traits"]
        self.inventory = data["inventory"]
        self.current_act = data["act"]
        self.current_page = data["page"]


if __name__ == "__main__":
    manager = PageManager()
    gav = Gavbot("scripttest", path="")
    gav.path = ""
    gav.current_page = "lobby_chase_yes"
    gav.manual_update_page()
    page = manager.load_page(gav)
    print(page)
    print(gav.meta)
    print(gav.traits)
