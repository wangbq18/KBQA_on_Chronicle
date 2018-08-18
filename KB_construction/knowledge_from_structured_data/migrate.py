# encoding=utf-8

"""

@author: SimmerChan

@contact: 7698590@qq.com

@file: migrate.py

@time: 2017/11/22 19:04

@desc: 把mysql中简繁转换好的CBDB数据导入到重新设计的mysql数据库中

"""
import pymysql
from collections import OrderedDict


def migrate_person(conn, cursor):
    # type: (pymysql.cursors.DictCursor, pymysql.connections.Connection) -> None
    """
    迁移人物主表
    :param conn:
    :param cursor:
    :return:
    """
    from_table_name = 'cbdb.biog_main'
    to_table_name = 'cbdb_kg.person'

    fields_mapping = OrderedDict()  # 记录两张表对应字段
    fields_mapping['c_personid'] = 'person_id'
    fields_mapping['c_name_chn'] = 'person_name'
    fields_mapping['c_surname_chn'] = 'person_surname'
    fields_mapping['c_mingzi_chn'] = 'person_mingzi'
    fields_mapping['c_female'] = 'person_gender'
    fields_mapping['c_death_age'] = 'person_death_age'
    fields_mapping['c_ethnicity_code'] = 'person_ethnicity'
    fields_mapping['c_choronym_code'] = 'person_choronym'
    fields_mapping['c_dy'] = 'person_dynasty'
    fields_mapping['c_birthyear'] = 'person_birth_year'
    fields_mapping['c_deathyear'] = 'person_death_year'
    fields_mapping['c_by_month'] = 'person_birth_month'
    fields_mapping['c_dy_month'] = 'person_death_month'
    fields_mapping['c_by_day'] = 'person_birth_day'
    fields_mapping['c_dy_day'] = 'person_death_day'
    fields_mapping['c_by_nh_code'] = 'person_birth_nianhao'
    fields_mapping['c_dy_nh_code'] = 'person_death_nianhao'
    fields_mapping['c_by_nh_year'] = 'person_birth_nianhao_year'
    fields_mapping['c_dy_nh_year'] = 'person_death_nianhao_year'
    fields_mapping['c_by_day_gz'] = 'person_birth_day_ganzhi'
    fields_mapping['c_dy_day_gz'] = 'person_death_day_ganzhi'
    fields_mapping['c_fl_earliest_year'] = 'person_floruit_earliest_year'
    fields_mapping['c_fl_latest_year'] = 'person_floruit_latest_year'
    fields_mapping['c_fl_ey_nh_code'] = 'person_floruit_earliest_nianhao'
    fields_mapping['c_fl_ly_nh_code'] = 'person_floruit_latest_nianhao'
    fields_mapping['c_fl_ey_nh_year'] = 'person_floruit_earliest_nianhao_year'
    fields_mapping['c_fl_ly_nh_year'] = 'person_floruit_latest_nianhao_year'

    cursor.execute("""SELECT
    c_personid,
    c_name_chn,
    c_female,
    c_ethnicity_code,
    c_birthyear,
    c_by_nh_code,
    c_by_nh_year,
    c_deathyear,
    c_dy_nh_code,
    c_dy_nh_year,
    c_death_age,
    c_fl_earliest_year,
    c_fl_ey_nh_code,
    c_fl_ey_nh_year,
    c_fl_latest_year,
    c_fl_ly_nh_code,
    c_fl_ly_nh_year,
    c_surname_chn,
    c_mingzi_chn,
    c_dy,
    c_choronym_code,
    c_by_month,
    c_dy_month,
    c_by_day,
    c_dy_day,
    c_by_day_gz,
    c_dy_day_gz
FROM {0}""".format(from_table_name))

    value_placeholder = '%s, ' * (len(fields_mapping) - 1) + '%s'
    fields_str = ''
    for _, v in fields_mapping.iteritems():
        fields_str += v + ','
    fields_str = fields_str[:-1]

    value_list = list()
    for i in cursor.fetchall():
        value = list()
        for k, _ in fields_mapping.iteritems():
            value.append(i[k])
        value_list.append(tuple(value))

    insert_command = "insert into {0} ({1}) values ({2})".format(to_table_name, fields_str, value_placeholder)

    cursor.executemany(insert_command, value_list)
    conn.commit()

    # TODO 根据原cbdb中的其他表，将code值转为对应的实际值
    # TODO 更新性别,民族,郡望,朝代,出生年号,死亡年号,最早年号,最晚年号
    update_commands = ["update cbdb_kg.person set cbdb_kg.person.person_gender='男' where cbdb_kg.person.person_gender='0'",
                       "update cbdb_kg.person set cbdb_kg.person.person_gender='女' where cbdb_kg.person.person_gender='1'",
                       "update cbdb_kg.person set cbdb_kg.person.person_ethnicity=(select cbdb.ethnicity_tribe_codes.c_name_chn from cbdb.ethnicity_tribe_codes where cbdb_kg.person.person_ethnicity=cbdb.ethnicity_tribe_codes.c_ethnicity_code)",
                       "update cbdb_kg.person set cbdb_kg.person.person_choronym=(select cbdb.choronym_codes.c_choronym_chn from cbdb.choronym_codes where cbdb_kg.person.person_choronym=cbdb.choronym_codes.c_choronym_code)",
                       "update cbdb_kg.person set cbdb_kg.person.person_dynasty=(select cbdb.dynasties.c_dynasty_chn from cbdb.dynasties where cbdb_kg.person.person_dynasty=cbdb.dynasties.c_dy)",
                       "update cbdb_kg.person set cbdb_kg.person.person_birth_nianhao=(select cbdb.nian_hao.c_nianhao_chn from cbdb.nian_hao where cbdb_kg.person.person_birth_nianhao=cbdb.nian_hao.c_nianhao_id)",
                       "update cbdb_kg.person set cbdb_kg.person.person_death_nianhao=(select cbdb.nian_hao.c_nianhao_chn from cbdb.nian_hao where cbdb_kg.person.person_death_nianhao=cbdb.nian_hao.c_nianhao_id)",
                       "update cbdb_kg.person set cbdb_kg.person.person_floruit_earliest_nianhao=(select cbdb.nian_hao.c_nianhao_chn from cbdb.nian_hao where cbdb_kg.person.person_floruit_earliest_nianhao=cbdb.nian_hao.c_nianhao_id)",
                       "update cbdb_kg.person set cbdb_kg.person.person_floruit_latest_nianhao=(select cbdb.nian_hao.c_nianhao_chn from cbdb.nian_hao where cbdb_kg.person.person_floruit_latest_nianhao=cbdb.nian_hao.c_nianhao_id)"
                       ]

    for update_command in update_commands:
        cursor.execute(update_command)
    conn.commit()


def migrate_appellation(conn, cursor):
    # type: (pymysql.cursors.DictCursor, pymysql.connections.Connection) -> None
    """
    迁移人物称谓表
    :param conn:
    :param cursor:
    :return:
    """
    from_table_name = 'cbdb.altname_data'
    to_table_name = 'cbdb_kg.appellation'

    fields_mapping = OrderedDict()  # 记录两张表对应字段
    fields_mapping['c_personid'] = 'person_id'
    fields_mapping['c_alt_name_chn'] = 'altname'
    fields_mapping['c_alt_name_type_code'] = 'altname_type'

    cursor.execute("""SELECT
        c_personid,
        c_alt_name_chn,
        c_alt_name_type_code
    FROM {0} WHERE c_personid IN (SELECT cbdb_kg.person.person_id from cbdb_kg.person)""".format(from_table_name))

    value_placeholder = '%s, ' * (len(fields_mapping) - 1) + '%s'
    fields_str = ''
    for _, v in fields_mapping.iteritems():
        fields_str += v + ','
    fields_str = fields_str[:-1]

    value_list = list()
    for i in cursor.fetchall():
        value = list()
        for k, _ in fields_mapping.iteritems():
            value.append(i[k])
        value_list.append(tuple(value))

    insert_command = "insert  into {0} ({1}) values ({2})".format(to_table_name, fields_str, value_placeholder)

    cursor.executemany(insert_command, value_list)
    conn.commit()

    # TODO 根据原cbdb中的其他表，将code值转为对应的实际值
    # TODO 更新称谓类型
    update_commands = [
        "update cbdb_kg.appellation set cbdb_kg.appellation.altname_type=(select cbdb.altname_codes.c_name_type_desc_chn from cbdb.altname_codes where cbdb_kg.appellation.altname_type=cbdb.altname_codes.c_name_type_code) where cbdb_kg.appellation.altname_type in (select cbdb.altname_codes.c_name_type_code from cbdb.altname_codes)",
        "update cbdb_kg.appellation set cbdb_kg.appellation.altname_type='未详' where cbdb_kg.appellation.altname_type not in (select cbdb.altname_codes.c_name_type_code from cbdb.altname_codes)",
        "update cbdb_kg.appellation set altname_type='谥号' where altname_type='諡号'"
        ]

    for update_command in update_commands:
        cursor.execute(update_command)
    conn.commit()


