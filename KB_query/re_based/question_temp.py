# encoding=utf-8

"""

@author: SimmerChan

@contact: 7698590@qq.com

@file: question_temp.py

@time: 2017/12/6 14:11

@desc: 问题模板

"""
from refo import finditer, Predicate, Star, Any
import re

# TODO SPARQL前缀和模板
SPARQL_PREXIX = u"""
PREFIX : <http://www.cadal.zju.edu.cn/bns/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
"""

SPARQL_SELECT_TEM = u"{prefix}\n" + \
                    u"SELECT DISTINCT {select} WHERE {{\n" + \
                    u"{expression}\n" + \
                    u"}}\n"

SPARQL_COUNT_TEM = u"{prefix}\n" + \
                   u"SELECT COUNT({select}) WHERE {{\n" + \
                   u"{expression}\n" + \
                   u"}}\n"

# TODO 如果有同名的人，那么返回属性最多的一个
SPARQL_SPECIFIC_TEM = u"{{ SELECT ?s (count(distinct ?o) as ?count) WHERE {{" \
                      u"?s :personName '{person}' ." \
                      u"?s ?p ?o. }}" \
                      u"GROUP BY ?s " \
                      u"ORDER BY DESC(?count) LIMIT 1" \
                      u"}}"

# TODO 返回第一个次序
SPARQL_SEQUENCE = u"ORDER BY ?sequence LIMIT 1"


class W(Predicate):
    def __init__(self, token=".*", pos=".*"):
        self.token = re.compile(token + "$")
        self.pos = re.compile(pos + "$")
        super(W, self).__init__(self.match)

    def match(self, word):
        m1 = self.token.match(word.token)
        m2 = self.pos.match(word.pos)
        return m1 and m2


class Rule(object):
    def __init__(self, condition_num, condition=None, action=None):
        assert condition and action
        self.condition = condition
        self.action = action
        self.condition_num = condition_num

    def apply(self, sentence):
        matches = []
        for m in finditer(self.condition, sentence):
            i, j = m.span()
            matches.extend(sentence[i:j])

        return self.action(matches), self.condition_num


class KeywordRule(object):
    def __init__(self, condition=None, action=None):
        assert condition and action
        self.condition = condition
        self.action = action

    def apply(self, sentence):
        matches = []
        for m in finditer(self.condition, sentence):
            i, j = m.span()
            matches.extend(sentence[i:j])
        if len(matches) == 0:
            return None
        else:
            return self.action()


