import sys
sys.path.append("noble_manager")
import copy
import inspect
import random
import json

class NobleManager:
    """Deals with the normal, day-to-day creation, execution and boring old management of Nobles.
     Probably isn't paid enough"""
    def __init__(self, nobles_dictionary_filename, noblenames_filename):
        self.noble_filename =  nobles_dictionary_filename
        self.noble_dictionary = self.load_file(self.noble_filename, {})
        self.noble_instances = self.load_instances()
        self.id_lookup = self.load_id()
        self.noble_creator_instance = NobleCreator(self, noblenames_filename)

    def run_events(self):
        noble_runner = NobleRunner(self, self.compile_instance_list())
        return noble_runner.run_events()

    def compile_instance_list(self):
        noble_list = []
        for name, noble in self.noble_instances.items():
            noble_list.append(noble)
        return noble_list

    def torment_nobles(self):
        for noble in self.compile_instance_list():
            noble.happiness -= 1
            return "\nYou make {} very unhappy!".format(noble.full_name)

    def list_names(self):
        return self.id_lookup

    def view_nobles(self):
        noble_list = []
        for name, noble in self.noble_instances.items():
            noble_list.append(noble)
        noble_list = sorted(noble_list, key=lambda noble: (noble.nobility), reverse=True)
        string = ""
        for noble in noble_list:
            string += ("\n{}\nNobility: {}\nWealth: {}\nHappiness: {}\n".format(noble.extended_title, noble.nobility, noble.wealth, noble.happiness))
        return string

    def view_single_noble(self, name):
        if type(name) == int:
            name = get_name_from_id(name)
        noble = self.noble_instances[name]
        return "{}\nNobility: {}\nWealth: {}\nHappiness: {}".format(noble.extended_title, noble.nobility, noble.wealth, noble.happiness)

    def execute_noble(self, full_name, death_message = None):
        noble_instance = self.noble_instances[full_name]
        if not death_message: death_message = noble_instance.death_message
        del self.noble_dictionary[full_name]
        del self.noble_instances[full_name]
        self.noble_instances = self.load_instances()
        for name, noble in self.noble_instances.items():
            del noble.relations[full_name]
        self.id_lookup = self.load_id()
        self.save_file()
        if full_name in self.noble_dictionary:
            return "Something went wrong"
        else:
            return death_message

    def execute_all(self):
        self.noble_dictionary = {}
        self.id_lookup = []
        self.noble_instances = self.load_instances()
        self.save_file()
        return("Everybody's dead, Dave")

    def patch_nobles(self, stat, value, mode="ignore"):
        """Adds or modifies a single stat of all nobles"""
        for noble in self.noble_dictionary:
            try:
                self.noble_dictionary[noble][stat]
                if mode == "overwrite": self.noble_dictionary[noble][stat] = value
                if mode == "delete": del self.noble_dictionary[noble][stat]
            except KeyError:
                if mode != "delete": self.noble_dictionary[noble][stat] = value

    def create_noble(self):
        """Uses the NobleCreator instance to create a new noble, and automitically creates an NobleInstance for it"""
        new_noble_instance = self.noble_creator_instance.create_noble()
        noble_welcomes = []
        for name, noble in self.noble_instances.items():
            noble_welcomes.append(noble.welcome_noble(new_noble_instance))
        self.noble_dictionary[new_noble_instance.full_name] = new_noble_instance.compile_dict()
        self.id_lookup.append((new_noble_instance.full_name, new_noble_instance.id))
        self.noble_instances[new_noble_instance.full_name] = new_noble_instance
        self.save_file()
        string = "New noble created: {}\n".format(new_noble_instance.extended_title)
        for item in noble_welcomes:
            string += "\n{}".format(item)
        return string

    def view_relations(self, name):
        string = ""
        noble = self.noble_instances[name]
        for name, value in noble.relations.items():
            string += "{}: {}\n".format(name, value)
        return string

    def get_name_from_id(self, ident):
        try:
            ident = int(ident)
        except TypeError:
            pass
        for item in self.id_lookup:
            if item[1] == ident: return item[0]
        return("ERROR")

    def load_instances(self):
        """Uses nobles_dictionary to create seperate NobleInstance instances of all nobles, and stores
        them in self.nobles_instances"""
        instances = {}
        for noble, stats in self.noble_dictionary.items():
            try:
                instances[noble] = NobleInstance(stats, self)
            except KeyError as e:
                print("Error! {} is missing a stat. ({})".format(stats["full_name"], e))
        return instances

    def load_id(self):
        id_list = []
        for name, noble in self.noble_instances.items():
            id_list.append((noble.full_name, noble.id))
        return id_list

    def load_file(self, var_file, default = None):
        """Loads specified file"""
        try:
            with open(var_file, "r") as file:
                raw_load = file.read()
            return json.loads(raw_load)
        except FileNotFoundError:
            print('"%s": File not found' % var_file)
            return default

    def save_file(self):
        """Saves self.nobles_dictionary and self.id_lookup"""
        dump = json.dumps(self.noble_dictionary)
        with open(self.noble_filename, "w") as file:
            file.write(dump)