def migrate_kinship(conn, cursor):
    # type: (pymysql.cursors.DictCursor, pymysql.connections.Connection) -> None
    """
    迁移人物亲属表
    :param conn:
    :param cursor:
    :return:
    """
    from_table_name1 = 'cbdb.kin_data'
    from_table_name2 = 'cbdb.kinship_codes'
    to_table_name = 'cbdb_kg.kinship'

    fields_mapping = OrderedDict()  # 记录两张表对应字段
    fields_mapping['c_personid'] = 'person_id'
    fields_mapping['c_kin_id'] = 'kinship_id'
    fields_mapping['c_kin_code'] = 'kinship_type'
    fields_mapping['c_kinrel'] = 'kinship_type_kinrel'

    cursor.execute("""SELECT
            cbdb.kin_data.c_personid,
            cbdb.kin_data.c_kin_id,
            cbdb.kin_data.c_kin_code,
            cbdb.kinship_codes.c_kinrel
        FROM {0}, {1} WHERE c_personid IN (SELECT cbdb_kg.person.person_id from cbdb_kg.person) and cbdb.kinship_codes.c_kincode=cbdb.kin_data.c_kin_code""".format(from_table_name1, from_table_name2))

    value_placeholder = '%s, ' * (len(fields_mapping) - 1) + '%s'
    fields_str = ''
    for _, v in fields_mapping.iteritems():
        fields_str += v + ','
    fields_str = fields_str[:-1]

    value_list = list()
    for i in cursor.fetchall():
        value = list()
        for k, _ in fields_mapping.iteritems():
            value.append(i[k])
        value_list.append(tuple(value))

    insert_command = "insert  into {0} ({1}) values ({2})".format(to_table_name, fields_str, value_placeholder)

    cursor.executemany(insert_command, value_list)
    conn.commit()

    # TODO 根据原cbdb中的其他表，将code值转为对应的实际值
    # TODO 更新亲属类型
    update_commands = [
        "update cbdb_kg.kinship set cbdb_kg.kinship.kinship_type=(select coalesce(nullif(cbdb.kinship_codes.c_kinrel_chn, ''), cbdb.kinship_codes.c_kinrel_alt) from cbdb.kinship_codes where cbdb_kg.kinship.kinship_type=cbdb.kinship_codes.c_kincode) where cbdb_kg.kinship.kinship_type in (select cbdb.kinship_codes.c_kincode from cbdb.kinship_codes)",
        "update cbdb_kg.kinship set cbdb_kg.kinship.kinship_type='未详' where cbdb_kg.kinship.kinship_type not in (select cbdb.kinship_codes.c_kincode from cbdb.kinship_codes)"
    ]

    for update_command in update_commands:
        try:
            cursor.execute(update_command)
        except:
            print update_command
            raise
    conn.commit()


def migrate_status(conn, cursor):
    # type: (pymysql.cursors.DictCursor, pymysql.connections.Connection) -> None
    """
    迁移人物职业表
    :param conn:
    :param cursor:
    :return:
    """
    from_table_name1 = 'cbdb.status_data'
    from_table_name2 = 'cbdb.status_codes'
    to_table_name = 'cbdb_kg.status'

    fields_mapping = OrderedDict()  # 记录两张表对应字段
    fields_mapping['c_personid'] = 'person_id'
    fields_mapping['c_status_desc_chn'] = 'status_name'
    fields_mapping['c_status_desc'] = 'status_name_eng'
    fields_mapping['c_sequence'] = 'status_sequence'
    fields_mapping['c_firstyear'] = 'first_year'
    fields_mapping['c_lastyear'] = 'last_year'
    fields_mapping['c_fy_nh_code'] = 'first_year_nianhao'
    fields_mapping['c_fy_nh_year'] = 'first_year_nianhao_year'
    fields_mapping['c_ly_nh_code'] = 'last_year_nianhao'
    fields_mapping['c_ly_nh_year'] = 'last_year_nianhao_year'

    cursor.execute("""SELECT
            c_personid,
            coalesce(replace(replace(c_status_desc_chn, '[', ''), ']', ''), 'no description') as c_status_desc_chn,
            coalesce(c_status_desc, 'no description') as c_status_desc,
            c_sequence,
            c_firstyear,
            c_lastyear,
            c_fy_nh_code,
            c_fy_nh_year,
            c_ly_nh_code,
            c_ly_nh_year
        FROM {0}, {1} WHERE c_personid IN (SELECT cbdb_kg.person.person_id from cbdb_kg.person) and cbdb.status_data.c_status_code=cbdb.status_codes.c_status_code""".format(from_table_name1, from_table_name2))

    value_placeholder = '%s, ' * (len(fields_mapping) - 1) + '%s'
    fields_str = ''
    for _, v in fields_mapping.iteritems():
        fields_str += v + ','
    fields_str = fields_str[:-1]

    value_list = list()
    for i in cursor.fetchall():
        value = list()
        for k, _ in fields_mapping.iteritems():
            value.append(i[k])
        value_list.append(tuple(value))

    insert_command = "insert  into {0} ({1}) values ({2})".format(to_table_name, fields_str, value_placeholder)

    cursor.executemany(insert_command, value_list)
    conn.commit()

    # TODO 根据原cbdb中的其他表，将code值转为对应的实际值
    # TODO 更新年号
    update_commands = [
        "update cbdb_kg.status set cbdb_kg.status.first_year_nianhao=(select cbdb.nian_hao.c_nianhao_chn from cbdb.nian_hao where cbdb_kg.status.first_year_nianhao=cbdb.nian_hao.c_nianhao_id)",
        "update cbdb_kg.status set cbdb_kg.status.last_year_nianhao=(select cbdb.nian_hao.c_nianhao_chn from cbdb.nian_hao where cbdb_kg.status.last_year_nianhao=cbdb.nian_hao.c_nianhao_id)"
    ]

    for update_command in update_commands:
        try:
            cursor.execute(update_command)
        except:
            print update_command
            raise
    conn.commit()


def migrate_text(conn, cursor):
    # type: (pymysql.cursors.DictCursor, pymysql.connections.Connection) -> None
    """
    迁移作品表
    :param conn:
    :param cursor:
    :return:
    """
    from_table_name1 = 'cbdb.text_codes'
    from_table_name2 = 'cbdb.text_biblcat_types_1'
    to_table_name = 'cbdb_kg.text'

    fields_mapping = OrderedDict()  # 记录两张表对应字段
    fields_mapping['c_textid'] = 'text_id'
    fields_mapping['c_title_chn'] = 'text_title'
    fields_mapping['c_text_cat_desc_chn'] = 'text_genre'
    fields_mapping['c_text_year'] = 'text_composition_year'
    fields_mapping['c_text_nh_code'] = 'text_composition_nianhao'
    fields_mapping['c_text_nh_year'] = 'text_composition_nianhao_year'
    fields_mapping['c_text_dy'] = 'dynasty'
    fields_mapping['c_extant'] = 'text_extant'

    cursor.execute("""SELECT
            c_textid,
            c_title_chn,
            c_text_cat_desc_chn,
            c_text_year,
            c_text_nh_code,
            c_text_nh_year,
            c_text_dy,
            c_extant
        FROM {0}, {1} WHERE cbdb.text_codes.c_bibl_cat_code=cbdb.text_biblcat_types_1.c_text_cat_code""".format(from_table_name1, from_table_name2))

    value_placeholder = '%s, ' * (len(fields_mapping) - 1) + '%s'
    fields_str = ''
    for _, v in fields_mapping.iteritems():
        fields_str += v + ','
    fields_str = fields_str[:-1]

    value_list = list()
    for i in cursor.fetchall():
        value = list()
        for k, _ in fields_mapping.iteritems():
            value.append(i[k])
        value_list.append(tuple(value))

    insert_command = "insert  into {0} ({1}) values ({2})".format(to_table_name, fields_str, value_placeholder)

    cursor.executemany(insert_command, value_list)
    conn.commit()

    # TODO 根据原cbdb中的其他表，将code值转为对应的实际值
    # TODO 更新年号，朝代，存佚情况
    update_commands = [
        "update cbdb_kg.text set cbdb_kg.text.text_composition_nianhao=(select cbdb.nian_hao.c_nianhao_chn from cbdb.nian_hao where cbdb_kg.text.text_composition_nianhao=cbdb.nian_hao.c_nianhao_id)",
        "update cbdb_kg.text set cbdb_kg.text.dynasty=(select cbdb.dynasties.c_dynasty_chn from cbdb.dynasties where cbdb_kg.text.dynasty=cbdb.dynasties.c_dy)",
        "update cbdb_kg.text set cbdb_kg.text.text_extant=(select cbdb.extant_codes.c_extant_desc_chn from cbdb.extant_codes where cbdb_kg.text.text_extant=cbdb.extant_codes.c_extant_code)"
    ]

    for update_command in update_commands:
        try:
            cursor.execute(update_command)
        except:
            print update_command
            raise
    conn.commit()