class PersonalOtherInfoQuestionSet:
    """
    人的对象属性相关问题
    """

    def __init__(self):
        pass

    @staticmethod
    def has_kinship_question(word_objects):
        """

        :param word_objects:
        :return:
        """
        select = u"?x"
        keyword = None
        for r in kinship_keyword_rules:
            keyword = r.apply(word_objects)

            if keyword is not None:
                break

        sparql = None
        for w in word_objects:
            if w.pos == pos_person:
                e = u"?s :personName '{person}' ." \
                    u"?s {keyword} ?o ." \
                    u"?o :personName ?x".format(person=w.token, keyword=keyword)

                sparql = SPARQL_SELECT_TEM.format(prefix=SPARQL_PREXIX,
                                                  select=select,
                                                  expression=e)
                break
        return sparql

    @staticmethod
    def has_kinship_number_question(word_objects):
        """

        :param word_objects:
        :return:
        """
        select = u"?x"
        keyword = None
        for r in kinship_keyword_rules:
            keyword = r.apply(word_objects)

            if keyword is not None:
                break

        sparql = None
        for w in word_objects:
            if w.pos == pos_person:
                e = u"?s :personName '{person}' ." \
                    u"?s {keyword} ?o ." \
                    u"?o :personName ?x".format(person=w.token, keyword=keyword)

                sparql = SPARQL_COUNT_TEM.format(prefix=SPARQL_PREXIX,
                                                 select=select,
                                                 expression=e)
                break
        return sparql

    @staticmethod
    def has_been_to_place_question(word_objects):
        """
        查询人物去过哪些地方
        :param word_objects:
        :return:
        """
        # print 'been to '
        select = u"?x"

        sparql = None
        for w in word_objects:
            if w.pos == pos_person:
                e = (u"?s :personName '{person}' ."
                     u"?s :hasRelationWithPlace ?n ."
                     u"?n :hasAddress ?m. "
                     u"?m :placeAddress ?x. " + SPARQL_SPECIFIC_TEM).format(person=w.token)

                sparql = SPARQL_SELECT_TEM.format(prefix=SPARQL_PREXIX,
                                                  select=select,
                                                  expression=e)
                break
        return sparql

    @staticmethod
    def has_specific_relation_with_place_question(word_objects):
        """
        查询人物具体关系的地点，比如出生地，籍贯等
        :param word_objects:
        :return:
        """
        # print 'has_specific_relation_with_place_question'
        select = u"?x"
        keyword = None
        for r in place_relation_keyword_rules:
            keyword = r.apply(word_objects)

            if keyword is not None:
                break
        # print 'keyword:{0}'.format(keyword)

        sparql = None
        for w in word_objects:
            if w.pos == pos_person:
                e = (u"?s :personName '{person}' ."
                     u"?s :hasRelationWithPlace ?n ."
                     u"?n a {keyword} ."
                     u"?n :hasAddress ?m ."
                     u"?m :placeAddress ?x" + SPARQL_SPECIFIC_TEM).format(person=w.token,
                                                                          keyword=keyword)

                sparql = SPARQL_SELECT_TEM.format(prefix=SPARQL_PREXIX,
                                                  select=select,
                                                  expression=e)
                break
        return sparql

    @staticmethod
    def has_posting_question(word_objects):
        """
        查询人物有哪些职位
        :param word_objects:
        :return:
        """
        # print 'has posting'
        select = u"?x"

        sparql = None
        for w in word_objects:
            if w.pos == pos_person:
                e = (u"?s :personName '{person}' ."
                     u"?s :hasPosting ?p ."
                     u"?p :hasPostingOffice ?o. "
                     u"?o :officeTitle ?x. " + SPARQL_SPECIFIC_TEM).format(person=w.token)

                sparql = SPARQL_SELECT_TEM.format(prefix=SPARQL_PREXIX,
                                                  select=select,
                                                  expression=e)
                break
        return sparql

    @staticmethod
    def has_posting_and_place_question(word_objects):
        """
        查询人物在哪里干了什么公职
        :param word_objects:
        :return:
        """
        # print 'has posting and place'
        select = u"?x"

        sparql = None
        person_word = None
        office_word = None

        for w in word_objects:
            if w.pos == pos_person:
                person_word = w.token

            if w.pos == pos_office:
                office_word = w.token

        if person_word is not None and office_word is not None:
            e = (u"?s :personName '{person}' ."
                 u"?s :hasPosting ?p ."
                 u"?p :hasPostingOffice ?o. "
                 u"?o :officeTitle '{office}'. "
                 u"?p :hasPostingAddress ?a."
                 u"?a :placeAddress ?x" + SPARQL_SPECIFIC_TEM).format(person=person_word, office=office_word)

            sparql = SPARQL_SELECT_TEM.format(prefix=SPARQL_PREXIX,
                                              select=select,
                                              expression=e)

        return sparql

    @staticmethod
    def has_posting_and_when_question(word_objects):
        """
        查询人物在何时干了什么公职
        :param word_objects:
        :return:
        """
        # print 'has posting and place'
        select = u"?x"

        sparql = None
        person_word = None
        office_word = None

        for w in word_objects:
            if w.pos == pos_person:
                person_word = w.token

            if w.pos == pos_office:
                office_word = w.token

        if person_word is not None and office_word is not None:
            e = (u"?s :personName '{person}' ."
                 u"?s :hasPosting ?p ."
                 u"?p :hasPostingOffice ?o. "
                 u"?o :officeTitle '{office}'. "
                 u"?p :firstYear ?x." + SPARQL_SPECIFIC_TEM).format(person=person_word, office=office_word)

            sparql = SPARQL_SELECT_TEM.format(prefix=SPARQL_PREXIX,
                                              select=select,
                                              expression=e)

        return sparql

    @staticmethod
    def has_work_question(word_objects):
        """
        查询人物有哪些作品
        :param word_objects:
        :return:
        """
        # print 'has work'
        select = u"?x"

        sparql = None
        for w in word_objects:
            if w.pos == pos_person:
                e = (u"?s :personName '{person}' ."
                     u"?s :hasText ?t ."
                     u"?t :textTitle ?x. " + SPARQL_SPECIFIC_TEM).format(person=w.token)

                sparql = SPARQL_SELECT_TEM.format(prefix=SPARQL_PREXIX,
                                                  select=select,
                                                  expression=e)
                break
        return sparql

    @staticmethod
    def has_status_question(word_objects):
        """
        查询人物有哪些身份
        :param word_objects:
        :return:
        """
        # print 'has status'
        select = u"?x"

        sparql = None
        for w in word_objects:
            if w.pos == pos_person:
                e = (u"?s :personName '{person}' ."
                     u"?s :hasStatus ?t ."
                     u"?t :statusName ?x. " + SPARQL_SPECIFIC_TEM).format(person=w.token)

                sparql = SPARQL_SELECT_TEM.format(prefix=SPARQL_PREXIX,
                                                  select=select,
                                                  expression=e)
                break
        return sparql

    @staticmethod
    def has_entry_question(word_objects):
        """
        查询人物入仕方式
        :param word_objects:
        :return:
        """
        # print 'has entry'
        select = u"?x"

        sparql = None
        for w in word_objects:
            if w.pos == pos_person:
                e = (u"?s :personName '{person}' ."
                     u"?s :hasEntry ?t ."
                     u"?t :entrySequence ?sequence ."
                     u"?t :entryName ?x. " + SPARQL_SPECIFIC_TEM).format(person=w.token)

                sparql = SPARQL_SELECT_TEM.format(prefix=SPARQL_PREXIX,
                                                  select=select,
                                                  expression=e)
                break
        return sparql

    @staticmethod
    def has_association_question(word_objects):
        """
        查询和某人具有某种关系的人
        :param word_objects:
        :return:
        """
        # print 'has_association_question'
        select = u"?x"
        keyword = None
        for r in association_keyword_rules:
            keyword = r.apply(word_objects)

            if keyword is not None:
                break
        # print 'keyword:{0}'.format(keyword)

        sparql = None
        for w in word_objects:
            if w.pos == pos_person:
                e = (u"?s :personName '{person}' ."
                     u"?s :hasNonKinshipAssociation ?n ."
                     u"?n rdf:type {keyword} ."
                     u"?n :hasAssociatedPerson ?p ."
                     u"?p :personName ?x" + SPARQL_SPECIFIC_TEM).format(person=w.token,
                                                                          keyword=keyword)

                sparql = SPARQL_SELECT_TEM.format(prefix=SPARQL_PREXIX,
                                                  select=select,
                                                  expression=e)
                break
        return sparql

    @staticmethod
    def has_association_with_specific_person_question(word_objects):
        """
        查询某人和某人是什么关系
        :param word_objects:
        :return:
        """
        # print 'has_association_with_specific_person_question'
        select = u"?x"

        person1 = None
        person2 = None

        for w in word_objects:
            if w.pos == pos_person or w.pos == pos_noun and w.token != association.token:
                if person1 is None:
                    person1 = w.token
                else:
                    person2 = w.token

            if person1 is not None and person2 is not None:
                break

        if person1 is None or person2 is None:
            return None

        e = (u"?s :personName '{person}' ."
             u"?s :hasNonKinshipAssociation ?n ."
             u"?n :hasAssociatedPerson ?p ."
             u"?p :personName '{person_b}' ."
             u"?n :associationName ?x" + SPARQL_SPECIFIC_TEM).format(person=person1, person_b=person2)

        sparql = SPARQL_SELECT_TEM.format(prefix=SPARQL_PREXIX,
                                          select=select,
                                          expression=e)

        return sparql

    @staticmethod
    def has_known_question(word_objects):
        """
        查询某人认识哪些人
        :param word_objects:
        :return:
        """
        # print 'has_known_question'
        select = u"?x"

        sparql = None
        for w in word_objects:
            if w.pos == pos_person:
                e = (u"?s :personName '{person}' ."
                     u"?s :hasNonKinshipAssociation ?n ."
                     u"?n :hasAssociatedPerson ?p ."
                     u"?p :personName ?x" + SPARQL_SPECIFIC_TEM).format(person=w.token)

                sparql = SPARQL_SELECT_TEM.format(prefix=SPARQL_PREXIX,
                                                  select=select,
                                                  expression=e)
                break

        return sparql

    @staticmethod
    def return_child_property():
        return u':hasChild'

    @staticmethod
    def return_son_property():
        return u':hasSon'

    @staticmethod
    def return_daughter_property():
        return u':hasDaughter'

    @staticmethod
    def return_husband_property():
        return u':hasHusband'

    @staticmethod
    def return_parent_property():
        return u':hasParent'

    @staticmethod
    def return_father_property():
        return u':hasFather'

    @staticmethod
    def return_mother_property():
        return u':hasMother'

    @staticmethod
    def return_sibling_property():
        return u':hasSibling'

    @staticmethod
    def return_brother_property():
        return u':hasBrother'

    @staticmethod
    def return_elder_brother_property():
        return u':hasElderBrother'

    @staticmethod
    def return_younger_brother_property():
        return u':hasYoungerBrother'

    @staticmethod
    def return_sister_property():
        return u':hasSister'

    @staticmethod
    def return_elder_sister_property():
        return u':hasElderSister'

    @staticmethod
    def return_younger_sister_property():
        return u':hasYoungerSister'

    @staticmethod
    def return_wife_or_concubine_property():
        return u':hasWifeOrConcubine'

    @staticmethod
    def return_wife_property():
        return u':hasWife'

    @staticmethod
    def return_concubine_property():
        return u':hasConcubine'

    @staticmethod
    def return_kinship_property():
        return u':hasKinship'

    @staticmethod
    def return_birth_place_property():
        return u':BirthPlace'

    @staticmethod
    def return_affiliation_property():
        return u':BasicAffiliation'

    @staticmethod
    def return_burial_address_property():
        return u':BurialAddress'

    @staticmethod
    def return_death_address_property():
        return u':DeathAddress'

    @staticmethod
    def return_visited_or_went_to_property():
        return u':VisitedOrWentTo'

    @staticmethod
    def return_social_association_property():
        return u':SocialAssociation'

    @staticmethod
    def return_scholarship_association_property():
        return u':ScholarshipAssociation'

    @staticmethod
    def return_friendship_association_property():
        return u':FriendshipAssociation'

    @staticmethod
    def return_politics_association_property():
        return u':PoliticsAssociation'

    @staticmethod
    def return_writings_association_property():
        return u':WritingsAssociation'

    @staticmethod
    def return_military_association_property():
        return u':MilitaryAssociation'

    @staticmethod
    def return_medicine_association_property():
        return u':MedicineAssociation'

    @staticmethod
    def return_religion_association_property():
        return u':ReligionAssociation'

    @staticmethod
    def return_family_association_property():
        return u':FamilyAssociation'

    @staticmethod
    def return_finance_association_property():
        return u':FinanceAssociation'


