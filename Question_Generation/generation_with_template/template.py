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
            print h, ' ' * 5,
        print
        for qr in query_results:
            for _, value in qr.iteritems():
                print value, ' ',
            print

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
personal_info_map = {'personAppellation': [u'³ÆÎ½', u'³ÆºÅ', u'³Æºô', u'ÃûºÅ'],
                     'alternateNameOrPreviouslyUsedName': [u'±ðÃû', u'ÔøÓÃÃû'],
                     'courtesyName': [u'×Ö'],
                     'dharmaName': [u'·¨ºÅ'],
                     'posthumousName': [u'ÚÖºÅ'],
                     'personDeathAge': [u'ÏíÄê'],
                     'personEthnicity': [u'ÖÖ×å', u'Ãñ×å'],
                     'dynasty': [u'³¯´ú'],
                     'personBirthYear': [u'³öÉú', u'³öÉúÈÕÆÚ', u'ÉúÈÕ', u'µ®³½'],
                     'personDeathYear': [u'¼ÉÈÕ']}


status_map = {'hasStatus': [u'Éí·Ý', u'Ö°Òµ']}

work_map = {'hasText': [u'×÷Æ·', u'´´×÷', u'ÖøÊö', u'Öø×÷', u'×«Êö']}

author_map = {'hasAuthor': [u'×÷Õß']}

kinship_relation_map = {'hasChild': [u'×ÓÅ®', u'¶ùÅ®', u'º¢×Ó'],
                        'hasSon': [u'¶ù×Ó', u'×ÓËÃ'],
                        'hasDaughter': [u'Å®¶ù', u'¹ëÅ®', u'¹ÃÄï', u'Ñ¾Í·'],
                        'hasHusband': [u'ÕÉ·ò', u'°®ÈË', u'ÏÈÉú', u'ÀÏ¹«', u'ÅäÅ¼', u'ÀÏ°é'],
                        'hasParent': [u'Ë«Ç×', u'¸¸Ä¸', u'µùÄï', u'µùÂè', u'¿¼åþ'],
                        'hasFather': [u'°Ö°Ö', u'¸¸Ç×', u'µù', u'ÀÏ×Ó', u'µùµù', u'ÀÏµù'],
                        'hasMother': [u'ÂèÂè', u'Ä¸Ç×', u'Äï', u'ÄïÇ×'],
                        'hasSibling': [u'ÐÖÃÃ', u'Í¬°û', u'ÐÖµÜ½ãÃÃ'],
                        'hasBrother': [u'ÐÖµÜ', u'µÜÐÖ', u'À¥ÖÙ', u'ÑãÐÐ', u'ÌÄé¦'],
                        'hasElderBrother': [u'¸ç¸ç', u'ÐÖ³¤'],
                        'hasYoungerBrother': [u'µÜµÜ'],
                        'hasSister': [u'æ¢ÃÃ', u'½ãÃÃ'],
                        'hasElderSister': [u'½ã½ã', u'°û½ã'],
                        'hasYoungerSister': [u'ÃÃÃÃ', u'°ûÃÃ', ],
                        'hasWife': [u'°®ÈË', u'ÅäÅ¼', u'ÆÞæª', u'ÀÏÆÅ', u'·òÈË', u'Ì«Ì«', u'Äï×Ó', u'Ï±¸¾¶ù', u'ÀÏ°é', u'æª', u'ÆÞ×Ó', u'°®ÆÞ']}

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
# Question Ïà¹Ø¶¨Òå
################################################################################


class Question:
    def __init__(self):
        self.sparql = None
        self.relation = list()
        self.question = list()

    def get_random_generation_samples(self):
        raise NotImplementedError

pattern = re.compile(u'\(.+\)|£¨.+£©')

################################################################################
# Question 1£¬XXµÄXXÊÇË­£¿
# ÀîÊÀÃñµÄ¶ù×ÓÊÇË­£¿
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

        self.question.append({'question': u'{subject}µÄ{predicate}ÊÇË­£¿', 'label': u'{0}O{1}OOO'})
        self.question.append({'question': u'{subject}µÄ{predicate}£¿', 'label': u'{0}O{1}O'})
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
# Question 2£¬XXµÄXXÊÇÊ²Ã´£¿
# Àî°×µÄ±ðÃûÊÇÊ²Ã´
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

        self.question.append({'question': u'{subject}µÄ{predicate}ÊÇÊ²Ã´£¿', 'label': u'{0}O{1}OOOO'})
        self.question.append({'question': u'{subject}µÄ{predicate}£¿', 'label': u'{0}O{1}O'})
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
# Question 3£¬XXÓÐÊ²Ã´×÷Æ·£¿
# Àî°×µÄ×÷Æ·
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

        self.question.append({'question': u'{subject}µÄ{predicate}ÓÐÄÄÐ©£¿', 'label': u'{0}O{1}OOOO'})
        self.question.append({'question': u'{subject}ÓÐÄÄÐ©{predicate}£¿', 'label': u'{0}OOO{1}O'})
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
# Question 4£¬XXÊÇË­µÄ×÷Æ·£¿
# µÇ»Æº×Â¥ÊÇË­µÄ×÷Æ·£¿
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

        self.question.append({'question': u'{subject}ÊÇË­µÄ×÷Æ·£¿', 'label': u'{0}OOOOOO'})
        self.question.append({'question': u'{subject}µÄ×÷ÕßÊÇË­£¿', 'label': u'{0}OOOOOO'})
        self.question.append({'question': u'Ë­Ð´µÄ{subject}£¿', 'label': u'OOO{0}O'})
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
# Question 5£¬XXµÄÖ°ÒµÊÇÊ²Ã´£¿
# »ÆÍ¥¼áÊÇ×öÊ²Ã´µÄ£¿
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

        self.question.append({'question': u'{subject}ÊÇ×öÊ²Ã´µÄ£¿', 'label': u'{0}OOOOOO'})
        self.question.append({'question': u'{subject}ÊÇ¸ÉÊ²Ã´µÄ£¿', 'label': u'{0}OOOOOO'})
        self.question.append({'question': u'{subject}µÄÖ°ÒµÊÇÊ²Ã´£¿', 'label': u'{0}OOOOOOO'})
        self.question.append({'question': u'{subject}µÄÉí·ÝÊÇÊ²Ã´£¿', 'label': u'{0}OOOOOOO'})
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
    questions.append(Question4(sparql_point))
    questions.append(Question5(sparql_point))

    samples = list()
    while True:
        q = random.choice(questions)
        tmp = q.get_random_generation_samples()
        if len(tmp) != 0:
            for t in tmp:
                if t not in samples:
                    user_dict.append(t[5])
                    samples.append(t)

            count = len(samples)
            print 'Count:{0}'.format(count)

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