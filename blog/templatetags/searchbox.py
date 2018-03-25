# -*- coding:utf-8 -*-
import re
import os
from django import template
from django.utils.safestring import mark_safe
from django.conf import settings

register = template.Library()


def get_url(url_kwargs):
    current_article_type_id = url_kwargs.get("article_type_id") if url_kwargs.get("article_type_id") else "0"
    current_category_id = url_kwargs.get("category_id") if url_kwargs.get("category_id") else "0"
    current_tags__nid = url_kwargs.get("tags__nid") if url_kwargs.get("tags__nid") else "0"
    current_url_list = [current_article_type_id,current_category_id,current_tags__nid]
    each_url_list = current_url_list[:]
    return current_url_list,each_url_list


def title(index):
    title_dict = {
        0:"网站分类",
        1:"个人分类",
        2:"个人标签",
    }
    return title_dict.get(index)


def process_searchbox_data(url_kwargs,target_list,index):
    """

    :param url_kwargs: 格式:{'article_type_id': '2', 'category_id': '4', 'tags__nid': '20'}
    :param target_list:支持两种格式，
        type_list ：[(1, 'Python'), (2, 'Linux'), (3, 'OpenStack'), (4, 'GoLang')]
        category_objs <QuerySet [<Category: gzl - 类1>, <Category: gzl - 学习笔记>, <Category: gzl - 实验还原>, <Category: gzl - 引用别人>, <Category: gzl - 日韩>]>
    :param index:  0:对应type 1：category 2：tags
    :return:
    """
    current_url_list,each_url_list = get_url(url_kwargs)
    target_html = ["<div>"]
    # 在前面加一个“全部”标签
    if str(current_url_list[index]) == "0":
        each_url_list[index] = 0
        tmp = '''<span>{title}：</span><a class ="active" href="/backend/article-{article_type_id}-{category_id}-{tags__nid}.html" > {target_list} </a>''' \
            .format(title=title(index), article_type_id=each_url_list[0], category_id=each_url_list[1],
                    tags__nid=each_url_list[2],
                    target_list="全部")
    else:
        each_url_list[index] = 0
        tmp = '''<span>{title}：</span><a href="/backend/article-{article_type_id}-{category_id}-{tags__nid}.html" > {target_list} </a>''' \
            .format(title=title(index), article_type_id=each_url_list[0], category_id=each_url_list[1],
                    tags__nid=each_url_list[2],
                    target_list="全部")
    target_html.append(tmp)
    if target_list:
        # 逐个列出数据库中各个元素如 Python Linux OpenStack GoLang
        for item in target_list:
            # 为了同时支持list、QuerySet，把里面的元素统一格式为list
            if not isinstance(item,tuple):
                item = [item.nid,item.title]

            each_url_list[index] = item[0]

            if str(current_url_list[index]) == str(item[0]):
                tmp = '''<a class ="active" href="/backend/article-{article_type_id}-{category_id}-{tags__nid}.html" > {target_list} </a>'''\
                .format(article_type_id=each_url_list[0],category_id=each_url_list[1],tags__nid=each_url_list[2],target_list=item[1])
            else:
                tmp = '''<a href="/backend/article-{article_type_id}-{category_id}-{tags__nid}.html" > {target_list} </a>''' \
                .format(article_type_id=each_url_list[0], category_id=each_url_list[1], tags__nid=each_url_list[2],
                            target_list=item[1])

            target_html.append(tmp)
    target_html.append("</div>")
    return mark_safe("\n".join(target_html))


@register.simple_tag
def searchbox_html(url_kwargs,target_list,index):
    return process_searchbox_data(url_kwargs,target_list,index)

@register.simple_tag
def searchbox_css():
    pass

@register.simple_tag
def searchbox_js():
    pass