class PersonalBasicInfoQuestionSet:
    """
    人的数据属性相关问题
    """

    def __init__(self):
        pass

    @staticmethod
    def has_appellation_question(word_objects):
        """
        查询人物的称谓
        :param word_objects:
        :return:
        """
        # print 'appellation'
        select = u"?x"
        keyword = None
        for r in personal_info_keyword_rules:
            keyword = r.apply(word_objects)

            if keyword is not None:
                break
        # print 'keyword:{0}'.format(keyword)

        sparql = None
        for w in word_objects:
            if w.pos == pos_person:
                e = (u"?s :personName '{person}' ."
                     u"" u"?s {keyword} ?x ." + SPARQL_SPECIFIC_TEM).format(person=w.token,
                                                                            keyword=keyword)

                sparql = SPARQL_SELECT_TEM.format(prefix=SPARQL_PREXIX,
                                                  select=select,
                                                  expression=e)
                break
        return sparql

    @staticmethod
    def has_death_age_question(word_objects):
        """
        查询人物的享年
        :param word_objects:
        :return:
        """
        # print 'has_death_age_question'
        select = u"?x"

        sparql = None
        for w in word_objects:
            if w.pos == pos_person:
                e = (u"?s :personName '{person}' ."
                     u"?s :personDeathAge ?x ." + SPARQL_SPECIFIC_TEM).format(person=w.token)

                sparql = SPARQL_SELECT_TEM.format(prefix=SPARQL_PREXIX,
                                                  select=select,
                                                  expression=e)
                break
        return sparql

    @staticmethod
    def has_ethnicity_question(word_objects):
        """
        查询人物的民族
        :param word_objects:
        :return:
        """
        # print 'has_ethnicity_question'
        select = u"?x"

        sparql = None
        for w in word_objects:
            if w.pos == pos_person:
                e = (u"?s :personName '{person}' ."
                     u"?s :personEthnicity ?x ." + SPARQL_SPECIFIC_TEM).format(person=w.token)

                sparql = SPARQL_SELECT_TEM.format(prefix=SPARQL_PREXIX,
                                                  select=select,
                                                  expression=e)
                break
        return sparql

    @staticmethod
    def has_dynasty_question(word_objects):
        """
        查询人物的朝代
        :param word_objects:
        :return:
        """
        # print 'has_dynasty_question'
        select = u"?x"

        sparql = None
        for w in word_objects:
            if w.pos == pos_person:
                e = (u"?s :personName '{person}' ."
                     u"?s :dynasty ?x ." + SPARQL_SPECIFIC_TEM) \
                    .format(person=w.token)

                sparql = SPARQL_SELECT_TEM.format(prefix=SPARQL_PREXIX,
                                                  select=select,
                                                  expression=e)
                break
        return sparql

    @staticmethod
    def has_birth_question(word_objects):
        """
        查询人物的出生日期
        :param word_objects:
        :return:
        """
        # print 'has_birth_question'
        select = u"?x"

        sparql = None
        for w in word_objects:
            if w.pos == pos_person:
                e = (u"?s :personName '{person}' ."
                     u"?s :personBirthYear ?x" + SPARQL_SPECIFIC_TEM).format(
                    person=w.token)

                sparql = SPARQL_SELECT_TEM.format(prefix=SPARQL_PREXIX,
                                                  select=select,
                                                  expression=e)
                break
        return sparql

    @staticmethod
    def has_death_question(word_objects):
        """
        查询人物的逝世日期
        :param word_objects:
        :return:
        """
        # print 'death'
        select = u"?x"

        sparql = None
        for w in word_objects:
            if w.pos == pos_person:
                e = (u"?s :personName '{person}' ."
                     u"?s :personDeathYear ?x ." + SPARQL_SPECIFIC_TEM).format(person=w.token)

                sparql = SPARQL_SELECT_TEM.format(prefix=SPARQL_PREXIX,
                                                  select=select,
                                                  expression=e)
                break
        return sparql

    @staticmethod
    def return_appellation_property():
        return u':personAppellation'

    @staticmethod
    def return_alternate_name_or_previously_used_name_property():
        return u':alternateNameOrPreviouslyUsedName'

    @staticmethod
    def return_courtesy_name_property():
        return u':courtesyName'

    @staticmethod
    def return_studio_name_or_style_name_property():
        return u':studioNameOrStyleName'

    @staticmethod
    def return_posthumous_name_property():
        return u':posthumousName'

    @staticmethod
    def return_enfeoffment_title_property():
        return u':enfeoffmentTitle'

    @staticmethod
    def return_childhood_name_property():
        return u':childhoodName'

    @staticmethod
    def return_childhood_courtesy_name_property():
        return u':childhoodCourtesyName'

    @staticmethod
    def return_bestowed_name_property():
        return u':bestowedName'

    @staticmethod
    def return_secular_surname_property():
        return u':secularSurname'

    @staticmethod
    def return_secular_personal_name_property():
        return u':secularPersonalName'

    @staticmethod
    def return_temple_name_property():
        return u':templeName'

    @staticmethod
    def return_honorific_name_property():
        return u':honorificName'

    @staticmethod
    def return_temple_title_property():
        return u':templeTitle'

    @staticmethod
    def return_other_transliterated_name_property():
        return u':otherTransliteratedName'

    @staticmethod
    def return_original_surname_property():
        return u':originalSurname'

    @staticmethod
    def return_dharma_name_property():
        return u':dharmaName'

    @staticmethod
    def return_birth_order_property():
        return u':birthOrder'


