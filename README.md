# dbapi

一个基于网页爬取的豆瓣API SDK（目前只有豆瓣小组部分）。

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