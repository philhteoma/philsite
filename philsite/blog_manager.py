import re, codecs

class Blog:
    def __init__(self, app_dir):
        self.app_dir = app_dir
        with open(app_dir+"/blog/archive/archive.txt", "r") as file:
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
        page_object = BlogPage(self.archive[new_page_index], new_page_index, self.app_dir, request)
        return page_object

class BlogPage:
    def __init__(self, page_info, new_page_index, app_dir, request=False):
        self.page_index = new_page_index
        self.formal_name = re.sub(" ", "_", page_info[0])
        self.page_name = page_info[1]
        self.page_date = page_info[2]
        self.app_dir = app_dir
        self.request = request
        if request:
            pass
        else:
            self.format_page()


    def format_page(self):
        try:
            with open(self.app_dir+"/blog/posts/" + self.formal_name + ".txt", "r") as file:
                self.raw_text = file.read()
        except UnicodeDecodeError:
            with codecs.open(self.app_dir+"/blog/posts/" + self.formal_name + ".txt", "r", "utf-8") as file:
                self.raw_text = file.read()
        split = re.split("<title>", self.raw_text)
        self.page_title = split[1]
        self.page_text = re.sub("\n\n", "<p>", split[2])
        self.page_text = self.extract_urls(self.page_text)
        self.page_text = self.quote(self.page_text)

    # def quote(self, string):
    #     toggle = True
    #     for i in range(string.count("\"\"")):
    #         if toggle:
    #             string = re.sub("\"\"", '<div class="quote_div">\n<i>\"', string, count=1)
    #         else:
    #             string = re.sub("\"\"", '\"</i>\n</div>', string, count=1)
    #         toggle = not toggle
    #     return string

    def quote(self, string):
        open_div = '<div class="quote_div">\n'
        close_div = '</div>'
        for i in range(int(string.count("\"\"")/2)):
            quotes = re.findall('""(.*?)""', string, flags=re.DOTALL)
            for quote in quotes:
                if "|" in quote:
                    url = re.findall('(.*?)\|', quote, flags=re.DOTALL)[0]
                    open_div += '<a href="'+url+'" class="quote_hyperlink">'
                    close_div = "</a>" + close_div
                    quote = re.sub('(.*?)\|', "", quote, flags=re.DOTALL)
                quote = open_div + '"' + quote + '"' + close_div
                string = re.sub('""(.*?)""', quote, string, count=1, flags=re.DOTALL)
                print(quote)
                print(string)
        return string

    def extract_urls(self, string):
        stage_one = re.split("}}", string)
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