# TODO 定义词性
pos_person = "nr"
pos_place = "ns"
pos_office = "nz"
pos_noun = "n"
person = (W(pos=pos_person))
place = (W(pos=pos_place))
office = (W(pos=pos_office))
noun = (W(pos=pos_noun))

# TODO 定义关键词


when = (W("何时") | W("时候"))
where = (W("哪里") | W("哪儿") | W("何地") | W("何处") | W("在") + W("哪"))
stop_words = (W("是") | W("的") | W(pos="uj"))
several = (W("几个") | W("多少"))

# TODO 1.个人信息关键词

# TODO 称谓
appellation = (W("称谓") | W("称号") | W("称呼") | W("名号"))
alternateNameOrPreviouslyUsedName = (W("别名") | W("曾用名"))
courtesyName = (W("字"))
studioNameOrStyleName = (W("别号") | W("室名"))
posthumousName = (W("谥号") | W("谥") + W("号"))
enfeoffmentTitle = (W("封爵"))
childhoodName = (W("小名"))
childhoodCourtesyName = (W("小字"))
bestowedName = (W("赐号"))
secularSurname = (W("俗姓"))
secularPersonalName = (W("俗名"))
templeName = (W("庙号"))
honorificName = (W("尊号") | W("尊") + W("号"))
templeTitle = (W("庙额"))
otherTransliteratedName = (W("其他") + W("译名"))
originalSurname = (W("本姓"))
dharmaName = (W("法号"))
birthOrder = (W("行第") | W("行") + W("第"))
appellation_combination = (appellation | alternateNameOrPreviouslyUsedName | courtesyName | studioNameOrStyleName
                           | posthumousName | enfeoffmentTitle | childhoodName | childhoodCourtesyName | bestowedName
                           | secularSurname | secularPersonalName | templeName | honorificName | templeTitle
                           | otherTransliteratedName | originalSurname | dharmaName | birthOrder)