def migrate_person_text(conn, cursor):
    # type: (pymysql.cursors.DictCursor, pymysql.connections.Connection) -> None
    """
    迁移人物作品对应表
    :param conn:
    :param cursor:
    :return:
    """
    from_table_name = 'cbdb.text_data'
    to_table_name = 'cbdb_kg.person_to_text'

    fields_mapping = OrderedDict()  # 记录两张表对应字段
    fields_mapping['c_personid'] = 'person_id'
    fields_mapping['c_textid'] = 'text_id'

    cursor.execute("""SELECT
            c_personid,
            c_textid
        FROM {0} where c_personid in (select person_id from cbdb_kg.person) and c_textid in (select text_id from cbdb_kg.text)""".format(from_table_name))

    value_placeholder = '%s, ' * (len(fields_mapping) - 1) + '%s'
    fields_str = ''
    for _, v in fields_mapping.iteritems():
        fields_str += v + ','
    fields_str = fields_str[:-1]

    value_list = list()
    for i in cursor.fetchall():
        value = list()
        for k, _ in fields_mapping.iteritems():
            value.append(i[k])
        value_list.append(tuple(value))

    insert_command = "insert  into {0} ({1}) values ({2})".format(to_table_name, fields_str, value_placeholder)

    cursor.executemany(insert_command, value_list)
    conn.commit()


def migrate_place(conn, cursor):
    # type: (pymysql.cursors.DictCursor, pymysql.connections.Connection) -> None
    """
    迁移地点表
    :param conn:
    :param cursor:
    :return:
    """
    from_table_name = 'cbdb.addresses'
    to_table_name = 'cbdb_kg.place'

    fields_mapping = OrderedDict()  # 记录两张表对应字段
    fields_mapping['c_addr_id'] = 'place_raw_id'
    fields_mapping['c_name_chn'] = 'place_name'
    fields_mapping['c_admin_type'] = 'place_admin_type'
    fields_mapping['x_coord'] = 'place_x_coordinate'
    fields_mapping['y_coord'] = 'place_y_coordinate'
    fields_mapping['c_firstyear'] = 'place_first_year'
    fields_mapping['c_lastyear'] = 'place_last_year'

    cursor.execute("""SELECT
            c_addr_id,
            c_name_chn,
            c_admin_type,
            x_coord,
            y_coord,
            c_firstyear,
            c_lastyear
        FROM {0}""".format(from_table_name))

    value_placeholder = '%s, ' * (len(fields_mapping) - 1) + '%s'
    fields_str = ''
    for _, v in fields_mapping.iteritems():
        fields_str += v + ','
    fields_str = fields_str[:-1]

    value_list = list()
    for i in cursor.fetchall():
        value = list()
        for k, _ in fields_mapping.iteritems():
            value.append(i[k])
        value_list.append(tuple(value))

    insert_command = "insert  into {0} ({1}) values ({2})".format(to_table_name, fields_str, value_placeholder)

    cursor.executemany(insert_command, value_list)
    conn.commit()


def migrate_place_to_place(conn, cursor):
    # type: (pymysql.cursors.DictCursor, pymysql.connections.Connection) -> None
    """
    迁移地点表
    :param conn:
    :param cursor:
    :return:
    """
    from_table_name = 'cbdb.addr_belongs_data'
    to_table_name = 'cbdb_kg.place_to_place'

    fields_mapping = OrderedDict()  # 记录两张表对应字段
    fields_mapping['c_addr_id'] = 'place_id'
    fields_mapping['c_belongs_to'] = 'belongs_to_id'
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    cursor.execute("""
select c_addr_id, c_belongs_to from {0} where c_addr_id in (select place_raw_id from cbdb_kg.place) and c_belongs_to in (select place_raw_id from cbdb_kg.place)
""".format(from_table_name))
    value_placeholder = '%s, ' * (len(fields_mapping) - 1) + '%s'
    fields_str = ''
    for _, v in fields_mapping.iteritems():
        fields_str += v + ','
    fields_str = fields_str[:-1]

    value_list = list()
    for i in cursor.fetchall():
        value = list()
        for k, _ in fields_mapping.iteritems():
            value.append(i[k])
        value_list.append(tuple(value))

    insert_command = "insert  into {0} ({1}) values ({2})".format(to_table_name, fields_str, value_placeholder)

    cursor.executemany(insert_command, value_list)
    conn.commit()

    print 'migrate place_to_place done!'
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

    print 'updating place_to_place.......'
    # TODO 把c_addr_id和c_belongs_to映射到cbdb_kg.place表中新增的唯一的place_id上
    update_commands = [
        "update cbdb_kg.place_to_place set cbdb_kg.place_to_place.place_id=(select min(cbdb_kg.place.place_id) from cbdb_kg.place where cbdb_kg.place.place_raw_id=cbdb_kg.place_to_place.place_id)",
        "update cbdb_kg.place_to_place set cbdb_kg.place_to_place.belongs_to_id=(select min(cbdb_kg.place.place_id) from cbdb_kg.place where cbdb_kg.place.place_raw_id=cbdb_kg.place_to_place.belongs_to_id)"
    ]

    cursor.execute("ALTER TABLE cbdb_kg.place_to_place DROP PRIMARY KEY")  # 先移除主键
    for update_command in update_commands:
        try:
            cursor.execute(update_command)
        except:
            print update_command
            raise
    cursor.execute("ALTER TABLE cbdb_kg.place_to_place ADD PRIMARY KEY(place_id, belongs_to_id)")
    conn.commit()
    print 'updating place_to_place done!'