class NobleStat:
    def __init__(self, name, min_value, max_value):
        self.value = None
        self.name = name
        self.min_value = min_value
        self.max_value = max_value

    def __get__(self, instance, owner):
        return self.value

    def __set__(self, instance, value):
        if value > self.max_value:
            print("New value too high, setting to max value. (Owner: {}, Stat: {}, Value: {}, Max:{})".format(instance, self.name, value, self.max_value))
            self.value = self.max_value
        elif value < self.min_value:
            print("New value too low, setting to min value. (Owner: {}, Stat: {}, Value: {}, Min:{})".format(instance, self.name, value, self.min_value))
            self.value = self.min_value
        else:
            self.value = value

class NobleInstance(NobleManager):
    """A class to turn nobles into objects, rather than just having them sit around in a dictionary. The point
    of thie exercise!"""
    wealth = NobleStat("wealth", 0, 9999)
    happiness = NobleStat("happiness", 0, 10)
    honour = NobleStat("honour", 0, 10)
    def __init__(self, noble_dict, noble_manager):
        self.noble_manager = noble_manager
        self.id = noble_dict["id"]
        self.gender = noble_dict["gender"]
        self.nobility = noble_dict["nobility"]
        self.full_name = noble_dict["full_name"]
        self.surname = noble_dict["surname"]
        self.full_title = noble_dict["full_title"]
        self.extended_title = noble_dict["extended_title"]
        self.relations = noble_dict["relations"]
        self.wealth = noble_dict["wealth"]
        self.happiness = noble_dict["happiness"]
        self.honour = noble_dict["honour"]
        self.available_actions = [
            self.do_fuck_all,
            self.invest_capital,
            self.prank_noble,
            self.duel_noble
            ]
        self.marked_for_death = False
        self.death_message = "I shouldn't be dead!"
        self.ram_status = None

    def perform_action(self, action=None, *args):
        result = None
        if self.happiness < 0:
            result = self.end_it()
        if not action: action = random.choice(self.available_actions)
        if not result: result = action(*args)
        self.save_self()
        return result

    def end_it(self):
        result = "{0} isn't looking too happy...".format(self.full_name)
        self.marked_for_death = True
        self.death_message = "{0}  is far too unhappy to be a noble. They slink off into solitude. Goodbye, {0}!".format(self.full_name)
        return result

    def duel_noble(self):
        valid_list = []
        for name, value in self.relations.items():
            if value <= 3: valid_list.append(self.noble_manager.noble_instances[name])
        if not valid_list: return "{} is itching for a fight, but finds themselves surrounded by caring friends!".format(self.full_name)
        duel_receiver = random.choice(valid_list)
        result = "{} challenges {} to a duel!".format(self.full_name, duel_receiver.full_name)
        reaction = duel_receiver.receive_duel_proposal(self)
        result += reaction
        if duel_receiver.ram_status == False:
            return result
        elif duel_receiver.ram_status == True:
            result += "\n{} and {} wake at dawn and face each other across the duelling field. The air is thick with tension, sweat, and ridiculous upper class gestures.".format(self.full_name, duel_receiver.full_name)
            winner = random.choice([self, duel_receiver])
            if winner == self:
                loser = duel_receiver
            else:
                loser = self
            result += "\n{0} shoots first! {1} is no more. Goodbye, {1}!".format(winner.full_name, loser.full_name)
            loser.marked_for_death = True
            loser.death_message = "{} is laid to rest by their family and friends. Such is the difficult life of the nobility.".format(loser.full_name)
            winner.honour += 1
            winner.happiness += 1
            winner.ram_status = None
            return result

    def receive_duel_proposal(self, duel_proposer):
        bravery_roll = random.randint(1, 10)
        if bravery_roll <= self.honour:
            result = "\n{} accepts the duel - Pistols at dawn!".format(self.full_name)
            self.ram_status = True
        else:
            result = "\n{} refuses the duel. Coward!".format(self.full_name)
            self.ram_status = False
            self.happiness -= 1
        return result

    def do_fuck_all(self):
        self.happiness += 1
        result = "{} sits on their arse for a week. They get happier. Feudalism!".format(self.full_name)
        return result

    def invest_capital(self):
        success = random.randrange(-50, 100, 1)
        percentage = success / 1000
        if success < 0:
            result = "{} tries investing some capital, but somehow buys into the only Ponzi scheme in medieval europe. D'oh!".format(self.full_name)
        elif success >= 0 and success < 5:
            result = "{} invests their capital into a reliable mining company - a good choice in pre 1980's britain".format(self.full_name)
        elif success >= 5:
            self.happiness += 1
            result = "{} takes a chance with an internet startup, and is suddenly rolling in cash!".format(self.full_name)
        self.wealth = int(self.wealth*(1 + percentage))
        return result

    def prank_noble(self, prankee=None):
        if not prankee:
            candidate_list = []
            for noble in self.relations:
                if self.relations[noble] < 7:
                    candidate_list.append(noble)
            if not candidate_list: return "{} wants to prank someone, but loves everyone too much!".format(self.full_name)
            prankee = random.choice(candidate_list)
        prankee_instance = self.noble_manager.noble_instances[prankee]
        result = "{} pulls a hilarious prank on {}!".format(self.full_name, prankee_instance.full_name)
        reaction = prankee_instance.get_pranked(self)
        result += reaction
        return result

    def get_pranked(self, pranker=None):
        if not pranker:
            result = "\n{} gets pranked by a ghost. Spooky! (Error)".format(self.full_name)
        else:
            outcome = random.randint(1, 3)
            if outcome == 1:
                self.happiness += 1
                result = "\n{} finds everything in their office wrapped in cellophane. What fun!".format(self.full_name)
            elif outcome == 2:
                self.happiness -= 1
                self.relations[pranker.full_name] -= 3
                result =  "\nWhile walking down main street, {0} is ambushed by clowns! {0} hate clowns!".format(self.full_name)
            elif outcome == 3:
                self.happiness -= 3
                self.wealth = int(self.wealth * 0.8)
                self.relations[pranker.full_name] -= 3
                result = "\n{} comes home to find their house on fire. Wait, that's not a prank - that's arson!".format(self.full_name)
        return result

    def welcome_noble(self, new_noble):
        if new_noble.surname == self.surname:
            print(new_noble.surname)
            print(self.surname)
            friendship = 10
        else:
            friendship = random.randint(1, 9)
        if friendship < 4:
            string = ("{} turns her nose up at this filthy newcomer".format(self.full_name))
        elif friendship >=4 and friendship < 7:
            string = ("{} eyes the newcomer cautiously".format(self.full_name))
        elif friendship >= 7:
            string = ("{} welcomes the newcomer with open arms!".format(self.full_name))
        self.relations[new_noble.full_name] = friendship
        return string

    def compile_dict(self):
        stat_dict = self.__dict__.copy()
        del stat_dict["noble_manager"]
        del stat_dict["available_actions"]
        stat_dict["wealth"] = self.wealth
        stat_dict["happiness"] = self.happiness
        stat_dict["honour"] = self.honour
        return stat_dict

    def save_self(self):
        """NobleManager passes itself to each NobleInstance to let this work"""
        stat_dict = self.compile_dict()
        self.noble_manager.noble_dictionary[self.full_name] = stat_dict
        self.noble_manager.save_file()

    def __str__(self):
        return 'NobleInstance: "{}"'.format(self.full_name)

    def __repr__(self):
        return '<instance of noble {}>'.format(self.full_name)

