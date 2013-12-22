#coding=utf8

'''
    这个模块对用户输入的词进行解析，生成适合我们的query形式
    默认生成directors，casts，title三个域的search。
    剩下的，击中了某个域，就对应增加那个域，并按照预定的权重生成query
    国外中的人名有中文“·”，所以需要将这个拆分开来
'''
import os, sys
sys.path.append('../')

from ltp_service import ltpservice

from tools.xml_processor import parse_XML

module_dir = os.path.dirname(__file__)  # get current directory

#(field, weight)
#每个query term默认都有这几个search field，以及权重
basic_fields_weight = {'directors': '10.0',
                       'casts': '10.0',
                       'title': '10.0',
                       #'summary': '2.0'
                       }
#一旦检查到该term也有custom_fields中的type，需要增加该域的搜索
custom_fields_weight = {'original_title': '10.0',
                        'aka': '10.0',
                        'countries': '15.0',
                        'user_tags': '15.0',
                        'year': '20.0',
                        }

def unicode_to_str(raw_str):
    if isinstance(raw_str, str):
        return raw_str
    elif isinstance(raw_str, unicode):
        return raw_str.encode('utf8')

class Parser:

    def __init__(self):
        self.load_film_terms()
        self.ltp_client = ltpservice.LTPService("%s:%s" % ('zhaoh@cslt.riit.tsinghua.edu.cn', '6Ts8ZDJK'))

    def load_film_terms(self):
        '''导入离线生成的terms, 用来判断term的基本从属情况

        导入从数据库成生成全部术语集合，用来判断用户的术语所属基本类型
        生成一个子典型数据，key为term，value为list，保存该term从属的全部类型（可能人名会出现在导演，演员，title，user_tags中）

        '''
        fields_terms_path = os.path.join(module_dir, 'fields_terms.txt')
        lines = open(fields_terms_path, 'r').readlines()
        terms = [tuple(l.strip().split('<￥>')) for l in lines if l]
        self.term_types = {}
        for term_str, type_ in terms:
            #国外的中文译名中存在·，需要split之后，以单个人名来搜索
            terms = term_str.split('·')
            for term in terms:
                self.term_types.setdefault(term, []).append(type_)



    def parse(self, raw_str):
        terms = raw_str.split()
        query = ''
        for term in terms:
            query += self.parse_term(term)
        return query

    def parse_term(self, term):
        ''' 解析单个term

            每个term默认输入title, casts, directors三个域，其他类型一旦击中，都需要增加该域，以及预设的权重
        '''

        def generate_query_by_fields(term, field_info):
            lines = ['%s:%s^%s ' % (f, term, w) for f, w in field_info.items()]
            #lines = ['%s:%s' % (r[0], term) for r in field_info]
            return ''.join(lines)

        try:
            query_str = generate_query_by_fields(term, basic_fields_weight)
            if term in self.term_types:
                types = self.term_types[term]
                custom_types = [t for t in types if t not in basic_fields_weight.keys()]
                if custom_types:
                    need_custom_fields = {ct: custom_fields_weight.get(ct, '1.0') for ct in custom_types}
                    query_str += generate_query_by_fields(term, need_custom_fields)

            else:
                #这个时候很有可能是一句话，就引入ltp进行分词
                #import pdb;pdb.set_trace()
                #import time
                #start = time.time()
                ltp_res = self.ltp_client.analysis(unicode_to_str(term), ltpservice.LTPOption.PARSER)
                #print ltp_res.tostring()
                adjs, persons = parse_XML(ltp_res.tostring(), 1)#直接取出形容词即可
                print persons
                #能找出形容词则生成形容词域，否则直接返回term
                #print 'get adjs cost %.2fs' % (time.time() - start)
                if not adjs and not persons:
                    return query_str
                else:
                    query_str = u''
                    if adjs:
                        query_str += ''.join(['adjs:%s ' % a for a in adjs])
                    if persons:
                        #for person in persons:
                        #    types = self.term_types.get(person, [])
                        #    person_fields = 
                        query_str += ''.join(['direcors:%s^10.0 casts:%s^10.0 ' % (p, p) for p in persons])

            return query_str
        except Exception as e:
            print e
            return term

    def test_ltp(self, raw_str):
        result = self.ltp_client.analysis(raw_str, ltpservice.LTPOption.PARSER)
        print result.tostring()

def test_parser(raw_str):
    parser = Parser()
    #term = u'张艺谋 章子怡'
    #print term in parser.person_terms
    #parser.test_ltp('很多人觉得剧情很矫情')
    print parser.parse(raw_str)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        raw_str = sys.argv[1]
    else:
        raw_str = u'我想看快乐的电影'
    test_parser(raw_str)
