#coding=utf8

'''
    这个模块对用户输入的词进行解析，生成适合我们的query形式
'''
import os, sys
sys.path.append('../')

from ltp_service import ltpservice

module_dir = os.path.dirname(__file__)  # get current directory

#(field, weight)
person_fields_weight = [('directors', '10.0'),
                        ('casts', '5.0'),
                        #('writers', '1.0')
                        ]
non_person_fields_weight = [('title', '10.0'),
                            ('original_title', '10.0'),
                            ('aka', '7.0'),
                            ('countries', '0.5'),
                            #('user_tags', '1.0'),
                            ('summary', '5.0')
                            ]

class Parser:

    def __init__(self):
        self.load_film_terms()
        self.ltp_client = ltpservice.LTPService("%s:%s" % ('zhaoh@cslt.riit.tsinghua.edu.cn', '6Ts8ZDJK'))

    def load_film_terms(self):
        '''导入离线生成的terms

        导入从数据库成生成全部的人名和非人名的术语集合，用来判断用户的术语所属基本类型

        '''
        fields_terms_path = os.path.join(module_dir, 'fields_terms.txt')
        lines = open(fields_terms_path, 'r').readlines()
        terms = [tuple(l.strip().split('<￥>')) for l in lines if l]
        person_terms_types = [r[0] for r in person_fields_weight]
        non_person_terms_types = [r[0] for r in non_person_fields_weight]

        self.person_terms = {r[0].decode('utf8'): r[1] for r in terms if r[1] in person_terms_types}
        self.non_person_terms = {r[0].decode('utf8'): r[1] for r in terms if r[1] in non_person_terms_types}

    def parse(self, raw_str):
        terms = raw_str.split()
        query = ''
        for term in terms:
            query += self.parse_term(term)
        return query

    def parse_term(self, term):
        ''' 解析单个term

        基于person_terms和non_person_terms判断该term的基本情况，然后生成不同类型的query_str

        '''

        def generate_query_by_fields(term, field_info):
            lines = ['%s:%s^%s' % (r[0], term, r[1]) for r in field_info]
            #lines = ['%s:%s' % (r[0], term) for r in field_info]
            return ' '.join(lines)


        if term in self.person_terms and term in self.non_person_terms:
            query_str = generate_query_by_fields(term, person_fields_weight + non_person_fields_weight)
        elif term in self.person_terms:
            query_str = generate_query_by_fields(term, person_fields_weight)
        elif term in self.non_person_terms:
            query_str = generate_query_by_fields(term, non_person_fields_weight)
        else:
            query_str = generate_query_by_fields(term, person_fields_weight + non_person_fields_weight)
        return query_str

    def test_ltp(self, raw_str):
        result = self.ltp_client.analysis(raw_str, ltpservice.LTPOption.PARSER)
        print result.tostring()

def test_parser():
    parser = Parser()
    #term = u'张艺谋 章子怡'
    #print term in parser.person_terms
    parser.test_ltp('很多人觉得剧情很矫情')

if __name__ == '__main__':
    test_parser()
