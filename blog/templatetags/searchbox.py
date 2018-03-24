# -*- coding:utf-8 -*-
import re
import os
from django import template
from django.utils.safestring import mark_safe
from django.conf import settings

register = template.Library()


# ,category_objs,tag_objs
# def process_searchbox_data(current_article_type_id,current_category_id,current_tags__nid,type_list):
#     test_html = []
#     if type_list:
#         for item in type_list:
#             if str(current_article_type_id) == str(item[0]):
#                 tmp = '''<a class ="active" href="/backend/article-{article_type_id}-{category_id}-{tags__nid}.html" > {article_type_title} </a>'''\
#                 .format(article_type_id=item[0],article_type_title=item[1],category_id=current_category_id,tags__nid=current_tags__nid)
#             else:
#                 tmp = '''<a href="/backend/article-{article_type_id}-{category_id}-{tags__nid}.html" > {article_type_title} </a>'''\
#                 .format(article_type_id=item[0],article_type_title=item[1],category_id=current_category_id,tags__nid=current_tags__nid)
#             test_html.append(tmp)
#     return mark_safe("\n".join(test_html))


def process_searchbox_data(url_kwargs,target_list,index):
    """

    :param url_kwargs: 格式:{'article_type_id': '2', 'category_id': '4', 'tags__nid': '20'}
    :param target_list:支持两种格式，
        type_list ：[(1, 'Python'), (2, 'Linux'), (3, 'OpenStack'), (4, 'GoLang')]
        category_objs <QuerySet [<Category: gzl - 类1>, <Category: gzl - 学习笔记>, <Category: gzl - 实验还原>, <Category: gzl - 引用别人>, <Category: gzl - 日韩>]>
    :param index:
    :return:
    """
    current_article_type_id = url_kwargs.get("article_type_id")
    current_category_id = url_kwargs.get("category_id")
    current_tags__nid = url_kwargs.get("tags__nid")
    new_url_list = [current_article_type_id,current_category_id,current_tags__nid]
    target_html = ["<div>"]
    if target_list:
        for item in target_list:
            # 为了同时支持list、QuerySet，把里面的元素统一格式为list
            if not isinstance(item,tuple):
                item = [item.nid,item.title]

            new_url_list[index] = item[0]
            if str(new_url_list[index]) == str(item[0]):
            # if str(current_article_type_id) == str(item[0]):
                tmp = '''<a class ="active" href="/backend/article-{article_type_id}-{category_id}-{tags__nid}.html" > {target_list} </a>'''\
                .format(article_type_id=new_url_list[0],category_id=new_url_list[1],tags__nid=new_url_list[2],target_list=item[1])
            else:
                tmp = '''<a href="/backend/article-{article_type_id}-{category_id}-{tags__nid}.html" > {target_list} </a>''' \
                .format(article_type_id=new_url_list[0], category_id=new_url_list[1], tags__nid=new_url_list[2],
                            target_list=item[1])
            target_html.append(tmp)
    target_html.append("</div>")
    return mark_safe("\n".join(target_html))


# @register.simple_tag
# def searchbox_html(url_kwargs,type_list,category_objs,tag_objs):
#     return process_searchbox_data(url_kwargs,type_list,category_objs,tag_objs)
@register.simple_tag
def searchbox_html(url_kwargs,target_list,index):
    return process_searchbox_data(url_kwargs,target_list,index)

@register.simple_tag
def searchbox_css():
    pass

@register.simple_tag
def searchbox_js():
    pass