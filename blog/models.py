from django.db import models
import django.utils.timezone as timezone

class UserInfo(models.Model):
    """
    用户表
    """
    nid = models.BigAutoField(primary_key=True)
    username = models.CharField(verbose_name='用户名', max_length=32, unique=True)
    password = models.CharField(verbose_name='密码', max_length=64)
    nickname = models.CharField(verbose_name='昵称', max_length=32)
    email = models.EmailField(verbose_name='邮箱', unique=True)
    avatar = models.ImageField(verbose_name='头像',upload_to="static/imgs/avatar",default="static/imgs/avatar/default.jpg")

    create_time = models.DateTimeField(verbose_name='创建时间', default=timezone.now)
    fans = models.ManyToManyField(verbose_name='粉丝们',
                                  to='UserInfo',
                                  through='UserFans',
                                  related_name='f',
                                  through_fields=('user', 'follower'),
                                  )

    def __str__(self):
        return self.username


class Blog(models.Model):
    """
    博客信息
    """
    nid = models.BigAutoField(primary_key=True)
    title = models.CharField(verbose_name='个人博客标题', max_length=64)
    site = models.CharField(verbose_name='个人博客后缀', max_length=32, unique=True)
    theme = models.CharField(verbose_name='博客主题', max_length=32)
    user = models.OneToOneField(to='UserInfo', to_field='nid',on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class UserFans(models.Model):
    """
    互粉关系表
    """
    user = models.ForeignKey(verbose_name='博主', to='UserInfo', to_field='nid', related_name='users',on_delete=models.CASCADE)
    follower = models.ForeignKey(verbose_name='粉丝', to='UserInfo', to_field='nid', related_name='followers',on_delete=models.CASCADE)

    class Meta:
        unique_together = [
            ('user', 'follower'),
        ]


class Category(models.Model):
    """
    博主个人文章分类表
    """
    nid = models.AutoField(primary_key=True)
    title = models.CharField(verbose_name='分类标题', max_length=32)

    blog = models.ForeignKey(verbose_name='所属博客', to='Blog', to_field='nid',on_delete=models.CASCADE)

    def __str__(self):
        return "%s - %s" % (self.blog.title,self.title)


class ArticleDetail(models.Model):
    """
    文章详细表
    """
    content = models.TextField(verbose_name='文章内容', )

    article = models.OneToOneField(verbose_name='所属文章', to='Article', to_field='nid',on_delete=models.CASCADE)


class UpDown(models.Model):
    """
    文章顶或踩
    """
    article = models.ForeignKey(verbose_name='文章', to='Article', to_field='nid',on_delete=models.CASCADE)
    user = models.ForeignKey(verbose_name='赞或踩用户', to='UserInfo', to_field='nid',on_delete=models.CASCADE)
    up = models.BooleanField(verbose_name='是否赞')

    class Meta:
        unique_together = [
            ('article', 'user'),
        ]


class Comment(models.Model):
    """
    评论表
    """
    nid = models.BigAutoField(primary_key=True)
    content = models.CharField(verbose_name='评论内容', max_length=255)
    create_time = models.DateTimeField(verbose_name='创建时间', default=timezone.now)

    reply = models.ForeignKey(verbose_name='回复评论', to='self', related_name='back',blank=True, null=True,on_delete=models.CASCADE)
    article = models.ForeignKey(verbose_name='评论文章', to='Article', to_field='nid',on_delete=models.CASCADE)
    user = models.ForeignKey(verbose_name='评论者', to='UserInfo', to_field='nid',on_delete=models.CASCADE)


class Tag(models.Model):
    nid = models.AutoField(primary_key=True)
    title = models.CharField(verbose_name='标签名称', max_length=32)
    blog = models.ForeignKey(verbose_name='所属博客', to='Blog', to_field='nid',on_delete=models.CASCADE)

    def __str__(self):
        return "%s - %s" % (self.blog.title, self.title)


class Article(models.Model):
    nid = models.BigAutoField(primary_key=True)
    title = models.CharField(verbose_name='文章标题', max_length=128)
    summary = models.CharField(verbose_name='文章简介', max_length=255)
    read_count = models.IntegerField(default=0)
    comment_count = models.IntegerField(default=0)
    up_count = models.IntegerField(default=0)
    down_count = models.IntegerField(default=0)
    create_time = models.DateTimeField(verbose_name='创建时间',default=timezone.now)

    blog = models.ForeignKey(verbose_name='所属博客', to='Blog', to_field='nid',on_delete=models.CASCADE)
    category = models.ForeignKey(verbose_name='文章类型', to='Category', to_field='nid', null=True,on_delete=models.CASCADE)

    type_choices = [
        (1, "Python"),
        (2, "Linux"),
        (3, "OpenStack"),
        (4, "GoLang"),
    ]

    article_type_id = models.IntegerField(choices=type_choices, default=None)


    tags = models.ManyToManyField(
        to="Tag",
        through='Article2Tag',
        through_fields=('article', 'tag'),
    )
    def __str__(self):
        return "%s - %s" % (self.blog.title,self.title)


class Article2Tag(models.Model):
    article = models.ForeignKey(verbose_name='文章', to="Article", to_field='nid',on_delete=models.CASCADE)
    tag = models.ForeignKey(verbose_name='标签', to="Tag", to_field='nid',on_delete=models.CASCADE)

    class Meta:
        unique_together = [
            ('article', 'tag'),
        ]