# TODO 其他信息
deathAge = (W("享年") | W('活') + W('了'))
ethnicity = (W("种族") | W("族") | W("民族"))
choronym = (W("郡望"))
dynasty = (W("朝代"))
birthDate = (W("出生") | W("出生日期") | W("生日") | W("诞辰"))
deathDate = (W("死") | W("忌日"))

# TODO 2. 人与地点的关系
location = (W("地方") | W("地点"))
beenTo = (W("去") + W("过"))
birthPlace = (W("出生地") | W("家乡") | W("故乡") | W("故土") | W("诞生地") | W("出生"))
affiliation = (W("籍贯"))
burialAddress = (W("埋葬") | W("安葬") | W("下葬") | W("入土"))
deathAddress = (W("死亡") | W("死") | W("身故") | W("去世") | W("逝世") | W("过世") | W("死去"))
visitedOrWentTO = (W("游历") | W("游览") | W("旅游") | W("观光"))
place_combination = (birthPlace | affiliation | burialAddress | deathAddress | visitedOrWentTO)

# TODO 3. 亲属关键词
child = (W("子女") | W("儿女") | W("孩子"))
son = (W("儿子") | W("子嗣"))
daughter = (W("女儿") | W("闺女") | W("姑娘") | W("丫头"))
husband = (W("丈夫") | W("爱人") | W("先生") | W("老公") | W("配偶") | W("老伴"))
parent = (W("双亲") | W("父母") | W("爹娘") | W("爹妈") | W("考妣"))
father = (W("爸爸") | W("父亲") | W("爹") | W("老子") | W("爹爹") | W("老爹"))
mother = (W("妈妈") | W("母亲") | W("娘") | W("娘亲"))
sibling = (W("兄妹") | W("同胞") | W("兄弟姐妹"))
brother = (W("兄弟") | W("弟兄") | W("昆仲") | W("雁行") | W("棠棣"))
elder_brother = (W("哥哥") | W("兄长"))
younger_brother = (W("弟弟"))
sister = (W("姊妹") | W("姐妹"))
elder_sister = (W("姐姐") | W("胞姐"))
younger_sister = (W("妹妹") | W("胞妹"))
wife = (W("爱人") | W("配偶") | W("妻妾") | W("老婆") | W("夫人") | W("太太") | W("娘子") | W("媳妇儿") | W("老伴") | W("妾") | W("妻子")| W("爱妻"))
kinship = (W("亲戚") | W("亲属"))
kinship_combination = (child | son | daughter | husband | parent | father | mother | sibling | brother | elder_brother |
                       younger_brother | sister | elder_sister | younger_sister | wife | kinship)

# TODO 4. 职位
posting = (W("任职") | W("职位") | W("官位") | W("官"))

# TODO 5. 作品
work = (W("作品") | W("创作") | W("著述") | W("著作") | W("撰述"))

# TODO 作品种类
unofficial_history = (W("杂史"))
official_history = (W("正史"))
ba_history = (W("霸史"))
privately_compiled_history = W("别史")
pseudo_history = W("野史")
art = (W("艺术"))
novel = (W("小说"))
biography = (W("传记") | W("传略") | W("事略") | W("文传"))
medical = (W("医书") | W("医家"))
military = (W("兵书") | W("兵家") | W("军事"))
travel = (W("游记"))
economics = (W("经济"))
astronomy = (W("天文") | W("天文学"))
political = (W("政书"))
legalists = W("法家")
logicians = W("名家")
confucianist = W("儒家")
taoism = (W("道家") | W("道教"))

genre_combination = (unofficial_history | official_history | ba_history | privately_compiled_history | pseudo_history
                     | art | novel | biography | medical | military | travel | economics | astronomy | political
                     | legalists | logicians | confucianist | taoism)

# TODO 6. 人与事件的关系（目前只有71条记录，数量太少，暂不实现该类查询）

