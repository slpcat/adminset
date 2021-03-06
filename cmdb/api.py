#! /usr/bin/env python
# -*- coding: utf-8 -*-
# 2017.3 update by guohongze@126.com
from django.http import HttpResponse
from models import Host, HostGroup, ASSET_TYPE, ASSET_STATUS
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.views.decorators.csrf import csrf_exempt
from config.views import get_dir
try:
    import json
except ImportError, e:
    import simplejson as json


def token_verify():

    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            iToken = get_dir('token')
            if request.POST:
                pToken = request.POST.get('token')
                if iToken == pToken:
                    return view_func(request, *args, **kwargs)
                else:
                    message = "forbidden your token error!!"
                    print message
                    return HttpResponse(status=403)
            if request.GET:
                pToken = request.GET['token']
                if iToken == pToken:
                    return view_func(request, *args, **kwargs)
                else:
                    message = "forbidden your token error!!"
                    print message
                    return HttpResponse(status=403)
            return HttpResponse(status=403)

        return _wrapped_view

    return decorator


def str2gb(args):
    """
    :参数 args:
    :返回: GB2312编码
    """
    return str(args).encode('gb2312')


def get_object(model, **kwargs):
    """
    use this function for query
    使用改封装函数查询数据库
    """
    for value in kwargs.values():
        if not value:
            return None

    the_object = model.objects.filter(**kwargs)
    if len(the_object) == 1:
        the_object = the_object[0]
    else:
        the_object = None
    return the_object


def page_list_return(total, current=1):
    """
    page
    分页，返回本次分页的最小页数到最大页数列表
    """
    min_page = current - 2 if current - 4 > 0 else 1
    max_page = min_page + 4 if min_page + 4 < total else total

    return range(min_page, max_page + 1)


def pages(post_objects, request):
    """
    page public function , return page's object tuple
    分页公用函数，返回分页的对象元组
    """
    paginator = Paginator(post_objects, 65535)
    try:
        current_page = int(request.GET.get('page', '1'))
    except ValueError:
        current_page = 1

    page_range = page_list_return(len(paginator.page_range), current_page)

    try:
        page_objects = paginator.page(current_page)
    except (EmptyPage, InvalidPage):
        page_objects = paginator.page(paginator.num_pages)

    if current_page >= 5:
        show_first = 1
    else:
        show_first = 0

    if current_page <= (len(paginator.page_range) - 3):
        show_end = 1
    else:
        show_end = 0

    # 所有对象， 分页器， 本页对象， 所有页码， 本页页码，是否显示第一页，是否显示最后一页
    return post_objects, paginator, page_objects, page_range, current_page, show_first, show_end


@csrf_exempt
@token_verify()
def collect(request):
    req = request
    if req.POST:
        vendor = req.POST.get('vendor')
        group = req.POST.get('group')
        disk = req.POST.get('disk')
        cpu_model = req.POST.get('cpu_model')
        cpu_num = req.POST.get('cpu_num')
        memory = req.POST.get('memory')
        sn = req.POST.get('sn')
        osver = req.POST.get('osver')
        hostname = req.POST.get('hostname')
        ip = req.POST.get('ip')
        asset_type = ""
        status = ""
        try:
            host = Host.objects.get(hostname=hostname)
        except:
            host = Host()
        # if req.POST.get('identity'):
        #     identity = req.POST.get('identity')
        #     try:
        #         host = Host.objects.get(identity=identity)
        #     except:
        #         host = Host()
        host.hostname = hostname
        #host.group = group
        host.cpu_num = int(cpu_num)
        host.cpu_model = cpu_model
        host.memory = int(memory)
        host.sn = sn
        host.disk = disk
        host.os = osver
        host.vendor = vendor
        host.ip = ip
        host.asset_type = asset_type
        host.status = status
        host.save()
        return HttpResponse("post data successfully!")
    else:
        return HttpResponse("no any post data!")


@token_verify()
def get_host(request):
    try:
        hostname = request.GET['name']
    except:
        return HttpResponse('you have no data')
    try:
        host = Host.objects.get(hostname=hostname)
    except:
        return HttpResponse('no data,please check your hostname')
    data = {'hostname': host.hostname, 'ip': host.ip}
    return HttpResponse(json.dumps({'status': 0, 'message': 'ok', 'data': data}))


@token_verify()
def get_group(request):
    if request.GET:
        d = []
        try:
            group_name = request.GET['name']
        except:
            return HttpResponse('your parameter is error')
        if group_name == 'all':
            host_groups = HostGroup.objects.all()
            for hg in host_groups:
                ret_hg = {'host_group': hg.name, 'members': []}
                members = Host.objects.filter(group__name=hg)
                for h in members:
                    ret_h = {'hostname': h.hostname, 'ipaddr': h.ip}
                    ret_hg['members'].append(ret_h)
                d.append(ret_hg)
            return HttpResponse(json.dumps(d))
        else:
            ret_hg = {'host_group': group_name, 'members': []}
            members = Host.objects.filter(group__name=group_name)
            for h in members:
                ret_h = {'hostname': h.hostname, 'ipaddr': h.ip}
                ret_hg['members'].append(ret_h)
            d.append(ret_hg)
            return HttpResponse(json.dumps(d))
    return HttpResponse(status=403)