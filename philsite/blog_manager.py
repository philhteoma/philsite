import re

class Blog:
    def __init__(self):
        with open("philsite/blog/archive/archive.txt", "r") as file:
            raw_archive = file.readlines()
        self.archive = [tuple(re.split("\|", x[:-1])) for x in raw_archive]
        self.archive.sort(key=lambda x: int(re.sub("/", "", x[1])))
        self.archive.reverse()
        self.archive = [(re.sub(" ", "_", x[0].lower()), x[0], x[1]) for x in self.archive]
        self.max_index = len(self.archive) - 1

    def load_page(self, request_string=""):
        if request_string:
            request_string = re.split("--", request_string)
            print(request_string)
            current_page_title = request_string[0]
            current_page_index = [x[0] for x in self.archive].index(current_page_title)
            arguments = request_string[1:]
            if "older" in arguments:
                new_page_index = current_page_index + 1
                request = True
            elif "newer" in arguments:
                new_page_index = current_page_index - 1
                if new_page_index < 0: new_page_index = 0
                request = True
            else:
                new_page_index = current_page_index
                request = False
        else:
            new_page_index = 0
            request = False
        page_object = BlogPage(self.archive[new_page_index], new_page_index, request)
        return page_object

class BlogPage:
    def __init__(self, page_info, new_page_index, request=False):
        self.page_index = new_page_index
        self.formal_name = re.sub(" ", "_", page_info[0])
        self.page_name = page_info[1]
        self.page_date = page_info[2]
        self.request = request
        if request:
            pass
        else:
            self.format_page()


    def format_page(self):
        with open("philsite/blog/posts/" + self.formal_name + ".txt", "r") as file:
            self.raw_text = file.read()
        split = re.split("<title>", self.raw_text)
        self.page_title = split[1]
        self.page_text = re.sub("\n\n", "<p>", split[2])
        self.page_text = self.extract_urls()

    def extract_urls(self):
        stage_one = re.split("}}", self.page_text)
        stage_two = [re.split("{{", x) for x in stage_one]
        for i in range(len(stage_two)):
            part = stage_two[i]
            if len(part) == 1:
                break
            url_pieces = re.split("\|", part[1])
            url = "<a href={0}>{1}</a>".format(url_pieces[1], url_pieces[0])
            stage_two[i][1] = url
        stage_three = [x for y in stage_two for x in y]
        return "".join(stage_three)

if __name__ == ("__main__"):
    blog = Blog()
    print(blog)