class NobleRunner:
    def __init__(self, noble_manager, action_list):
        self.noble_manager = noble_manager
        self.action_list = action_list

    def run_events(self):
        string = ""
        for noble in self.action_list:
            if noble.marked_for_death:
                string += "{} would do something, but most of their time is being taken up by being dead".format(noble.full_name)
            else:
                string += "\n\n"
                string += noble.perform_action()
                death_message = self.check_for_deaths()
                if death_message:
                    string += death_message
        return string

    def check_for_deaths(self):
        death_list = []
        for name, noble in self.noble_manager.noble_instances.items():
            if noble.marked_for_death == True:
                death_list.append((name, noble))
        string = ""
        for name, noble in death_list:
            if noble in self.action_list:
                self.action_list.remove(noble)
                string += "\n" + self.noble_manager.execute_noble(name)

    def __str__(self):
        return "An instance of class NobleRunner"

    def __repr__(self):
        return "<instance of class NobleRunner>"

class NobleCreator(NobleManager):
    """It's called NobleCreator. Take a wild guess as to what it does"""
    def __init__(self, NobleManager, noblenames_filename):
        self.noble_manager = NobleManager
        self.noblename_filename = noblenames_filename
        self.noblenames = self.load_names()

    def create_noble(self):
        """It's called create_noble. Take a wild guess as to what it does"""
        noble = {}
        noble["gender"] = random.choice(["m", "f"])
        noble["nobility"] = random.randint(1, 10)
        names = self.create_noble_name(noble["gender"], noble["nobility"])
        noble["full_name"] = names[0]
        noble["surname"] = names[1]
        noble["full_title"] = names[2]
        noble["extended_title"] = names[3]
        noble["id"] = self.find_appropriate_id()
        noble["relations"] = self.generate_relations()
        noble["wealth"] = random.randint(10, 9999)
        noble["happiness"] = random.randint(1, 10)
        noble["honour"] = random.randint(1, 10)
        noble_instance = NobleInstance(noble, self.noble_manager)
        return noble_instance

    def generate_relations(self):
        relations_dict = {}
        for name, noble in self.noble_manager.noble_instances.items():
            relations_dict[name] = random.randint(1,10)
        return relations_dict

    def load_names(self):
        with open(self.noblename_filename, "r") as file:
            coded = file.read()
        return json.loads(coded)

    def create_noble_name(self, gender, nobility):
        flag = True
        while flag == True:
            flag = False
            if gender == "m":                                   #Setting appropriate lists to use based on the Nobles stats.
                first_name = self.noblenames["first_male"]           #This part gets the appropriate gender lists
                titles = self.noblenames["titles_male"]
            else:
                first_name = self.noblenames["first_female"]
                titles = self.noblenames["titles_female"]
            if nobility >= 7:                                   #This part sets the appropriate ranked nobility lists
                placenames = self.noblenames["placenames_major"]
            elif nobility >= 4:
                placenames = self.noblenames["placenames_minor"]
            else:                                               #This bit unsets some variables of the noble is too shitty to have a title
                placenames = None
                titles = None
                full_title = None
            surname = random.choice(self.noblenames["surname"])                    #Setting final lists
            nickname = random.choice(self.noblenames["nicknames"])
            full_name_list = []
            for item in self.noble_manager.id_lookup:
                full_name_list.append(item[0])
            while True:
                full_name = "{} {}".format(random.choice(first_name), surname)    #Generates First and second name, stores under full_name
                if not full_name in full_name_list: break
            if titles:                                                  #Generates a title and place, stores under full_title"
                full_title = "{} {}".format(random.choice(titles), random.choice(placenames))
            extended_title = full_name + nickname  #adds a nickname to full_name, stores in extended_title
            if titles:                                          #If the nobility has a title (i.e. they are not shitty), adds it to extended title
                extended_title = "{}, {}".format(extended_title, full_title)

        return[full_name, surname, full_title, extended_title]

    def find_appropriate_id(self):
        """Nobles need to have distinct identification numbers. This lets that happen"""
        default_id = 100
        id_list = []
        for item in self.noble_manager.id_lookup:
            id_list.append(item[1])
        while True:
            if default_id in id_list:
                default_id += 1
                continue
            return default_id


if __name__ == "__main__":
    noble = NobleManager("nobles_dictionary.json", "noblenames.json")
    options = [
    ("Create Noble", noble.create_noble),
    ("Patch Nobles", noble.patch_nobles),
    ("View Nobles", noble.view_nobles),
    ("View relations", noble.view_relations),
    ("View Single Noble", noble.view_single_noble),
    ("Execute Noble", noble.execute_noble),
    ("Execute all", noble.execute_all),
    ("Torment Nobles", noble.torment_nobles),
    ("Run Events", noble.run_events),
    ("Save File", noble.save_file)
    ]
    while True:
        print("\n")
        for i in range(len(options)):
            print("({}. {}) ".format(i, options[i][0]), end="")
        while True:
            try:
                choice = int(input("\nDo what?"))
                break
            except ValueError:
                print("Use a number dude")
        try:
            method = options[choice][1]
        except IndexError:
            print("Not a valid choice homie")
        dependancy_list = inspect.signature(method)
        arg_list = []
        for item in dependancy_list.parameters:
            arg_list.append(input("Need argument: {}\n".format(item)))
        print("\n{}".format(method(*arg_list)))
