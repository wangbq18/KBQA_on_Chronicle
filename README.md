# 基于中国古代编年史的KBQA

## KB_construction

将[CBDB](https://projects.iq.harvard.edu/cbdb)项目存于Sqlite的数据转存到MYSQL。
- [备份文件](https://pan.baidu.com/s/1Whp4nn2lUFqTdNGY6Rj5Xw)，对应的所有数据的SQL文件。
- [备份文件](https://pan.baidu.com/s/1L_Asd5v6I7IpFdAe6cqlSw)，后续项目用到的部分数据的SQL文件。

## KB_query

包含两个模块，re_based与nn_based。re_based实现了基于正则和模板的语义解析及查询功能；nn_based实现了基于深度学习模型的语义解析，查询则是基于知识库实体名称匹配打分机制。sparql engine采用apache jena fuseki。

## KB_service

基于web.py的服务端模块，可对接微信公众号提供服务；也包含了一个简单的web前端页面，提供基于网页的访问和查询。

## Question_Generation

问题生成模块，即给定一个RDF三元组，生成对应的自然语言问题。

- template， 基于模板，人为构造一些问题。
- seq2seq，基于序列到序列的方法，以template构造的数据为基础数据进行模型训练。对于给定主题词和关系，模型可以生成对应的问题。参考[ChineseQG](https://github.com/tyliupku/ChineseQG)。

## Other_resources

- cbdb_kg_mapping.ttl，[d2rq](http://d2rq.org/)的mapping文件，用于将mysql存储的数据用为RDF格式。
- chronicle_schema.owl，编年史的本体结构，可用protege编辑。
