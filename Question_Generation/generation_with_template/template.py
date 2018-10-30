# encoding=utf-8

"""

@author: SimmerChan

@contact: hsl7698590@gmail.com

@file: template.py

@time: 2018/6/24 22:01

@desc:

"""
import random
from SPARQLWrapper import SPARQLWrapper, JSON
from collections import OrderedDict
import pymongo
import re
import jieba

user_dict = []
SPARQL_PREXIX = u"""
PREFIX : <http://www.cadal.zju.edu.cn/bns/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
"""


class JenaFuseki:
    def __init__(self, endpoint_url='http://localhost:3030/chronicle_kg/query'):
        self.sparql_conn = SPARQLWrapper(endpoint_url)

    def get_sparql_result(self, query):
        self.sparql_conn.setQuery(query)
        self.sparql_conn.setReturnFormat(JSON)
        return self.sparql_conn.query().convert()

    @staticmethod
    def parse_result_into_list(query_result):
        query_head = query_result['head']['vars']
        query_results = list()
        for r in query_result['results']['bindings']:
            temp_dict = OrderedDict()
            for h in query_head:
                try:
                    temp_dict[h] = r[h]['value']
                except KeyError:
                    continue
            query_results.append(temp_dict)
        return query_head, query_results

    def print_result_to_string(self, query_result):
        query_head, query_results = self.parse_result_into_list(query_result)
        for h in query_head:
            print(h, ' ' * 5,)
        print()
        for qr in query_results:
            for _, value in qr.iteritems():
                print(value, ' ',)
            print()

    def get_sparql_result_value(self, query_result):
        _, query_results = self.parse_result_into_list(query_result)
        values = list()
        for qr in query_results:
            for _, value in qr.iteritems():
                values.append(value)
        return values


sparql_point = JenaFuseki()

#######################################################################################
# Define Relation Keyword Mapping
#######################################################################################
personal_info_map = {'personAppellation': [u'称谓', u'称号', u'称呼', u'名号'],
                     'alternateNameOrPreviouslyUsedName': [u'别名', u'曾用名'],
                     'courtesyName': [u'字'],
                     'dharmaName': [u'法号'],
                     'posthumousName': [u'谥号'],
                     'personDeathAge': [u'享年'],
                     'personEthnicity': [u'种族', u'民族'],
                     'dynasty': [u'朝代'],
                     'personBirthYear': [u'出生', u'出生日期', u'生日', u'诞辰'],
                     'personDeathYear': [u'忌日']}


status_map = {'hasStatus': [u'身份', u'职业']}

work_map = {'hasText': [u'作品', u'创作', u'著述', u'著作', u'撰述']}

author_map = {'hasAuthor': [u'作者']}

kinship_relation_map = {'hasChild': [u'子女', u'儿女', u'孩子'],
                        'hasSon': [u'儿子', u'子嗣'],
                        'hasDaughter': [u'女儿', u'闺女', u'姑娘', u'丫头'],
                        'hasHusband': [u'丈夫', u'爱人', u'先生', u'老公', u'配偶', u'老伴'],
                        'hasParent': [u'双亲', u'父母', u'爹娘', u'爹妈', u'考妣'],
                        'hasFather': [u'爸爸', u'父亲', u'爹', u'老子', u'爹爹', u'老爹'],
                        'hasMother': [u'妈妈', u'母亲', u'娘', u'娘亲'],
                        'hasSibling': [u'兄妹', u'同胞', u'兄弟姐妹'],
                        'hasBrother': [u'兄弟', u'弟兄', u'昆仲', u'雁行', u'棠棣'],
                        'hasElderBrother': [u'哥哥', u'兄长'],
                        'hasYoungerBrother': [u'弟弟'],
                        'hasSister': [u'姊妹', u'姐妹'],
                        'hasElderSister': [u'姐姐', u'胞姐'],
                        'hasYoungerSister': [u'妹妹', u'胞妹', ],
                        'hasWife': [u'爱人', u'配偶', u'妻妾', u'老婆', u'夫人', u'太太', u'娘子', u'媳妇儿', u'老伴', u'妾', u'妻子', u'爱妻']}

all_relation_map = dict()
all_relation_map.update(personal_info_map)
all_relation_map.update(kinship_relation_map)
all_relation_map.update(status_map)
all_relation_map.update(author_map)
all_relation_map.update(work_map)

for v in all_relation_map.values():
    for word in v:
        user_dict.append(word)

############################################################################################
# Question 相关定义
################################################################################


class Question:
    def __init__(self):
        self.sparql = None
        self.relation = list()
        self.question = list()

    def get_random_generation_samples(self):
        raise NotImplementedError

