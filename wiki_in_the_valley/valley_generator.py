import requests
import re
import time

final_string = ""


def regex_url(para, mode=False):
    links = re.findall('/wiki/.*?"', para)
    parens = set()
    if mode:
        parens = find_parens_links(para)
    if links:
        #print("Url's found:")
        to_remove = []
        for item in links:
            #print(item)
            if item in parens:
                to_remove.append(item)
        for item in to_remove:
            links.remove(item)
    return links

def find_parens_links(para):
    parens = re.findall('\(.*?\)', para)
    parens_urls = set()
    for item in parens:
        urls = regex_url(item)
        for url in urls:
            parens_urls.add(url)
    #print(parens_urls)
    return parens_urls

def remove_tables(page):
    while True:
        non_nested = re.search("<table.*?</table>", page, re.DOTALL)
        nested = re.search("<table.*?<table", page, re.DOTALL)
        if nested:
            nested_str = nested.group(0)
            non_nested_str = non_nested.group(0)
            if len(non_nested_str) > len(nested_str):
                page = re.sub("<table.*?<table", "<table>", page, 1, re.DOTALL)
                page = re.sub("</table>", "", page, 1, re.DOTALL)
                continue
        subbed = re.sub("<table.*?</table>", "", page, 1, re.DOTALL)
        if subbed == page:
            break
        page = subbed
    return page

def remove_tags(page, open_tag, close_tag):
    while True:
        non_nested = re.search("%s.*?%s" % (open_tag, close_tag), page, re.DOTALL)
        nested = re.search("%s.*?%s" % (open_tag, open_tag), page, re.DOTALL)
        if nested:
            nested_str = nested.group(0)
            non_nested_str = non_nested.group(0)
            if len(non_nested_str) > len(nested_str):
                page = re.sub("%s.*?%s" % (open_tag, open_tag), open_tag, page, 1, re.DOTALL)
                page = re.sub(close_tag, "", page, 1, re.DOTALL)
                continue
        subbed = re.sub("%s.*?%s" % (open_tag, close_tag), "", page, 1, re.DOTALL)
        if subbed == page:
            break
        page = subbed
    return page

def get_next_url(url):
    """uses request to find the next link in the wiki chain"""
    time.sleep(0.2)
    wiki_page = requests.get(url)
    wiki_page_text = remove_tags(wiki_page.text, "<table", "</table>")
    paras = re.findall("(<p>.*?</p>|<li>.*?</li>)", wiki_page_text)
    for i in range(len(paras)):
        raw_para = paras[i]
        para = remove_tags(raw_para, "\(", "\)")
        raw_links = regex_url(raw_para, True)
        raw_links_modified = []
        for item in raw_links:
            raw_links_modified.append(remove_tags(item, "\(", "\)"))
        links = regex_url(para, True)
        if links:
            links[:] = [x for x in links if x[:11] != "/wiki/File:" and x[:11] != "/wiki/Help:"]
            for i in range(len(links)):
                if links[i] in raw_links_modified:
                    location = raw_links_modified.index(links[i])
                    links[i] = raw_links[location]
            break
    #print(links)
    try:
        link = links[0][:-1]
    except IndexError: return
    return "https://en.wikipedia.org" + link


def find_full_list(starting_url):
    """finds and logs the full list of wikipedia pages in a chain"""
    full_list = [starting_url]
    next_url = starting_url
    while True:
        #print("Analysing %s...\n\n" % next_url)
        next_url = get_next_url(next_url)
        if next_url in full_list:
            #print("LOOK HERE!!!!!!!!!!!!!!!!!!!!!!!!!", full_list)
            location = full_list.index(next_url)
            if location == 0:
                break
            else:
                full_list = full_list[:(location + 1)]
                break
        if next_url == "https://en.wikipedia.org/wiki/Philosophy":
            full_list.append(next_url)
            break
        if next_url:
            full_list.append(next_url)
        if not next_url:
            #print(full_list)
            break
    return full_list

def format_list(full_list):
    for i in range(len(full_list)):
        string = full_list[i][30:]
        string = re.sub("\(.*?\)", "", string)
        string = re.sub("_", " ", string)
        #print("--", string, "--")
        string = string.strip()
        #print("--", string, "--")
        full_list[i] = string
    return full_list

def build_song(full_list):
    song_lyrics = "Oh ro, the rattlin' %s,\nThe %s down in the valley o'!\nOh ro, the rattlin' %s,\nThe %s down in the valley o'!" % (full_list[0], full_list[0], full_list[0], full_list[0])
    for i in range(1, len(full_list)):
        song_lyrics += build_verse(full_list[:i+1])
    #print("Song built!")
    return song_lyrics

def build_verse(verse_list):
    verse = "\n\nAnd in that %s there was a %s - a rare %s, a rattlin' %s!" % (verse_list[-2], verse_list[-1], verse_list[-1], verse_list[-1])
    for i in range(len(verse_list)-1, 0, -1):
        verse += "\nand the %s in the %s," % (verse_list[i], verse_list[i-1])
    verse += "\nand the %s down in the valley-o'!" % verse_list[0]
    return verse

def save_song(song, first_link):
    file_name = "%s down in the valley-o!.txt" % first_link
    with open(file_name, "w") as file:
        file.write(song)
    #print('Song saved as "%s"' % file_name)

def make_a_song(url):
    full_list = find_full_list(url)

    for item in full_list:
        pass
        #print(item)

    formatted_list = format_list(full_list)
    song = build_song(full_list)
    return [full_list, song]

if __name__ == "__main__":
    url = input("Which wiki article?")
    make_a_song(url)
    save_song(song, formatted_list[0])

# link_list = [
#     "https://en.wikipedia.org/wiki/Python",
#     "https://en.wikipedia.org/wiki/High-level_programming_language",
#     "https://en.wikipedia.org/wiki/Computer_science",
#     "https://en.wikipedia.org/wiki/Science",
#     "https://en.wikipedia.org/wiki/Knowledge",
#     "https://en.wikipedia.org/wiki/Awareness",
#     "https://en.wikipedia.org/wiki/Consciousness",
#     "https://en.wikipedia.org/wiki/Quality",
#     "https://en.wikipedia.org/wiki/Attribute",
#     "https://en.wikipedia.org/wiki/Philosophy"
#     ]
#
# formatted_list = format_list(link_list)
# song_lyrics = build_song(formatted_list)
#
# with open("valley_o_lyrics.txt", "w") as file:
#     file.write(song_lyrics)