# TODO 7. 人与非亲属关系
know = (W("认识") | W("认得"))
association = (W("关系"))
social_association = (W("社会"))
scholarship_association = (W("学术"))
friendship_association = (W("朋友") | W("友人"))
politics_association = (W("政治") | W("政坛"))
writing_association = (W("著述") | W("创作") | W("著作") | W("撰著") | W("编著"))
military_association = (W("军事"))
medicine_association = (W("医疗") | W("医患") | W("医治") | W("诊疗") | W("治疗") | W("诊治") | W("临床"))
religion_association = (W("宗教"))
family_association = (W("家庭"))
finance_association = (W("财务"))
association_combination = (social_association | scholarship_association | friendship_association | politics_association
                           | writing_association | military_association | medicine_association | religion_association
                           | family_association | family_association | finance_association)

# TODO 8. 人与机构关系（目前只有232条记录，数量太少，暂不实现该类查询）

# TODO 9. 身份
status = (W("身份") | W("职业") | W("干什么") | W("做") + W("什么"))

# TODO 10. 人与入仕关系
entry = (W("入仕") | W("做官"))

# TODO 入仕方式
palace = W("宫廷")
kinship = (W("血亲") | W("亲戚") | W("亲属"))
marriage = (W("姻亲") | W("婚姻") | W("联姻"))
examination = (W("科举") | W("考试"))
school = W("学校")
yin_privilege = W("恩荫")
recruitment = W("征召")
recommendation = (W("荐举") | W("推荐"))
military = W("军功")
talent = (W("技术") | W("专长") | W("特长"))
surrender = W("归降")
purchase = W("进纳")
decree = W("特旨")
religion = W("宗教")
failed_pursuit = W("求官")
specials = W("补官")

entry_combination = (palace | kinship | marriage | examination | school | yin_privilege | recruitment | recommendation
                     | military | talent | surrender | purchase | decree | religion | failed_pursuit | specials)

# TODO 问题匹配规则
"""
1. 某某人的某某亲属是谁。例如：李世民的儿子是谁。
2. 某某人有几个亲属。例如，李世民有几个儿子。
3. 某某人的称谓是什么。例如，李世民的谥号是什么。
4. 某某人去过哪些地方。
5. 某某人与地方具体关系。例如，李世民的出生地在哪
6. 某某人享年多少岁。 例如，李世民活了多少岁
7. 某某人的民族是什么。
8. 某某人是哪个朝代的。
9. 某某人的出生日期。
10. 某某人的忌日。
11. 某某人有哪些职位。
12. 某某人在哪里当的某官。
13. 某某人在什么时候当的某官。
14. 某某人有什么作品。
15. 某某人的职业/身份。
16. 某某人怎么入仕的。
17. 和某某人拥有某关系的人有哪些。
18. 某某人和某某人是什么关系。
19. 某人认识哪些人。
"""
rules = [
    Rule(condition_num=2, condition=person + Star(Any(), greedy=False) + kinship_combination,
         action=PersonalOtherInfoQuestionSet.has_kinship_question),
    Rule(condition_num=3, condition=person + Star(Any(), greedy=False) + several + kinship_combination,
         action=PersonalOtherInfoQuestionSet.has_kinship_number_question),
    Rule(condition_num=2, condition=person + Star(Any(), greedy=False) + appellation_combination,
         action=PersonalBasicInfoQuestionSet.has_appellation_question),
    Rule(condition_num=3,
         condition=person + Star(Any(), greedy=False) + beenTo + Star(Any(), greedy=False) + (where | location),
         action=PersonalOtherInfoQuestionSet.has_been_to_place_question),
    Rule(condition_num=3,
         condition=(person + Star(Any(), greedy=False) + place_combination + Star(Any(), greedy=False) + (
             where | location)) | (person + Star(Any(), greedy=False) + (where | location) + Star(Any(), greedy=False) + place_combination) | person + Star(stop_words, greedy=False) + place_combination,
         action=PersonalOtherInfoQuestionSet.has_specific_relation_with_place_question),
    Rule(condition_num=2, condition=person + Star(Any(), greedy=False) + deathAge,
         action=PersonalBasicInfoQuestionSet.has_death_age_question),
    Rule(condition_num=2, condition=person + Star(Any(), greedy=False) + ethnicity,
         action=PersonalBasicInfoQuestionSet.has_ethnicity_question),
    Rule(condition_num=2, condition=person + Star(Any(), greedy=False) + dynasty,
         action=PersonalBasicInfoQuestionSet.has_dynasty_question),
    Rule(condition_num=3,
         condition=person + Star(Any(), greedy=False) + when + Star(Any(), greedy=False) + birthDate | person + Star(
             stop_words, greedy=False) + birthDate,
         action=PersonalBasicInfoQuestionSet.has_birth_question),
    Rule(condition_num=3, condition=person + Star(Any(), greedy=False) + when + Star(Any(),
                                                                                     greedy=False) + deathDate | person + stop_words + deathDate,
         action=PersonalBasicInfoQuestionSet.has_death_question),
    Rule(condition_num=2, condition=person + Star(Any(), greedy=False) + posting,
         action=PersonalOtherInfoQuestionSet.has_posting_question),
    Rule(condition_num=3, condition=person + Star(Any(), greedy=False) + where + Star(Any(), greedy=False) + office,
         action=PersonalOtherInfoQuestionSet.has_posting_and_place_question),
    Rule(condition_num=3, condition=person + Star(Any(), greedy=False) + when + Star(Any(), greedy=False) + office,
         action=PersonalOtherInfoQuestionSet.has_posting_and_when_question),
    Rule(condition_num=2, condition=person + Star(Any(), greedy=False) + work + Star(Any(), greedy=False),
         action=PersonalOtherInfoQuestionSet.has_work_question),
    Rule(condition_num=2, condition=person + Star(Any(), greedy=False) + status + Star(Any(), greedy=False),
         action=PersonalOtherInfoQuestionSet.has_status_question),
    Rule(condition_num=2, condition=person + Star(Any(), greedy=False) + entry + Star(Any(), greedy=False),
         action=PersonalOtherInfoQuestionSet.has_entry_question),
    Rule(condition_num=3, condition=Star(Any(), greedy=False) + person + Star(Any(), greedy=False) + association_combination + Star(Any(), greedy=False), action=PersonalOtherInfoQuestionSet.has_association_question),
    Rule(condition_num=3, condition=person + Star(Any(), greedy=False) + person + Star(Any(), greedy=False) + association, action=PersonalOtherInfoQuestionSet.has_association_with_specific_person_question),
    Rule(condition_num=2, condition=(person + Star(Any(), greedy=False) + know + Star(Any(), greedy=False)) | (Star(Any(), greedy=False) + know + Star(Any(), greedy=False) + person + Star(Any(), greedy=False)), action=PersonalOtherInfoQuestionSet.has_known_question)
]