pattern = re.compile(u'\(.+\)|（.+）')

################################################################################
# Question 1，XX的XX是谁？
# 李世民的儿子是谁？
################################################################################


class Question1(Question):
    def __init__(self, fusuki):
        # type: (JenaFuseki) -> None
        """

        :param fusuki:
        """
        Question.__init__(self)
        self.fusuki = fusuki
        self.sparql = u"{prefix}" \
                      u"SELECT DISTINCT ?s ?x ?o ?y WHERE {{" \
                      u"?s :personName ?x ." \
                      u"?s :{relation} ?o ." \
                      u"?o :personName ?y}}"

        self.question.append({'question': u'{subject}的{predicate}是谁？', 'label': u'{0}O{1}OOO'})
        self.question.append({'question': u'{subject}的{predicate}？', 'label': u'{0}O{1}O'})
        self.relation.append('hasChild')
        self.relation.append('hasSon')
        self.relation.append('hasDaughter')
        self.relation.append('hasHusband')
        self.relation.append('hasParent')
        self.relation.append('hasFather')
        self.relation.append('hasMother')
        self.relation.append('hasSibling')
        self.relation.append('hasBrother')
        self.relation.append('hasElderBrother')
        self.relation.append('hasYoungerBrother')
        self.relation.append('hasSister')
        self.relation.append('hasElderSister')
        self.relation.append('hasYoungerSister')
        self.relation.append('hasWife')

    def get_random_generation_samples(self, sample_num=100):
        self.random_relation = random.choice(self.relation)
        sparql = self.sparql.format(prefix=SPARQL_PREXIX, relation=self.random_relation)
        sparql_result = self.fusuki.get_sparql_result(sparql)
        random_samples = self.parse_sparql_result(sparql_result, sample_num)
        return random_samples

    def parse_sparql_result(self, result, sample_num=100):
        result_list = result['results']['bindings']
        if len(result_list) > sample_num:
            result_list = random.sample(result_list, sample_num)

        parsed_result_list = list()
        for r in result_list:
            subject = r['s']['value']
            predicate = self.random_relation

            subject_word = r['x']['value']
            predicate_word = random.choice(all_relation_map[self.random_relation])
            answer = r['y']['value']
            if re.search(pattern, subject_word) or re.search(pattern, answer):
                continue

            question_tmp = random.choice(self.question)
            question = question_tmp['question'].format(subject=subject_word, predicate=predicate_word)
            subject_word_len = len(subject_word)
            if subject_word_len == 1:
                sub_label = 'B'
            elif subject_word_len == 2:
                sub_label = 'BE'
            else:
                sub_label = 'B' + (subject_word_len - 2) * 'M' + 'E'
            question_label = question_tmp['label'].format(sub_label, len(predicate_word) * 'O')

            parsed_result_list.append([subject, predicate, question, question_label, answer, subject_word, predicate_word])

        return parsed_result_list

################################################################################
# Question 2，XX的XX是什么？
# 李白的别名是什么
################################################################################


class Question2(Question):
    def __init__(self, fusuki):
        # type: (JenaFuseki) -> None
        """

        :param fusuki:
        """
        Question.__init__(self)
        self.fusuki = fusuki
        self.sparql = u"{prefix}" \
                      u"SELECT DISTINCT ?s ?x ?o WHERE {{" \
                      u"?s :personName ?x ." \
                      u"?s :{relation} ?o ." \
                      u"}}"

        self.question.append({'question': u'{subject}的{predicate}是什么？', 'label': u'{0}O{1}OOOO'})
        self.question.append({'question': u'{subject}的{predicate}？', 'label': u'{0}O{1}O'})
        self.relation.append('personAppellation')
        self.relation.append('alternateNameOrPreviouslyUsedName')
        self.relation.append('dharmaName')
        self.relation.append('posthumousName')
        self.relation.append('personDeathAge')
        self.relation.append('personEthnicity')
        self.relation.append('dynasty')
        self.relation.append('personBirthYear')
        self.relation.append('personDeathYear')

    def get_random_generation_samples(self, sample_num=100):
        self.random_relation = random.choice(self.relation)
        sparql = self.sparql.format(prefix=SPARQL_PREXIX, relation=self.random_relation)
        sparql_result = self.fusuki.get_sparql_result(sparql)
        random_samples = self.parse_sparql_result(sparql_result, sample_num)
        return random_samples

    def parse_sparql_result(self, result, sample_num=100):
        result_list = result['results']['bindings']
        if len(result_list) > sample_num:
            result_list = random.sample(result_list, sample_num)

        parsed_result_list = list()
        for r in result_list:
            subject = r['s']['value']
            predicate = self.random_relation
            answer = r['o']['value']

            subject_word = r['x']['value']
            predicate_word = random.choice(all_relation_map[self.random_relation])

            question_tmp = random.choice(self.question)
            question = question_tmp['question'].format(subject=subject_word, predicate=predicate_word)
            subject_word_len = len(subject_word)
            if subject_word_len == 1:
                sub_label = 'B'
            elif subject_word_len == 2:
                sub_label = 'BE'
            else:
                sub_label = 'B' + (subject_word_len - 2) * 'M' + 'E'
            question_label = question_tmp['label'].format(sub_label, len(predicate_word) * 'O')

            parsed_result_list.append([subject, predicate, question, question_label, answer, subject_word, predicate_word])

        return parsed_result_list