def migrate_mode_of_entry(conn, cursor):
    # type: (pymysql.cursors.DictCursor, pymysql.connections.Connection) -> None
    """
    迁移入仕表
    :param conn:
    :param cursor:
    :return:
    """
    from_table_name = 'cbdb.entry_data'
    to_table_name = 'cbdb_kg.mode_of_entry'

    fields_mapping = OrderedDict()  # 记录两张表对应字段
    fields_mapping['c_personid'] = 'person_id'
    fields_mapping['c_sequence'] = 'entry_sequence'
    fields_mapping['c_entry_code'] = 'entry_type'
    fields_mapping['c_kin_id'] = 'entry_kinship_id'
    fields_mapping['c_assoc_id'] = 'entry_non_kinship_id'
    fields_mapping['c_kin_code'] = 'entry_kinship_type'
    fields_mapping['c_assoc_code'] = 'entry_non_kinship_type'
    fields_mapping['c_addr_id'] = 'place_id'
    fields_mapping['c_age'] = 'entry_age'
    fields_mapping['c_exam_rank'] = 'entry_exam_rank'
    fields_mapping['c_year'] = 'entry_year'
    fields_mapping['c_nianhao_id'] = 'entry_nianhao'
    fields_mapping['c_entry_nh_year'] = 'entry_nianhao_year'

    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    cursor.execute("""SELECT
            c_personid,
            c_sequence,
            c_entry_code,
            c_kin_id,
            c_assoc_id,
            c_kin_code,
            c_assoc_code,
            c_addr_id,
            ABS(c_age) as c_age,
            c_exam_rank,
            c_year,
            c_nianhao_id,
            c_entry_nh_year
        FROM {0} WHERE c_personid in (SELECT person_id FROM cbdb_kg.person)""".format(from_table_name))

    value_placeholder = '%s, ' * (len(fields_mapping) - 1) + '%s'
    fields_str = ''
    for _, v in fields_mapping.iteritems():
        fields_str += v + ','
    fields_str = fields_str[:-1]

    value_list = list()
    for i in cursor.fetchall():
        value = list()
        for k, _ in fields_mapping.iteritems():
            value.append(i[k])
        value_list.append(tuple(value))

    insert_command = "insert  into {0} ({1}) values ({2})".format(to_table_name, fields_str, value_placeholder)

    cursor.executemany(insert_command, value_list)
    conn.commit()
    print 'migrate mode_of_entry done!'
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

    print 'updating mode_of_entry.......'
    # TODO 替换entry_kinship_type, entry_non_kinship_type, place_id, entry_nianhao
    update_commands = [
        "update cbdb_kg.mode_of_entry set cbdb_kg.mode_of_entry.entry_kinship_type=coalesce((select c_kinrel_chn from cbdb.kinship_codes where cbdb.kinship_codes.c_kincode=cbdb_kg.mode_of_entry.entry_kinship_type), '未详')",
        "update cbdb_kg.mode_of_entry set cbdb_kg.mode_of_entry.entry_non_kinship_type=coalesce((select c_assoc_type_desc_chn from cbdb.assoc_types, cbdb.assoc_codes, cbdb.assoc_code_type_rel where cbdb.assoc_codes.c_assoc_code=cbdb_kg.mode_of_entry.entry_non_kinship_type and cbdb.assoc_codes.c_assoc_code=cbdb.assoc_code_type_rel.c_assoc_code and cbdb.assoc_code_type_rel.c_assoc_type_id=cbdb.assoc_types.c_assoc_type_id), '社会关系（笼统）')",
        "update cbdb_kg.mode_of_entry set cbdb_kg.mode_of_entry.place_id=(select cbdb_kg.place.place_id from cbdb_kg.place where cbdb_kg.place.place_raw_id=cbdb_kg.mode_of_entry.place_id limit 1)",
        "update cbdb_kg.mode_of_entry set cbdb_kg.mode_of_entry.entry_nianhao=(select c_nianhao_chn from cbdb.nian_hao where cbdb.nian_hao.c_nianhao_id=cbdb_kg.mode_of_entry.entry_nianhao)"
    ]

    cursor.execute("""
    ALTER TABLE `cbdb_kg`.`mode_of_entry`
DROP FOREIGN KEY `entry_place_id`,
DROP FOREIGN KEY `entry_person_id`,
DROP FOREIGN KEY `entry_non_kinship_id`,
DROP FOREIGN KEY `entry_kinship_id`;
ALTER TABLE `cbdb_kg`.`mode_of_entry`
DROP INDEX `entry_non_kinship_id_idx` ,
DROP INDEX `entry_kinship_id_idx` ,
DROP INDEX `entry_place_id_idx` ;
    """)
    cursor.execute("ALTER TABLE cbdb_kg.mode_of_entry DROP PRIMARY KEY")  # 先移除主键

    for update_command in update_commands:
        try:
            cursor.execute(update_command)
        except:
            print update_command
            raise

    cursor.execute("ALTER TABLE cbdb_kg.mode_of_entry ADD PRIMARY KEY(person_id, entry_sequence, entry_type, entry_kinship_id, entry_non_kinship_id, entry_kinship_type, entry_non_kinship_type, entry_year)")
    cursor.execute("""
    ALTER TABLE `cbdb_kg`.`mode_of_entry`
ADD CONSTRAINT `entry_person_id`
  FOREIGN KEY (`person_id`)
  REFERENCES `cbdb_kg`.`person` (`person_id`)
  ON DELETE NO ACTION
  ON UPDATE NO ACTION,
ADD CONSTRAINT `entry_place_id`
  FOREIGN KEY (`place_id`)
  REFERENCES `cbdb_kg`.`place` (`place_id`)
  ON DELETE NO ACTION
  ON UPDATE NO ACTION,
ADD CONSTRAINT `entry_kinship_id`
  FOREIGN KEY (`entry_kinship_id`)
  REFERENCES `cbdb_kg`.`person` (`person_id`)
  ON DELETE NO ACTION
  ON UPDATE NO ACTION,
ADD CONSTRAINT `entry_non_kinship_id`
  FOREIGN KEY (`entry_non_kinship_id`)
  REFERENCES `cbdb_kg`.`person` (`person_id`)
  ON DELETE NO ACTION
  ON UPDATE NO ACTION;
    """)
    conn.commit()
    print 'updating place_to_place done!'


def migrate_person_to_place(conn, cursor):
    # type: (pymysql.cursors.DictCursor, pymysql.connections.Connection) -> None
    """
    迁移人物地点
    :param conn:
    :param cursor:
    :return:
    """
    # from_table_name = 'cbdb.biog_addr_data'
    # to_table_name = 'cbdb_kg.person_to_place'
    #
    # fields_mapping = OrderedDict()  # 记录两张表对应字段
    # fields_mapping['c_personid'] = 'person_id'
    # fields_mapping['c_addr_id'] = 'place_id'
    # fields_mapping['c_addr_type'] = 'place_type'
    # fields_mapping['c_sequence'] = 'place_sequence'
    # fields_mapping['c_firstyear'] = 'first_year'
    # fields_mapping['c_fy_month'] = 'first_year_month'
    # fields_mapping['c_fy_day'] = 'first_year_day'
    # fields_mapping['c_fy_nh_code'] = 'first_year_nianhao'
    # fields_mapping['c_fy_nh_year'] = 'first_year_nianhao_year'
    # fields_mapping['c_fy_day_gz'] = 'first_year_day_ganzhi'
    # fields_mapping['c_lastyear'] = 'last_year'
    # fields_mapping['c_ly_month'] = 'last_year_month'
    # fields_mapping['c_ly_day'] = 'last_year_day'
    # fields_mapping['c_ly_nh_code'] = 'last_year_nianhao'
    # fields_mapping['c_ly_nh_year'] = 'last_year_nianhao_year'
    # fields_mapping['c_ly_day_gz'] = 'last_year_day_ganzhi'
    #
    # cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    # cursor.execute("""SELECT
    #             c_personid,
    #             c_addr_id,
    #             c_addr_type,
    #             c_sequence,
    #             c_firstyear,
    #             c_fy_month,
    #             c_fy_day,
    #             c_fy_nh_code,
    #             c_fy_nh_year,
    #             c_fy_day_gz,
    #             c_lastyear,
    #             c_ly_month,
    #             c_ly_day,
    #             c_ly_nh_code,
    #             c_ly_nh_year,
    #             c_ly_day_gz
    #         FROM {0} WHERE c_personid in (SELECT person_id FROM cbdb_kg.person)""".format(from_table_name))
    # value_placeholder = '%s, ' * (len(fields_mapping) - 1) + '%s'
    # fields_str = ''
    # for _, v in fields_mapping.iteritems():
    #     fields_str += v + ','
    # fields_str = fields_str[:-1]
    #
    # value_list = list()
    # for i in cursor.fetchall():
    #     value = list()
    #     for k, _ in fields_mapping.iteritems():
    #         value.append(i[k])
    #     value_list.append(tuple(value))
    #
    # insert_command = "insert  into {0} ({1}) values ({2})".format(to_table_name, fields_str, value_placeholder)
    #
    # cursor.executemany(insert_command, value_list)
    # conn.commit()
    # cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    # print 'migrate person_to_place done!'

    print 'updating person_to_place.......'
    # TODO 更新place_id,first_year_nianhao,first_year_day_ganzhi,last_year_nianhao,last_year_day_ganzhi
    update_commands = [
        "update cbdb_kg.person_to_place set cbdb_kg.person_to_place.place_id=coalesce((select cbdb_kg.place.place_id from cbdb_kg.place where cbdb_kg.place.place_raw_id=cbdb_kg.person_to_place.place_id limit 1), 1)",
        "update cbdb_kg.person_to_place set cbdb_kg.person_to_place.first_year_nianhao=(select cbdb.nian_hao.c_nianhao_chn from cbdb.nian_hao where cbdb_kg.person_to_place.first_year_nianhao=cbdb.nian_hao.c_nianhao_id)",
        "update cbdb_kg.person_to_place set cbdb_kg.person_to_place.last_year_nianhao=(select cbdb.nian_hao.c_nianhao_chn from cbdb.nian_hao where cbdb_kg.person_to_place.last_year_nianhao=cbdb.nian_hao.c_nianhao_id)",
        "update cbdb_kg.person_to_place set cbdb_kg.person_to_place.first_year_day_ganzhi=(select cbdb.ganzhi_codes.c_ganzhi_chn from cbdb.ganzhi_codes where cbdb_kg.person_to_place.first_year_day_ganzhi=cbdb.ganzhi_codes.c_ganzhi_code)",
        "update cbdb_kg.person_to_place set cbdb_kg.person_to_place.last_year_day_ganzhi=(select cbdb.ganzhi_codes.c_ganzhi_chn from cbdb.ganzhi_codes where cbdb_kg.person_to_place.last_year_day_ganzhi=cbdb.ganzhi_codes.c_ganzhi_code)"
    ]

    # cursor.execute("ALTER TABLE cbdb_kg.place_to_place DROP PRIMARY KEY")  # 先移除主键
    for update_command in update_commands:
        try:
            cursor.execute(update_command)
        except:
            print update_command
            raise
    # cursor.execute("ALTER TABLE cbdb_kg.place_to_place ADD PRIMARY KEY(place_id, belongs_to_id)")
    conn.commit()
    print 'updating person_to_place done!'