# TODO 关键词到具体某个词的匹配
kinship_keyword_rules = [
    KeywordRule(condition=person + Star(Any(), greedy=False) + child,
                action=PersonalOtherInfoQuestionSet.return_child_property),
    KeywordRule(condition=person + Star(Any(), greedy=False) + son,
                action=PersonalOtherInfoQuestionSet.return_son_property),
    KeywordRule(condition=person + Star(Any(), greedy=False) + daughter,
                action=PersonalOtherInfoQuestionSet.return_daughter_property),
    KeywordRule(condition=person + Star(Any(), greedy=False) + husband,
                action=PersonalOtherInfoQuestionSet.return_husband_property),
    KeywordRule(condition=person + Star(Any(), greedy=False) + parent,
                action=PersonalOtherInfoQuestionSet.return_parent_property),
    KeywordRule(condition=person + Star(Any(), greedy=False) + father,
                action=PersonalOtherInfoQuestionSet.return_father_property),
    KeywordRule(condition=person + Star(Any(), greedy=False) + mother,
                action=PersonalOtherInfoQuestionSet.return_mother_property),
    KeywordRule(condition=person + Star(Any(), greedy=False) + sibling,
                action=PersonalOtherInfoQuestionSet.return_sibling_property),
    KeywordRule(condition=person + Star(Any(), greedy=False) + brother,
                action=PersonalOtherInfoQuestionSet.return_brother_property),
    KeywordRule(condition=person + Star(Any(), greedy=False) + elder_brother,
                action=PersonalOtherInfoQuestionSet.return_elder_brother_property),
    KeywordRule(condition=person + Star(Any(), greedy=False) + younger_brother,
                action=PersonalOtherInfoQuestionSet.return_younger_brother_property),
    KeywordRule(condition=person + Star(Any(), greedy=False) + sister,
                action=PersonalOtherInfoQuestionSet.return_sister_property),
    KeywordRule(condition=person + Star(Any(), greedy=False) + elder_sister,
                action=PersonalOtherInfoQuestionSet.return_elder_sister_property),
    KeywordRule(condition=person + Star(Any(), greedy=False) + younger_sister,
                action=PersonalOtherInfoQuestionSet.return_younger_sister_property),
    KeywordRule(condition=person + Star(Any(), greedy=False) + wife,
                action=PersonalOtherInfoQuestionSet.return_wife_property),
    KeywordRule(condition=person + Star(Any(), greedy=False) + kinship,
                action=PersonalOtherInfoQuestionSet.return_kinship_property)
]

personal_info_keyword_rules = [
    KeywordRule(condition=person + Star(Any(), greedy=False) + appellation,
                action=PersonalBasicInfoQuestionSet.return_appellation_property),
    KeywordRule(condition=person + Star(Any(), greedy=False) + alternateNameOrPreviouslyUsedName,
                action=PersonalBasicInfoQuestionSet.return_alternate_name_or_previously_used_name_property),
    KeywordRule(condition=person + Star(Any(), greedy=False) + courtesyName,
                action=PersonalBasicInfoQuestionSet.return_courtesy_name_property),
    KeywordRule(condition=person + Star(Any(), greedy=False) + studioNameOrStyleName,
                action=PersonalBasicInfoQuestionSet.return_studio_name_or_style_name_property),
    KeywordRule(condition=person + Star(Any(), greedy=False) + posthumousName,
                action=PersonalBasicInfoQuestionSet.return_posthumous_name_property),
    KeywordRule(condition=person + Star(Any(), greedy=False) + enfeoffmentTitle,
                action=PersonalBasicInfoQuestionSet.return_enfeoffment_title_property),
    KeywordRule(condition=person + Star(Any(), greedy=False) + childhoodName,
                action=PersonalBasicInfoQuestionSet.return_childhood_name_property),
    KeywordRule(condition=person + Star(Any(), greedy=False) + childhoodCourtesyName,
                action=PersonalBasicInfoQuestionSet.return_childhood_courtesy_name_property),
    KeywordRule(condition=person + Star(Any(), greedy=False) + bestowedName,
                action=PersonalBasicInfoQuestionSet.return_bestowed_name_property),
    KeywordRule(condition=person + Star(Any(), greedy=False) + secularSurname,
                action=PersonalBasicInfoQuestionSet.return_secular_surname_property),
    KeywordRule(condition=person + Star(Any(), greedy=False) + secularPersonalName,
                action=PersonalBasicInfoQuestionSet.return_secular_personal_name_property),
    KeywordRule(condition=person + Star(Any(), greedy=False) + templeName,
                action=PersonalBasicInfoQuestionSet.return_temple_name_property),
    KeywordRule(condition=person + Star(Any(), greedy=False) + honorificName,
                action=PersonalBasicInfoQuestionSet.return_honorific_name_property),
    KeywordRule(condition=person + Star(Any(), greedy=False) + templeTitle,
                action=PersonalBasicInfoQuestionSet.return_temple_title_property),
    KeywordRule(condition=person + Star(Any(), greedy=False) + otherTransliteratedName,
                action=PersonalBasicInfoQuestionSet.return_other_transliterated_name_property),
    KeywordRule(condition=person + Star(Any(), greedy=False) + originalSurname,
                action=PersonalBasicInfoQuestionSet.return_original_surname_property),
    KeywordRule(condition=person + Star(Any(), greedy=False) + dharmaName,
                action=PersonalBasicInfoQuestionSet.return_dharma_name_property),
    KeywordRule(condition=person + Star(Any(), greedy=False) + birthOrder,
                action=PersonalBasicInfoQuestionSet.return_birth_order_property)
]