################################################################################
# Question 3，XX有什么作品？
# 李白的作品
################################################################################


class Question3(Question):
    def __init__(self, fusuki):
        # type: (JenaFuseki) -> None
        """

        :param fusuki:
        """
        Question.__init__(self)
        self.fusuki = fusuki
        self.sparql = u"{prefix}" \
                      u"SELECT DISTINCT ?s ?x ?o ?y WHERE {{" \
                      u"?s :personName ?x ." \
                      u"?s :{relation} ?o ." \
                      u"?o :textTitle ?y}}"

        self.question.append({'question': u'{subject}的{predicate}有哪些？', 'label': u'{0}O{1}OOOO'})
        self.question.append({'question': u'{subject}有哪些{predicate}？', 'label': u'{0}OOO{1}O'})
        self.relation.append('hasText')

    def get_random_generation_samples(self, sample_num=100):
        self.random_relation = random.choice(self.relation)
        sparql = self.sparql.format(prefix=SPARQL_PREXIX, relation=self.random_relation)
        sparql_result = self.fusuki.get_sparql_result(sparql)
        random_samples = self.parse_sparql_result(sparql_result, sample_num)
        return random_samples

    def parse_sparql_result(self, result, sample_num=100):
        result_list = result['results']['bindings']
        if len(result_list) > sample_num:
            result_list = random.sample(result_list, sample_num)

        parsed_result_list = list()
        for r in result_list:
            subject = r['s']['value']
            predicate = self.random_relation

            subject_word = r['x']['value']
            predicate_word = random.choice(all_relation_map[self.random_relation])
            answer = r['y']['value']
            if re.search(pattern, subject_word) or re.search(pattern, answer):
                continue

            question_tmp = random.choice(self.question)
            question = question_tmp['question'].format(subject=subject_word, predicate=predicate_word)
            subject_word_len = len(subject_word)
            if subject_word_len == 1:
                sub_label = 'B'
            elif subject_word_len == 2:
                sub_label = 'BE'
            else:
                sub_label = 'B' + (subject_word_len - 2) * 'M' + 'E'
            question_label = question_tmp['label'].format(sub_label, len(predicate_word) * 'O')

            parsed_result_list.append([subject, predicate, question, question_label, answer, subject_word, predicate_word])

        return parsed_result_list

################################################################################
# Question 4，XX是谁的作品？
# 登黄鹤楼是谁的作品？
################################################################################


class Question4(Question):
    def __init__(self, fusuki):
        # type: (JenaFuseki) -> None
        """

        :param fusuki:
        """
        Question.__init__(self)
        self.fusuki = fusuki
        self.sparql = u"{prefix}" \
                      u"SELECT DISTINCT ?s ?x ?o ?y WHERE {{" \
                      u"?s :textTitle ?x ." \
                      u"?s :{relation} ?o ." \
                      u"?o :personName ?y}}"

        self.question.append({'question': u'{subject}是谁的作品？', 'label': u'{0}OOOOOO'})
        self.question.append({'question': u'{subject}的作者是谁？', 'label': u'{0}OOOOOO'})
        self.question.append({'question': u'谁写的{subject}？', 'label': u'OOO{0}O'})
        self.relation.append('hasAuthor')

    def get_random_generation_samples(self, sample_num=100):
        self.random_relation = random.choice(self.relation)
        sparql = self.sparql.format(prefix=SPARQL_PREXIX, relation=self.random_relation)
        sparql_result = self.fusuki.get_sparql_result(sparql)
        random_samples = self.parse_sparql_result(sparql_result, sample_num)
        return random_samples

    def parse_sparql_result(self, result, sample_num=100):
        result_list = result['results']['bindings']
        if len(result_list) > sample_num:
            result_list = random.sample(result_list, sample_num)

        parsed_result_list = list()
        for r in result_list:
            subject = r['s']['value']
            predicate = self.random_relation

            subject_word = r['x']['value']
            predicate_word = random.choice(all_relation_map[self.random_relation])
            answer = r['y']['value']
            if re.search(pattern, subject_word) or re.search(pattern, answer):
                continue

            question_tmp = random.choice(self.question)
            question = question_tmp['question'].format(subject=subject_word)
            subject_word_len = len(subject_word)
            if subject_word_len == 1:
                sub_label = 'B'
            elif subject_word_len == 2:
                sub_label = 'BE'
            else:
                sub_label = 'B' + (subject_word_len - 2) * 'M' + 'E'
            question_label = question_tmp['label'].format(sub_label, len(predicate_word) * 'O')

            parsed_result_list.append([subject, predicate, question, question_label, answer, subject_word, predicate_word])

        return parsed_result_list