def migrate_non_kinship_association(conn, cursor):
    # type: (pymysql.cursors.DictCursor, pymysql.connections.Connection) -> None
    """
    迁移人物非亲属关系
    :param conn:
    :param cursor:
    :return:
    """
    from_table_name = 'cbdb.assoc_data'
    to_table_name = 'cbdb_kg.non_kinship_association'

    fields_mapping = OrderedDict()  # 记录两张表对应字段
    fields_mapping['c_personid'] = 'person_id'
    fields_mapping['c_addr_id'] = 'place_id'
    fields_mapping['c_assoc_id'] = 'associated_person_id'
    fields_mapping['c_assoc_code'] = 'association_type'
    fields_mapping['c_occasion_code'] = 'association_occasion'
    fields_mapping['c_sequence'] = 'association_sequence'
    fields_mapping['c_text_title'] = 'association_text'
    fields_mapping['c_assoc_year'] = 'association_year'
    fields_mapping['c_assoc_nh_code'] = 'association_nianhao'
    fields_mapping['c_assoc_nh_year'] = 'association_nianhao_year'
    fields_mapping['c_assoc_month'] = 'association_month'
    fields_mapping['c_assoc_day'] = 'association_day'
    fields_mapping['c_assoc_day_gz'] = 'association_day_ganzhi'

    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    cursor.execute("""SELECT
                c_personid,
                c_addr_id,
                c_assoc_id,
                c_assoc_code,
                c_occasion_code,
                c_sequence,
                c_text_title,
                c_assoc_year,
                c_assoc_nh_code,
                c_assoc_nh_year,
                c_assoc_month,
                c_assoc_day,
                c_assoc_day_gz
            FROM {0} WHERE c_personid in (SELECT person_id FROM cbdb_kg.person) and c_assoc_id in (SELECT person_id FROM cbdb_kg.person)""".format(from_table_name))
    value_placeholder = '%s, ' * (len(fields_mapping) - 1) + '%s'
    fields_str = ''
    for _, v in fields_mapping.iteritems():
        fields_str += v + ','
    fields_str = fields_str[:-1]

    value_list = list()
    for i in cursor.fetchall():
        value = list()
        for k, _ in fields_mapping.iteritems():
            value.append(i[k])
        value_list.append(tuple(value))

    insert_command = "insert  into {0} ({1}) values ({2})".format(to_table_name, fields_str, value_placeholder)

    cursor.executemany(insert_command, value_list)
    conn.commit()
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    print 'migrate non_kinship_association done!'

    print 'updating non_kinship_association.......'
    # TODO 更新place_id,association_occasion, association_nianhao,association_day_ganzhi
    update_commands = [
        "update cbdb_kg.non_kinship_association set cbdb_kg.non_kinship_association.place_id=coalesce((select cbdb_kg.place.place_id from cbdb_kg.place where cbdb_kg.place.place_raw_id=cbdb_kg.non_kinship_association.place_id limit 1), 1)",
        "update cbdb_kg.non_kinship_association set cbdb_kg.non_kinship_association.association_occasion=(select cbdb.occasion_codes.c_occasion_desc_chn from cbdb.occasion_codes where cbdb_kg.non_kinship_association.association_occasion=cbdb.occasion_codes.c_occasion_code)",
        "update cbdb_kg.non_kinship_association set cbdb_kg.non_kinship_association.association_nianhao=(select cbdb.nian_hao.c_nianhao_chn from cbdb.nian_hao where cbdb_kg.non_kinship_association.association_nianhao=cbdb.nian_hao.c_nianhao_id)",
        "update cbdb_kg.non_kinship_association set cbdb_kg.non_kinship_association.association_day_ganzhi=(select cbdb.ganzhi_codes.c_ganzhi_chn from cbdb.ganzhi_codes where cbdb_kg.non_kinship_association.association_day_ganzhi=cbdb.ganzhi_codes.c_ganzhi_code)"
    ]

    # cursor.execute("ALTER TABLE cbdb_kg.place_to_place DROP PRIMARY KEY")  # 先移除主键
    for update_command in update_commands:
        try:
            cursor.execute(update_command)
        except:
            print update_command
            raise
    # cursor.execute("ALTER TABLE cbdb_kg.place_to_place ADD PRIMARY KEY(place_id, belongs_to_id)")
    conn.commit()
    print 'updating non_kinship_association done!'