place_relation_keyword_rules = [
    KeywordRule(condition=(person + Star(Any(), greedy=False) + birthPlace + Star(Any(), greedy=False) + (
        where | location)) | (person + Star(Any(), greedy=False) + (where | location) + Star(Any(), greedy=False) + birthPlace) | (person + Star(
             stop_words, greedy=False) + birthPlace),
                action=PersonalOtherInfoQuestionSet.return_birth_place_property),
    KeywordRule(condition=person + Star(Any(), greedy=False) + affiliation + Star(Any(), greedy=False) + (
        where | location) | person + Star(Any(), greedy=False) + (where | location) + Star(Any(),
                                                                                           greedy=False) + affiliation | person + Star(
        Any(), greedy=False) + affiliation, action=PersonalOtherInfoQuestionSet.return_affiliation_property),
    KeywordRule(condition=person + Star(Any(), greedy=False) + burialAddress + Star(Any(), greedy=False) + (
        where | location) | person + Star(Any(), greedy=False) + (where | location) + Star(Any(),
                                                                                           greedy=False) + burialAddress | person + Star(
        Any(), greedy=False) + burialAddress, action=PersonalOtherInfoQuestionSet.return_burial_address_property),
    KeywordRule(condition=person + Star(Any(), greedy=False) + deathAddress + Star(Any(), greedy=False) + (
        where | location) | person + Star(Any(), greedy=False) + (where | location) + Star(Any(),
                                                                                           greedy=False) + deathAddress | person + Star(
        Any(), greedy=False) + deathAddress, action=PersonalOtherInfoQuestionSet.return_death_address_property),
    KeywordRule(condition=person + Star(Any(), greedy=False) + visitedOrWentTO + Star(Any(), greedy=False) + (
        where | location) | person + Star(Any(), greedy=False) + (where | location) + Star(Any(),
                                                                                           greedy=False) + visitedOrWentTO | person + Star(
        Any(), greedy=False) + visitedOrWentTO, action=PersonalOtherInfoQuestionSet.return_visited_or_went_to_property)
]

association_keyword_rules = [
    KeywordRule(condition=Star(Any(), greedy=False) + person + Star(Any(), greedy=False) + social_association, action=PersonalOtherInfoQuestionSet.return_social_association_property),
    KeywordRule(condition=Star(Any(), greedy=False) + person + Star(Any(), greedy=False) + scholarship_association, action=PersonalOtherInfoQuestionSet.return_scholarship_association_property),
    KeywordRule(condition=Star(Any(), greedy=False) + person + Star(Any(), greedy=False) + friendship_association, action=PersonalOtherInfoQuestionSet.return_friendship_association_property),
    KeywordRule(condition=Star(Any(), greedy=False) + person + Star(Any(), greedy=False) + politics_association, action=PersonalOtherInfoQuestionSet.return_politics_association_property),
    KeywordRule(condition=Star(Any(), greedy=False) + person + Star(Any(), greedy=False) + writing_association, action=PersonalOtherInfoQuestionSet.return_writings_association_property),
    KeywordRule(condition=Star(Any(), greedy=False) + person + Star(Any(), greedy=False) + military_association, action=PersonalOtherInfoQuestionSet.return_military_association_property),
    KeywordRule(condition=Star(Any(), greedy=False) + person + Star(Any(), greedy=False) + medicine_association, action=PersonalOtherInfoQuestionSet.return_medicine_association_property),
    KeywordRule(condition=Star(Any(), greedy=False) + person + Star(Any(), greedy=False) + religion_association, action=PersonalOtherInfoQuestionSet.return_religion_association_property),
    KeywordRule(condition=Star(Any(), greedy=False) + person + Star(Any(), greedy=False) + family_association, action=PersonalOtherInfoQuestionSet.return_family_association_property),
    KeywordRule(condition=Star(Any(), greedy=False) + person + Star(Any(), greedy=False) + finance_association, action=PersonalOtherInfoQuestionSet.return_finance_association_property)

]