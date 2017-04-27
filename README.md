# dbapi

学习Python，自制基于`xpath`的豆瓣小组API SDK。

**目前还在开发中，尚未发布，仅作观赏用**

## 下载

```bash
git clone https://github.com/acrazing/dbapi.git
cd dbapi

# 安装依赖
pip install --upgrade requests lxml
```

## 使用说明

```python
from dbapi import DoubanAPI
api = DoubanAPI()
# 模拟登录，登录结果会缓存，详细文档以后再说
# 登录次数多了会命中蛋疼的验证码，请小心！
api.login('username', 'password')
# 如果命中了验证码又没有登录，直接用这个接口填写Cookie
api.use(cookies)
# 调用豆瓣小组搜索小组API
api.group.search_groups('keyword')
```

命令行中使用（仅作为测试）

```bash
python -m dbapi.DoubanAPI test_api search_groups keyword
```

## API列表

```python
# 创建实例
api = DoubanAPI()

# 登录
api.login(username, password)

# 设置Cookie
api.use(cookies)

### 小组相关

# 创建小组，未实现
api.group.add_group(**kwargs)

# 搜索小组，start参数多用于翻页
api.group.search_groups(keyword, start=0)

# 加入的小组列表，所有人
api.group.list_joined_groups(user_alias=None)

# 删除小组
api.group.remove_group(group_id)

# 加入小组
api.group.join_group(group_alias, message=None)

# 离开小组
api.group.leave_group(group_alias)

# 搜索话题
api.group.search_topics(keyword, sort='relevance', start=0)

# 小组内的话题，所有人
api.group.list_topics(group_alias, _type='', start=0)

# 已加入小组的所有话题，仅本人
api.group.list_joined_topics(start=0)

# 发表的话题, 仅本人
api.group.list_user_topics(user_alias=None, start=0)

# 回复过的话题列表，仅本人
api.group.list_commented_topics(start=0)

api.group.list_liked_topics(user_alias=None, start=0)

# 推荐的话题列表
api.group.list_reced_topics(user_alias=None, start=0)

# 创建话题(验证码真的好恶心哦, 假设通过测试了)
api.group.add_topic(group_alias, title, content)

# 删除话题
api.group.remove_topic(topic_id)

# 编辑话题
api.group.update_topic(topic_id, title, content)

# 推荐话题
api.group.rec_topic(topic_id)

# 喜欢话题
api.group.like_topic(topic_id)

api.group.undo_rec_topic(topic_id)

api.group.undo_like_topic(topic_id)

# 回复列表
api.group.list_comments(topic_id, start=0)

# 添加回复
api.group.add_comment(topic_id, content, reply_id=None)

# 删除回复
api.group.remove_comment(topic_id, comment_id, reason='0', other=None)

# 用户在话题下的回复列表，全部，不作翻页
api.group.list_user_comments(topic_id, user_alias=None)

# 删除回复过的话题（需要删除所有的回复）
api.group.remove_commented_topic(topic_id)
```

## Roadmap

- [x] SDK核心结构
- [X] 小组核心API
- [ ] 小组完整API
- [ ] 完善文档
- [ ] 发布

## License

MIT