# -- coding:utf-8 --
#usage: process the get request of the app
from django.http import HttpResponse
from django.utils import simplejson
from django.forms.models import model_to_dict

from django.utils.http import urlquote
import urllib

import os, json
#import sys
#sys.path.append('./')
import SearchMysql_v3 as searchmysql
#from search import SearchMysql_v3 as searchmysql
import IndexMysql
#from search import IndexMysql
from models import MovieItems, ShortComments, MovieAwards
#from search.models import MovieItems
'''
interface for querying from app
use standard get request
return json
'''

module_dir = os.path.dirname(__file__)  # get current directory

'''
this will get none which means there's no jvm in the memory,  that can also be 
proved cause you'll never initJvm twice
'''
last_get_env = searchmysql.getVMEnv()

'''
no jvm in memory, so you can initJvm here 
'''
env = searchmysql.initJvm()

new_get_env = searchmysql.getVMEnv()

retobj = {}

DEBUG = False
if DEBUG:
    retobj['last_get_env'] = str(last_get_env)
    retobj['new_get_env'] = str(new_get_env)
    retobj['initResult'] = str(env)
    retobj['theSameorNot'] = (new_get_env is env)


def index(request):
    return HttpResponse('This is a test html')

def search(request):
    #try:
    #return HttpResponse(request)
    if request.method == 'GET':
        # extract the specified get parameters
        #command = urlquote(request.get['command']).decode('utf8')
        import urlparse
        #query_str is 'command=%E8%AF%9D&start=0&count=10'
        # The blow expression is wrong! request has no 'get' function, but has 'GET' as a dict, use request.GET['field_name']
        #query_str = request.get('QUERY_STRING', '')
        #args = urlparse.parse_qs(query_str)
        command = urllib.unquote(request.GET['command'])
        start = int(urllib.unquote(request.GET['start']))#start 规定从0开始
        count = int(urllib.unquote(request.GET['count']))

        #get current jvm
        VMEnv = searchmysql.getVMEnv()
        if VMEnv:
            retobj['debug'] = "attach to jvm"
            res = VMEnv.attachCurrentThread()
            retobj['attachResult'] = res
        else:
            retobj['debug'] = "new jvm"
            searchmysql.initJvm()



        # here goes the pylucene routines, fetch results and construct json
        # we can construct a standard python dictionary and then convert it to json
        # examples for returning json are demonstrated blow

        awrapper = IndexMysql.CreateAWrapper()
        searcher,analyzer = searchmysql.config()
        retlist = searchmysql.run(command,searcher,awrapper, use_custom_parser=True)

        anscount = len(retlist)



        if start+count < anscount:
            retobj['count'] = count
            retobj['start'] = start
            retobj['total'] = anscount
            retobj['subjects'] = retlist[start:start+count]
        elif start < anscount:
            retobj['count'] = anscount-start
            retobj['start'] = start
            retobj['total'] = anscount
            retobj['subjects'] = retlist[start:anscount]
        else:
            retobj['count'] = '老纪你看清楚，总共才'+str(anscount)+'个！'

        retjson = retobj
        #retjson = simplejson.dumps(retobj,ensure_ascii=false)  #all is unicode withoout ensure...
        #retjson = eval(retjson) #将原本是字符串的json的引号去掉 比如'[1,2,3]'-->[1,2,3],将字符串变成变量
        #retjson = retlist[0:5] #right encode utf8 list

        '''
        emdjson = {}
        emdjson['code'] = 0
        emdjson['message'] = 'hello little dict'
        emdjson['goal'] = u'测试字典嵌套的json输出'

        retjson['emdjson'] = emdjson
        '''

        return HttpResponse(simplejson.dumps(retjson, ensure_ascii = False), content_type="application/json")
    '''
    except exception, e:
            errjson = {}
            errjson['retcode'] = 1
            errjson['message'] = 'sorry, server exception occurred!'
            errjson['exceptioncode'] = e.args[0]
            #errjson['exceptionmessage'] = e.args[1]
            return httpresponse(simplejson.dumps(errjson, ensure_ascii = false), content_type="application/json")
    '''

