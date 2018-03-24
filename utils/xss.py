from bs4 import BeautifulSoup

def xss(old):
    soup = BeautifulSoup(old, "html.parser")
    valid_tag = {
        "p": ["class", "id"],
        "img": ["src"],
        "div": ["class"],
        "span":["style"],
    }
    tags = soup.find_all()
    for tag in tags:
        if tag.name not in valid_tag:
            tag.decompose()  # 删除整个标签
            # tag.clear()  # 删除标签里的内容
        if tag.attrs:  # 有些是空字典
            for k in list(tag.attrs.keys()):  # {"id":"i1","a"=123,"b"=999}
                if k not in valid_tag[tag.name]:
                    del tag.attrs[k]  # 删除属性
    content_origin = soup.decode()
    content_text = soup.get_text()
    return content_origin,content_text