def migrate_institution(conn, cursor):
    # type: (pymysql.cursors.DictCursor, pymysql.connections.Connection) -> None
    """
    迁移机构表
    :param conn:
    :param cursor:
    :return:
    """
    # from_table_name1 = 'cbdb.social_institution_codes'
    # from_table_name2 = 'cbdb.social_institution_addr'
    # to_table_name = 'cbdb_kg.institution'
    #
    # fields_mapping = OrderedDict()  # 记录两张表对应字段
    # fields_mapping['c_inst_code'] = 'institution_id'
    # fields_mapping['c_inst_addr_id'] = 'place_id'
    # fields_mapping['c_inst_name_code'] = 'institution_name'
    # fields_mapping['c_inst_type_code'] = 'institution_type'
    # fields_mapping['c_inst_begin_dy'] = 'institution_begin_dynasty'
    # fields_mapping['c_inst_end_dy'] = 'institution_end_dynasty'
    # fields_mapping['c_inst_floruit_dy'] = 'institution_floruit_dynasty'
    # fields_mapping['c_inst_first_known_year'] = 'institution_first_known_year'
    # fields_mapping['c_inst_last_known_year'] = 'institution_last_known_year'
    # fields_mapping['c_inst_begin_year'] = 'first_year'
    # fields_mapping['c_inst_end_year'] = 'last_year'
    # fields_mapping['c_by_nianhao_code'] = 'first_year_nianhao'
    # fields_mapping['c_ey_nianhao_code'] = 'last_year_nianhao'
    # fields_mapping['c_by_nianhao_year'] = 'first_year_nianhao_year'
    # fields_mapping['c_ey_nianhao_year'] = 'last_year_nianhao_year'
    #
    # cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    # cursor.execute("""SELECT
    #             cbdb.social_institution_codes.c_inst_code as c_inst_code,
    #             c_inst_addr_id,
    #             cbdb.social_institution_codes.c_inst_name_code as c_inst_name_code,
    #             c_inst_type_code,
    #             c_inst_begin_dy,
    #             c_inst_end_dy,
    #             c_inst_floruit_dy,
    #             c_inst_first_known_year,
    #             c_inst_last_known_year,
    #             c_inst_begin_year,
    #             c_inst_end_year,
    #             c_by_nianhao_code,
    #             c_ey_nianhao_code,
    #             c_by_nianhao_year,
    #             c_ey_nianhao_year
    #         FROM {0}, {1} WHERE cbdb.social_institution_codes.c_inst_code=cbdb.social_institution_addr.c_inst_code""".format(from_table_name1, from_table_name2))
    # value_placeholder = '%s, ' * (len(fields_mapping) - 1) + '%s'
    # fields_str = ''
    # for _, v in fields_mapping.iteritems():
    #     fields_str += v + ','
    # fields_str = fields_str[:-1]
    #
    # value_list = list()
    # for i in cursor.fetchall():
    #     value = list()
    #     for k, _ in fields_mapping.iteritems():
    #         value.append(i[k])
    #     value_list.append(tuple(value))
    #
    # insert_command = "insert  into {0} ({1}) values ({2})".format(to_table_name, fields_str, value_placeholder)
    #
    # cursor.executemany(insert_command, value_list)
    # conn.commit()
    # cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    # print 'migrate institution done!'

    print 'updating institution.......'
    # TODO 更新place_id,institution_name, institution_type,institution_begin_dynasty,institution_end_dynasty,institution_floruit_dynasty，first_year_nianhao，last_year_nianhao
    update_commands = [
        "update cbdb_kg.institution set cbdb_kg.institution.place_id=coalesce((select cbdb_kg.place.place_id from cbdb_kg.place where cbdb_kg.place.place_raw_id=cbdb_kg.institution.place_id limit 1), 1)",
        "update cbdb_kg.institution set cbdb_kg.institution.institution_name=(select cbdb.social_institution_name_codes.c_inst_name_hz from cbdb.social_institution_name_codes where cbdb_kg.institution.institution_name=cbdb.social_institution_name_codes.c_inst_name_code)",
        "update cbdb_kg.institution set cbdb_kg.institution.institution_type=(select cbdb.social_institution_types.c_inst_type_hz from cbdb.social_institution_types where cbdb_kg.institution.institution_type=cbdb.social_institution_types.c_inst_type_code)",
        "update cbdb_kg.institution set cbdb_kg.institution.institution_begin_dynasty=(select cbdb.dynasties.c_dynasty_chn from cbdb.dynasties where cbdb_kg.institution.institution_begin_dynasty=cbdb.dynasties.c_dy)",
        "update cbdb_kg.institution set cbdb_kg.institution.institution_end_dynasty=(select cbdb.dynasties.c_dynasty_chn from cbdb.dynasties where cbdb_kg.institution.institution_end_dynasty=cbdb.dynasties.c_dy)",
        "update cbdb_kg.institution set cbdb_kg.institution.institution_floruit_dynasty=(select cbdb.dynasties.c_dynasty_chn from cbdb.dynasties where cbdb_kg.institution.institution_floruit_dynasty=cbdb.dynasties.c_dy)",
        "update cbdb_kg.institution set cbdb_kg.institution.first_year_nianhao=(select cbdb.nian_hao.c_nianhao_chn from cbdb.nian_hao where cbdb_kg.institution.first_year_nianhao=cbdb.nian_hao.c_nianhao_id)",
        "update cbdb_kg.institution set cbdb_kg.institution.last_year_nianhao=(select cbdb.nian_hao.c_nianhao_chn from cbdb.nian_hao where cbdb_kg.institution.last_year_nianhao=cbdb.nian_hao.c_nianhao_id)"
    ]

    # cursor.execute("ALTER TABLE cbdb_kg.place_to_place DROP PRIMARY KEY")  # 先移除主键
    for update_command in update_commands:
        try:
            cursor.execute(update_command)
        except:
            print update_command
            raise
    # cursor.execute("ALTER TABLE cbdb_kg.place_to_place ADD PRIMARY KEY(place_id, belongs_to_id)")
    conn.commit()
    print 'updating institution done!'


def migrate_person_institution(conn, cursor):
    # type: (pymysql.cursors.DictCursor, pymysql.connections.Connection) -> None
    """
    迁移人物机构表
    :param conn:
    :param cursor:
    :return:
    """
    # from_table_name = 'cbdb.biog_inst_data'
    # to_table_name = 'cbdb_kg.person_to_institution'
    #
    # fields_mapping = OrderedDict()  # 记录两张表对应字段
    # fields_mapping['c_personid'] = 'person_id'
    # fields_mapping['c_inst_code'] = 'institution_id'
    # fields_mapping['c_bi_role_code'] = 'institution_type'
    # fields_mapping['c_bi_begin_year'] = 'first_year'
    # fields_mapping['c_bi_end_year'] = 'last_year'
    # fields_mapping['c_bi_by_nh_code'] = 'first_year_nianhao'
    # fields_mapping['c_bi_ey_nh_code'] = 'last_year_nianhao'
    # fields_mapping['c_bi_by_nh_year'] = 'first_year_nianhao_year'
    # fields_mapping['c_bi_ey_nh_year'] = 'last_year_nianhao_year'
    #
    # cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    # cursor.execute("""SELECT
    #             c_personid,
    #             c_inst_code,
    #             c_bi_role_code,
    #             c_bi_begin_year,
    #             c_bi_end_year,
    #             c_bi_by_nh_code,
    #             c_bi_ey_nh_code,
    #             c_bi_by_nh_year,
    #             c_bi_ey_nh_year
    #         FROM {0} WHERE c_personid in (select person_id from cbdb_kg.person)""".format(from_table_name))
    # value_placeholder = '%s, ' * (len(fields_mapping) - 1) + '%s'
    # fields_str = ''
    # for _, v in fields_mapping.iteritems():
    #     fields_str += v + ','
    # fields_str = fields_str[:-1]
    #
    # value_list = list()
    # for i in cursor.fetchall():
    #     value = list()
    #     for k, _ in fields_mapping.iteritems():
    #         value.append(i[k])
    #     value_list.append(tuple(value))
    #
    # insert_command = "insert  into {0} ({1}) values ({2})".format(to_table_name, fields_str, value_placeholder)
    #
    # cursor.executemany(insert_command, value_list)
    # conn.commit()
    # cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    # print 'migrate person_institution done!'

    print 'updating person_institution.......'
    # TODO 更新first_year_nianhao，last_year_nianhao
    update_commands = [
        "update cbdb_kg.person_to_institution set cbdb_kg.person_to_institution.first_year_nianhao=(select cbdb.nian_hao.c_nianhao_chn from cbdb.nian_hao where cbdb_kg.person_to_institution.first_year_nianhao=cbdb.nian_hao.c_nianhao_id)",
        "update cbdb_kg.person_to_institution set cbdb_kg.person_to_institution.last_year_nianhao=(select cbdb.nian_hao.c_nianhao_chn from cbdb.nian_hao where cbdb_kg.person_to_institution.last_year_nianhao=cbdb.nian_hao.c_nianhao_id)"
    ]

    # cursor.execute("ALTER TABLE cbdb_kg.place_to_place DROP PRIMARY KEY")  # 先移除主键
    for update_command in update_commands:
        try:
            cursor.execute(update_command)
        except:
            print update_command
            raise
    # cursor.execute("ALTER TABLE cbdb_kg.place_to_place ADD PRIMARY KEY(place_id, belongs_to_id)")
    conn.commit()
    print 'updating person_institution done!'


def migrate_office(conn, cursor):
    # type: (pymysql.cursors.DictCursor, pymysql.connections.Connection) -> None
    """
    迁移职位表
    :param conn:
    :param cursor:
    :return:
    """
    # from_table_name = 'cbdb.office_codes'
    # to_table_name = 'cbdb_kg.office'
    #
    # fields_mapping = OrderedDict()  # 记录两张表对应字段
    # fields_mapping['c_office_id'] = 'office_id'
    # fields_mapping['c_office_chn'] = 'office_title'
    # fields_mapping['c_office_tree_id'] = 'office_type'
    # fields_mapping['c_dy'] = 'dynasty'
    #
    # cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    # cursor.execute("""SELECT
    #             cbdb.office_codes.c_office_id as c_office_id,
    #             c_office_chn,
    #             cbdb.office_codes.c_office_id as c_office_tree_id,
    #             c_dy
    #         FROM {0}""".format(from_table_name))
    # value_placeholder = '%s, ' * (len(fields_mapping) - 1) + '%s'
    # fields_str = ''
    # for _, v in fields_mapping.iteritems():
    #     fields_str += v + ','
    # fields_str = fields_str[:-1]
    #
    # value_list = list()
    # for i in cursor.fetchall():
    #     value = list()
    #     for k, _ in fields_mapping.iteritems():
    #         value.append(i[k])
    #     value_list.append(tuple(value))
    #
    # insert_command = "insert  into {0} ({1}) values ({2})".format(to_table_name, fields_str, value_placeholder)
    #
    # cursor.executemany(insert_command, value_list)
    # conn.commit()
    # cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    # print 'migrate office done!'

    print 'updating office.......'
    # TODO 更新office_type，dynasty
    update_commands = [
        "update cbdb_kg.office set cbdb_kg.office.office_type=(SELECT group_concat(c_office_type_desc_chn separator ', ') FROM cbdb.office_code_type_rel, cbdb.office_type_tree where cbdb.office_code_type_rel.c_office_id=cbdb_kg.office.office_id and cbdb.office_code_type_rel.c_office_tree_id=cbdb.office_type_tree.c_office_type_node_id)",
        "update cbdb_kg.office set cbdb_kg.office.dynasty=(select cbdb.dynasties.c_dynasty_chn from cbdb.dynasties where cbdb_kg.office.dynasty=cbdb.dynasties.c_dy)"
    ]

    # cursor.execute("ALTER TABLE cbdb_kg.place_to_place DROP PRIMARY KEY")  # 先移除主键
    for update_command in update_commands:
        try:
            cursor.execute(update_command)
        except:
            print update_command
            raise
    # cursor.execute("ALTER TABLE cbdb_kg.place_to_place ADD PRIMARY KEY(place_id, belongs_to_id)")
    conn.commit()
    print 'updating office done!'


