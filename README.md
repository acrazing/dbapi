# dbapi

一个基于网页爬取的豆瓣API SDK（目前只有豆瓣小组部分）。

## 先说有趣的事儿

1. 登录客户端：因为客户端有缓存Session，所以你只需要登录一次，在命令行中：
    ```bash
    python -m dbapi.DoubanAPI test_client login "username" "password"
    ```
2. 删除自己回复过的帖子：因为要删除自己发的帖子实际上是要删除掉所有自己在帖子下的回复，如果回复非常多不知道自己回复的在哪一页或者自己的回复非常多，操作起来会比较恶心
    ```bash
    python -m dbapi.DoubanAPI test_api remove_commented_topic "topic_id"
    # topic_id 可以通过下面这个命令拿到：
    python -m dbapi.DoubanAPI test_api list_commented_topics
    # 这个命令会返回所有自己回复过的帖子
    ```
3. 删除自己发的帖子：因为要先删除所有的回复，所以也很恶心
    ```bash
    python -m dbapi.DoubanAPI test_api remove_topic "topic_id"
    # topic_id 可以通过下面这个命令拿到：
    python -m dbapi.DoubanAPI test_api list_user_topics
    # 这个命令会返回所有自己发布的帖子
    ```
4. 获取豆瓣用户关系链：参考[test/relation.py](./test/relation.py)中的代码，这里面既没有锁，也没有队列，只用到了几个原子性操作来确保并发安全。这个代码是用来爬取活跃用户的，没有保存关系链，目前我注册了四个账号在后台跑，两秒一次目前还没有触发机器人，最开始只用了一个种子用户[sevear](https://www.douban.com/people/sevear/)，对所有关注者大于100的进行爬取，后来逐步加到了现在的`10000`，爬取过的用户保存在[__relation__.json](./__relation__.json)中，筛选过的用户保存在[__result__.json](./__result__.json)中。如果要自己跑这个脚本的话，需要clone一下这个repo，因为没有发布到pip源当中：
    ```bash
    git clone https://github.com/acrazing/dbapi.git
    cd dbapi
    pip install -r requirements.txt
    # 将爬虫账户信息保存在文件中：帐户理论上越多越好，但是过多的话IO和网络会形成瓶颈，
    # 但是你也肯定没有那么多帐号对吧~
    echo -e "user:pass\nuser:pass\n..." > accounts.dat
    # 启动爬虫，这里会利用__relation__.json中的结果，如果要从最新的开始爬的话可以
    # 删掉这个文件再爬取，这样的话init_users必需要有，并且要满足你的筛选条件
    # 参数都不是必需的，都有默认值
    # 启动后Ctrl+C终止程序，会自动保存结果，这个只在Win上测试过，因为我这几天在用一
    # 台五年前的Win笔记本（真的好难用，还是Cent和Mac大法好），如果在你的机器上有Bug的
    # 话，欢迎提交PR或者Issue~
    python -m test.relation init_users=user,user,... min_rev=10000
    ```
5. 你也可以自己做自己的爬虫，也可以添加自己的API接口，欢迎提PR~

## 已知的BUG

- [x] 线程假死：怀疑是网络引起的，`requests`加了`timeout`限制之后没有复现
- [ ] 有内存泄漏，跑`test/relation.py`的时候时间久了内存会爆

## 安装

```bash
pip install dbapi
```

## 代码使用

```python
from dbapi import DoubanAPI
api = DoubanAPI()
api.login('username', 'password')
```

## 命令行使用

还未专门做入口，暂时用测试API

```bash
# 调用SDK自身API
python -m dbapi.DoubanAPI test_client <method> [...params]
# 其中<method>是要调用的方法，params是传入到方法的参数
# 例如：调用登录接口
python -m dbapi.DoubanAPI test_client login username password

# 调用模块API
python -m dbapi.DoubanAPI test_api <module> <method> [...params]
# 其中<module>是模块名，目前只有`group`（豆瓣小组），<method>是要调用
# 的方法，params是传入的参数
# 例如：搜索小组
python -m dbapi.DoubanAPI test_api group search_groups keyword
```

## API

```python
# import，所有的方法都暴露在这个类下
from dbapi.DoubanAPI import DoubanAPI

# 实例化，cfg中每一项都有默认值，具体看config.py
api = DoubanAPI(cfg={
    'persist_file': '__cache__.dat',  # 用于持久化的文件
    'headers': {},  # 用于HTTP请求伪装浏览器的头
    'logger': 'dbapi',  # 日志ID
    'log_level': logging.DEBUG,  # 日志记录等级
    'log_destination': sys.stderr,  # 日志输出位置
})

# 登录，失败会抛出错误
api.login(username, password)

# 登出
api.logout()

# 如果遭遇了验证码，用这个接口直接设置会话信息，可以是用'; '分隔的字符串
# 也可以是个字典
api.use(cookies)

###########  小组相关API  ############

# 创建小组
api.group.add_group(**kwargs)
# 搜索小组
api.group.search_groups()
# 加入的小组
api.group.list_joined_groups()
# 删除小组
api.group.remove_group()
# 加入小组
api.group.join_group()
# 退出小组
api.group.leave_group()
# 搜索话题
api.group.search_topics()
# 小组的话题
api.group.list_topics()
# 加入的话题
api.group.list_joined_topics()
# 发表的话题
api.group.list_user_topics()
# 评论的话题
api.group.list_commented_topics()
# 喜欢的话题
api.group.list_liked_topics()
# 推荐的话题
api.group.list_reced_topics()
# 创建话题
api.group.add_topic()
# 删除话题
api.group.remove_topic()
# 编辑话题
api.group.update_topic()
# 推荐话题
api.group.rec_topic()
# 喜欢话题
api.group.like_topic()
# 取消推荐话题
api.group.undo_rec_topic()
# 取消喜欢话题
api.group.undo_like_topic()
# 评论列表
api.group.list_comments()
# 添加评论
api.group.add_comment()
# 删除评论
api.group.remove_comment()
# 用户在话题下的评论列表
api.group.list_user_comments()
# 删除回复的话题（删除所有回复）
api.group.remove_commented_topic()


######## 用户相关API ##########

# 获取用户信息
api.people.get_people(user_alias=None)

# 关注用户列表
api.people.list_contacts(user_alias=None, start=0)

# 关注者列表
api.people.list_rev_contacts(user_alias=None, start=0)

```

## Roadmap

- [x] SDK核心结构
- [X] 小组核心API
- [ ] 小组完整API
- [x] 完善文档
- [x] 发布
- [ ] 命令行入口

## Requirements

- requests
- lxml

Thanks!

## License

MIT