################################################################################
# Question 5，XX的职业是什么？
# 黄庭坚是做什么的？
################################################################################


class Question5(Question):
    def __init__(self, fusuki):
        # type: (JenaFuseki) -> None
        """

        :param fusuki:
        """
        Question.__init__(self)
        self.fusuki = fusuki
        self.sparql = u"{prefix}" \
                      u"SELECT DISTINCT ?s ?x ?o ?y WHERE {{" \
                      u"?s :personName ?x ." \
                      u"?s :{relation} ?o ." \
                      u"?o :statusName ?y}}"

        self.question.append({'question': u'{subject}是做什么的？', 'label': u'{0}OOOOOO'})
        self.question.append({'question': u'{subject}是干什么的？', 'label': u'{0}OOOOOO'})
        self.question.append({'question': u'{subject}的职业是什么？', 'label': u'{0}OOOOOOO'})
        self.question.append({'question': u'{subject}的身份是什么？', 'label': u'{0}OOOOOOO'})
        self.relation.append('hasStatus')

    def get_random_generation_samples(self, sample_num=100):
        self.random_relation = random.choice(self.relation)
        sparql = self.sparql.format(prefix=SPARQL_PREXIX, relation=self.random_relation)
        sparql_result = self.fusuki.get_sparql_result(sparql)
        random_samples = self.parse_sparql_result(sparql_result, sample_num)
        return random_samples

    def parse_sparql_result(self, result, sample_num=100):
        result_list = result['results']['bindings']
        if len(result_list) > sample_num:
            result_list = random.sample(result_list, sample_num)

        parsed_result_list = list()
        for r in result_list:
            subject = r['s']['value']
            predicate = self.random_relation

            subject_word = r['x']['value']
            predicate_word = random.choice(all_relation_map[self.random_relation])
            answer = r['y']['value']
            if re.search(pattern, subject_word) or re.search(pattern, answer):
                continue

            question_tmp = random.choice(self.question)
            question = question_tmp['question'].format(subject=subject_word)
            subject_word_len = len(subject_word)
            if subject_word_len == 1:
                sub_label = 'B'
            elif subject_word_len == 2:
                sub_label = 'BE'
            else:
                sub_label = 'B' + (subject_word_len - 2) * 'M' + 'E'
            question_label = question_tmp['label'].format(sub_label, len(predicate_word) * 'O')

            parsed_result_list.append([subject, predicate, question, question_label, answer, subject_word, predicate_word])

        return parsed_result_list

if __name__ == '__main__':
    # TODO connect to mongodb
    db_client = pymongo.MongoClient()
    db = db_client['chronicle_training_data']
    collection = db['pattern_auto_generated_data']

    questions = list()
    questions.append(Question1(sparql_point))
    questions.append(Question2(sparql_point))
    questions.append(Question3(sparql_point))
    # questions.append(Question4(sparql_point))
    questions.append(Question5(sparql_point))

    samples = list()
    brackets_pattern = re.compile('[\(\)（）]')
    while True:
        q = random.choice(questions)
        tmp = q.get_random_generation_samples()
        if len(tmp) != 0:
            for t in tmp:
                if t not in samples:
                    if re.search(brackets_pattern, t[2]):
                        continue
                    user_dict.append(t[5])
                    samples.append(t)

            count = len(samples)
            print('Count:{0}'.format(count))

            if count > 100000:
                break

    fields = ['subject', 'predicate', 'question', 'question_label', 'answer', 'subject_word', 'predicate_word',
              'segmented']

    # TODO load dict
    jieba.load_userdict(user_dict)

    for s in samples:
        segmented = ' '.join(jieba.lcut(s[2]))
        s.append(segmented)

    samples_dict = [dict(zip(fields, s)) for s in samples]

    collection.insert(samples_dict)