def migrate_posting(conn, cursor):
    # type: (pymysql.cursors.DictCursor, pymysql.connections.Connection) -> None
    """
    迁移任职表
    :param conn:
    :param cursor:
    :return:
    """
    # from_table_name1 = 'cbdb.posting_data'
    # from_table_name2 = 'cbdb.posted_to_office_data'
    # to_table_name = 'cbdb_kg.posting'
    #
    # fields_mapping = OrderedDict()  # 记录两张表对应字段
    # fields_mapping['c_personid'] = 'person_id'
    # fields_mapping['c_posting_id'] = 'posting_id'
    # fields_mapping['c_office_id'] = 'office_id'
    # fields_mapping['c_sequence'] = 'posting_sequence'
    # fields_mapping['c_firstyear'] = 'first_year'
    # fields_mapping['c_fy_month'] = 'first_year_month'
    # fields_mapping['c_fy_day'] = 'first_year_day'
    # fields_mapping['c_fy_nh_code'] = 'first_year_nianhao'
    # fields_mapping['c_fy_nh_year'] = 'first_year_nianhao_year'
    # fields_mapping['c_fy_day_gz'] = 'first_year_day_ganzhi'
    # fields_mapping['c_lastyear'] = 'last_year'
    # fields_mapping['c_ly_month'] = 'last_year_month'
    # fields_mapping['c_ly_day'] = 'last_year_day'
    # fields_mapping['c_ly_nh_code'] = 'last_year_nianhao'
    # fields_mapping['c_ly_nh_year'] = 'last_year_nianhao_year'
    # fields_mapping['c_ly_day_gz'] = 'last_year_day_ganzhi'
    # fields_mapping['c_dy'] = 'dynasty'
    #
    # cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    # cursor.execute("""SELECT
    #             cbdb.posting_data.c_personid as c_personid,
    #             cbdb.posting_data.c_posting_id as c_posting_id,
    #             c_office_id,
    #             c_sequence,
    #             c_firstyear,
    #             c_fy_month,
    #             c_fy_day,
    #             c_fy_nh_code,
    #             c_fy_nh_year,
    #             c_fy_day_gz,
    #             c_lastyear,
    #             c_ly_month,
    #             c_ly_day,
    #             c_ly_nh_code,
    #             c_ly_nh_year,
    #             c_ly_day_gz,
    #             c_dy
    #         FROM {0}, {1} WHERE cbdb.posting_data.c_personid in (select person_id from cbdb_kg.person) and {0}.c_posting_id={1}.c_posting_id""".format(from_table_name1, from_table_name2))
    # value_placeholder = '%s, ' * (len(fields_mapping) - 1) + '%s'
    # fields_str = ''
    # for _, v in fields_mapping.iteritems():
    #     fields_str += v + ','
    # fields_str = fields_str[:-1]
    #
    # value_list = list()
    # for i in cursor.fetchall():
    #     value = list()
    #     for k, _ in fields_mapping.iteritems():
    #         value.append(i[k])
    #     value_list.append(tuple(value))
    #
    # insert_command = "insert  into {0} ({1}) values ({2})".format(to_table_name, fields_str, value_placeholder)
    #
    # cursor.executemany(insert_command, value_list)
    # conn.commit()
    # cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    # print 'migrate posting done!'

    print 'updating posting.......'
    # TODO 更新first_year_nianhao, last_year_nianhao, first_year_day_ganzhi, last_year_day_ganzhi, dynasty
    update_commands = [
        "update cbdb_kg.posting set cbdb_kg.posting.first_year_nianhao=(select cbdb.nian_hao.c_nianhao_chn from cbdb.nian_hao where cbdb_kg.posting.first_year_nianhao=cbdb.nian_hao.c_nianhao_id)",
        "update cbdb_kg.posting set cbdb_kg.posting.last_year_nianhao=(select cbdb.nian_hao.c_nianhao_chn from cbdb.nian_hao where cbdb_kg.posting.last_year_nianhao=cbdb.nian_hao.c_nianhao_id)",
        "update cbdb_kg.posting set cbdb_kg.posting.first_year_day_ganzhi=(select cbdb.ganzhi_codes.c_ganzhi_chn from cbdb.ganzhi_codes where cbdb_kg.posting.first_year_day_ganzhi=cbdb.ganzhi_codes.c_ganzhi_code)",
        "update cbdb_kg.posting set cbdb_kg.posting.last_year_day_ganzhi=(select cbdb.ganzhi_codes.c_ganzhi_chn from cbdb.ganzhi_codes where cbdb_kg.posting.last_year_day_ganzhi=cbdb.ganzhi_codes.c_ganzhi_code)",
        "update cbdb_kg.posting set cbdb_kg.posting.dynasty=(select cbdb.dynasties.c_dynasty_chn from cbdb.dynasties where cbdb_kg.posting.dynasty=cbdb.dynasties.c_dy)"
    ]

    # cursor.execute("ALTER TABLE cbdb_kg.place_to_place DROP PRIMARY KEY")  # 先移除主键
    for update_command in update_commands:
        try:
            cursor.execute(update_command)
        except:
            print update_command
            raise
    # cursor.execute("ALTER TABLE cbdb_kg.place_to_place ADD PRIMARY KEY(place_id, belongs_to_id)")
    conn.commit()
    print 'updating posting done!'


def migrate_posted_to_place(conn, cursor):
    # type: (pymysql.cursors.DictCursor, pymysql.connections.Connection) -> None
    """
    迁移任命地点表
    :param conn:
    :param cursor:
    :return:
    """
    from_table_name = 'cbdb.posted_to_addr_data'
    to_table_name = 'cbdb_kg.posted_to_place'

    fields_mapping = OrderedDict()  # 记录两张表对应字段
    fields_mapping['c_addr_id'] = 'place_id'
    fields_mapping['c_posting_id'] = 'posting_id'

    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    cursor.execute("""SELECT
                c_addr_id,
                c_posting_id
            FROM {0} WHERE cbdb.posted_to_addr_data.c_posting_id in (select posting_id from cbdb_kg.posting) and cbdb.posted_to_addr_data.c_office_id in (select office_id from cbdb_kg.office)""".format(from_table_name))
    value_placeholder = '%s, ' * (len(fields_mapping) - 1) + '%s'
    fields_str = ''
    for _, v in fields_mapping.iteritems():
        fields_str += v + ','
    fields_str = fields_str[:-1]

    value_list = list()
    for i in cursor.fetchall():
        value = list()
        for k, _ in fields_mapping.iteritems():
            value.append(i[k])
        value_list.append(tuple(value))

    insert_command = "insert  into {0} ({1}) values ({2})".format(to_table_name, fields_str, value_placeholder)

    cursor.executemany(insert_command, value_list)
    conn.commit()
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    print 'migrate posted_to_place done!'

    print 'updating posted_to_place.......'
    # TODO 更新first_year_nianhao, last_year_nianhao, first_year_day_ganzhi, last_year_day_ganzhi, dynasty
    update_commands = [
        "update cbdb_kg.posted_to_place set cbdb_kg.posted_to_place.place_id=coalesce((select cbdb_kg.place.place_id from cbdb_kg.place where cbdb_kg.place.place_raw_id=cbdb_kg.posted_to_place.place_id limit 1), 1)"
    ]

    # cursor.execute("ALTER TABLE cbdb_kg.place_to_place DROP PRIMARY KEY")  # 先移除主键
    for update_command in update_commands:
        try:
            cursor.execute(update_command)
        except:
            print update_command
            raise
    # cursor.execute("ALTER TABLE cbdb_kg.place_to_place ADD PRIMARY KEY(place_id, belongs_to_id)")
    conn.commit()
    print 'updating posted_to_place done!'


