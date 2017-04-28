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

TODO

## 详细文档

<https://acrazing.github.io/dbapi/doc/>

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