def search_by_custom_parser(request):
    #try:
    #return HttpResponse("test custom parser")
    if request.method == 'GET':
        # extract the specified get parameters
        #command = urlquote(request.get['command']).decode('utf8')
        import urlparse
        #query_str is 'command=%E8%AF%9D&start=0&count=10'
        # The blow expression is wrong! request has no 'get' function, but has 'GET' as a dict, use request.GET['field_name']
        #query_str = request.get('QUERY_STRING', '')
        #args = urlparse.parse_qs(query_str)
        command = urllib.unquote(request.GET['command'])
        start = int(urllib.unquote(request.GET['start']))#start 规定从0开始
        count = int(urllib.unquote(request.GET['count']))


        # here goes the pylucene routines, fetch results and construct json
        # we can construct a standard python dictionary and then convert it to json
        # examples for returning json are demonstrated blow

        awrapper = IndexMysql.CreateAWrapper()
        searcher,analyzer = searchmysql.config()
        retlist = searchmysql.run(command, searcher, awrapper, use_custom_parser=True)

        anscount = len(retlist)

        retobj = {}

        if start+count < anscount:
            retobj['count'] = count
            retobj['start'] = start
            retobj['total'] = anscount
            retobj['subjects'] = retlist[start:start+count]
        elif start < anscount:
            retobj['count'] = anscount-start
            retobj['start'] = start
            retobj['total'] = anscount
            retobj['subjects'] = retlist[start:anscount]
        else:
            retobj['count'] = '老纪你看清楚，总共才'+str(anscount)+'个！'

        retjson = retobj
        #retjson = simplejson.dumps(retobj,ensure_ascii=false)  #all is unicode withoout ensure...
        #retjson = eval(retjson) #将原本是字符串的json的引号去掉 比如'[1,2,3]'-->[1,2,3],将字符串变成变量
        #retjson = retlist[0:5] #right encode utf8 list

        '''
        emdjson = {}
        emdjson['code'] = 0
        emdjson['message'] = 'hello little dict'
        emdjson['goal'] = u'测试字典嵌套的json输出'

        retjson['emdjson'] = emdjson
        '''

        return HttpResponse(simplejson.dumps(retjson, ensure_ascii = False), content_type="application/json")
    '''
    except exception, e:
            errjson = {}
            errjson['retcode'] = 1
            errjson['message'] = 'sorry, server exception occurred!'
            errjson['exceptioncode'] = e.args[0]
            #errjson['exceptionmessage'] = e.args[1]
            return httpresponse(simplejson.dumps(errjson, ensure_ascii = false), content_type="application/json")
    '''

def detail(request, subject_id):
    '''
        根据movie_id，查询电影的detail信息，json形式返回
    '''
    try:
        subject_id = int(subject_id)
        movie_items = list(MovieItems.objects.filter(subject_id=subject_id))
        if not movie_items:
            return HttpResponse("{'error': 'can not find this item'}")
        movie_item = movie_items[0]
        ret = model_to_dict(movie_item)
        comments = get_comments_by_id(subject_id)
        awards = get_awards_by_id(subject_id)
        recommended_movies = get_recommended_movies(ret['others_like'])
        ret['comments'] = comments
        ret['awards'] = awards
        ret['others_like'] = recommended_movies
        ret_json = simplejson.dumps(ret, ensure_ascii = False)
        return HttpResponse(ret_json, content_type="application/json")
    except Exception as e:
        return HttpResponse("发生异常: %s，老纪你在详情页捕获一下" % e, content_type="application/json")

def get_comments_by_id(subject_id, retN=20):
    try:
        comments = list(ShortComments.objects.filter(subject_id=subject_id))
        comments = [model_to_dict(c) for c in comments]
        comments = sorted(comments, key=lambda d: d['comment_date'], reverse=True)
        return comments[:retN]
    except Exception as e:
        return []

def get_awards_by_id(subject_id):
    try:
        awards = list(MovieAwards.objects.filter(subject_id=subject_id))
        awards = [model_to_dict(a) for a in awards]
        awards = awards[0] if awards else []
        if awards:
            awards['award_items'] = json.loads(awards['award_items'])
        #for k, v in awards.items():
        #    awards[k] = v.encode('utf8')
        return awards
    except Exception as e:
        return []

def get_recommended_movies(others_like_movies):
    if not others_like_movies:
        return []
    movies = others_like_movies.split(u'￥')
    movies = [m.split('<>') for m in movies]
    ids = [m[0] for m in movies]
    id2urls = dict(MovieItems.objects.filter(subject_id__in=ids).values_list('subject_id', 'image_small'))
    id2names = {m[0]: m[1] for m in movies}
    recommended_movies = []
    for id_, name in id2names.items():
        item = {}
        url = id2urls.get(id_, '')
        item['subject_id'] = id_
        item['name'] = name
        item['image_url'] = url
        recommended_movies.append(item)
    return recommended_movies

def get_navigation_list(request):
    try:
        if request.method == 'GET':
            type_ = int(urllib.unquote(request.GET['type']))#0表示引导list, 1表示九宫格需要的热门词汇
            if type_ == 0:
                navi_file = os.path.join(module_dir, 'data/navi_list.txt')
            elif type_ == 1:
                navi_file = os.path.join(module_dir, 'data/navi_blocks.txt')

            lines = open(navi_file, 'r').readlines()
            sentences = [l.strip().decode('utf8') for l in lines if l.strip()]
            msg = u'引导list' if type_ == 0 else u'九宫格'
            res = {'data': sentences, 'count': len(sentences), 'msg': msg}
            return HttpResponse(simplejson.dumps(res, ensure_ascii = False), content_type="application/json")
    except Exception as e:
        return HttpResponse("发生异常: %s，老纪你自己解决" % e, content_type="application/json")