def migrate_event(conn, cursor):
    # type: (pymysql.cursors.DictCursor, pymysql.connections.Connection) -> None
    """
    迁移事件表
    :param conn:
    :param cursor:
    :return:
    """
    from_table_name = 'cbdb.event_codes'
    to_table_name = 'cbdb_kg.event'

    fields_mapping = OrderedDict()  # 记录两张表对应字段
    fields_mapping['c_event_code'] = 'event_id'
    fields_mapping['c_event_name_chn'] = 'event_name'

    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    cursor.execute("""SELECT
                c_event_code,
                c_event_name_chn
            FROM {0}""".format(from_table_name))
    value_placeholder = '%s, ' * (len(fields_mapping) - 1) + '%s'
    fields_str = ''
    for _, v in fields_mapping.iteritems():
        fields_str += v + ','
    fields_str = fields_str[:-1]

    value_list = list()
    for i in cursor.fetchall():
        value = list()
        for k, _ in fields_mapping.iteritems():
            value.append(i[k])
        value_list.append(tuple(value))

    insert_command = "insert  into {0} ({1}) values ({2})".format(to_table_name, fields_str, value_placeholder)

    cursor.executemany(insert_command, value_list)
    conn.commit()
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    print 'migrate event done!'


def migrate_person_to_event(conn, cursor):
    # type: (pymysql.cursors.DictCursor, pymysql.connections.Connection) -> None
    """
    迁移人物事件表
    :param conn:
    :param cursor:
    :return:
    """
    from_table_name = 'cbdb.events_data'
    to_table_name = 'cbdb_kg.person_to_event'

    fields_mapping = OrderedDict()  # 记录两张表对应字段
    fields_mapping['c_personid'] = 'person_id'
    fields_mapping['c_event_code'] = 'event_id'
    fields_mapping['c_event_record_id'] = 'event_record_id'
    fields_mapping['c_sequence'] = 'event_sequence'
    fields_mapping['c_event'] = 'event_content'
    fields_mapping['c_year'] = 'event_year'
    fields_mapping['c_nh_code'] = 'event_nianhao'
    fields_mapping['c_nh_year'] = 'event_nianhao_year'
    fields_mapping['c_month'] = 'event_month'
    fields_mapping['c_day'] = 'event_day'
    fields_mapping['c_day_ganzhi'] = 'event_day_ganzhi'

    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    cursor.execute("""SELECT
                c_personid,
                coalesce(c_event_code, 0) as c_event_code,
                coalesce(c_event_record_id, 0) as c_event_record_id,
                c_sequence,
                c_event,
                c_year,
                c_nh_code,
                c_nh_year,
                c_month,
                c_day,
                c_day_ganzhi
            FROM {0} where not (isnull(c_event_code) and isnull(c_event_record_id))""".format(from_table_name))
    value_placeholder = '%s, ' * (len(fields_mapping) - 1) + '%s'
    fields_str = ''
    for _, v in fields_mapping.iteritems():
        fields_str += v + ','
    fields_str = fields_str[:-1]

    value_list = list()
    for i in cursor.fetchall():
        value = list()
        for k, _ in fields_mapping.iteritems():
            value.append(i[k])
        value_list.append(tuple(value))

    insert_command = "insert  into {0} ({1}) values ({2})".format(to_table_name, fields_str, value_placeholder)

    cursor.executemany(insert_command, value_list)
    conn.commit()
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    print 'migrate person_to_event done!'

    print 'updating person_to_event.......'
    # TODO 更新event_nianhao,event_day_ganzhi
    update_commands = [
        "update cbdb_kg.person_to_event set cbdb_kg.person_to_event.event_nianhao=(select cbdb.nian_hao.c_nianhao_chn from cbdb.nian_hao where cbdb_kg.person_to_event.event_nianhao=cbdb.nian_hao.c_nianhao_id)",
        "update cbdb_kg.person_to_event set cbdb_kg.person_to_event.event_day_ganzhi=(select cbdb.ganzhi_codes.c_ganzhi_chn from cbdb.ganzhi_codes where cbdb_kg.person_to_event.event_day_ganzhi=cbdb.ganzhi_codes.c_ganzhi_code)"
    ]

    # cursor.execute("ALTER TABLE cbdb_kg.place_to_place DROP PRIMARY KEY")  # 先移除主键
    for update_command in update_commands:
        try:
            cursor.execute(update_command)
        except:
            print update_command
            raise
    # cursor.execute("ALTER TABLE cbdb_kg.place_to_place ADD PRIMARY KEY(place_id, belongs_to_id)")
    conn.commit()
    print 'updating person_to_event done!'


def migrate_event_record_to_place(conn, cursor):
    # type: (pymysql.cursors.DictCursor, pymysql.connections.Connection) -> None
    """
    迁移人物事件地点表
    :param conn:
    :param cursor:
    :return:
    """
    from_table_name = 'cbdb.events_addr'
    to_table_name = 'cbdb_kg.event_record_to_place'

    fields_mapping = OrderedDict()  # 记录两张表对应字段
    fields_mapping['c_addr_id'] = 'place_id'
    fields_mapping['c_event_record_id'] = 'event_record_id'

    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    cursor.execute("""SELECT
                c_addr_id,
                c_event_record_id
            FROM {0}""".format(from_table_name))
    value_placeholder = '%s, ' * (len(fields_mapping) - 1) + '%s'
    fields_str = ''
    for _, v in fields_mapping.iteritems():
        fields_str += v + ','
    fields_str = fields_str[:-1]

    value_list = list()
    for i in cursor.fetchall():
        value = list()
        for k, _ in fields_mapping.iteritems():
            value.append(i[k])
        value_list.append(tuple(value))

    insert_command = "insert  into {0} ({1}) values ({2})".format(to_table_name, fields_str, value_placeholder)

    cursor.executemany(insert_command, value_list)
    conn.commit()
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    print 'migrate event_record_to_place done!'

    print 'updating event_record_to_place.......'
    # TODO 更新place_id
    update_commands = [
        "update cbdb_kg.event_record_to_place set cbdb_kg.event_record_to_place.place_id=coalesce((select cbdb_kg.place.place_id from cbdb_kg.place where cbdb_kg.place.place_raw_id=cbdb_kg.event_record_to_place.place_id limit 1), 1)",
    ]

    # cursor.execute("ALTER TABLE cbdb_kg.place_to_place DROP PRIMARY KEY")  # 先移除主键
    for update_command in update_commands:
        try:
            cursor.execute(update_command)
        except:
            print update_command
            raise
    # cursor.execute("ALTER TABLE cbdb_kg.place_to_place ADD PRIMARY KEY(place_id, belongs_to_id)")
    conn.commit()
    print 'updating event_record_to_place done!'


if __name__ == '__main__':
    # TODO 连接本地mysql的CBDB数据库
    db_conn = pymysql.connect(host="localhost", user="root", use_unicode=True, charset="utf8mb4",
                              cursorclass=pymysql.cursors.DictCursor)

    db_cursor = db_conn.cursor()

    # migrate_person(db_conn, db_cursor)

    # migrate_appellation(db_conn, db_cursor)

    # migrate_kinship(db_conn, db_cursor)

    # migrate_status(db_conn, db_cursor)

    # migrate_text(db_conn, db_cursor)

    # migrate_person_text(db_conn, db_cursor)

    # migrate_place(db_conn, db_cursor)

    # migrate_place_to_place(db_conn, db_cursor)

    # migrate_mode_of_entry(db_conn, db_cursor)

    # migrate_person_to_place(db_conn, db_cursor)

    # migrate_non_kinship_association(db_conn, db_cursor)

    # migrate_institution(db_conn, db_cursor)

    # migrate_person_institution(db_conn, db_cursor)

    # migrate_office(db_conn, db_cursor)

    # migrate_posting(db_conn, db_cursor)

    # migrate_posted_to_place(db_conn, db_cursor)

    # migrate_event(db_conn, db_cursor)

    # migrate_person_to_event(db_conn, db_cursor)

    # migrate_event_record_to_place(db_conn, db_cursor)

    db_conn.close()
