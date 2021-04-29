# 系统维护:用户管理、角色管理、功能管理
from django.db import reset_queries
from django.shortcuts import render
from django.http import HttpResponseRedirect, Http404, HttpResponse, JsonResponse

from ..tasks import *
from .basic_views import getpagefuns
from .public_func import *
from django.contrib.auth.decorators import login_required


######################
# 用户管理
######################
@login_required
def organization(request, funid):
    allgroup = Group.objects.exclude(state="9").values("id", "name")

    return render(request, 'organization.html', {
        'username': request.user.userinfo.fullname,
        "pagefuns": getpagefuns(funid, request=request),
        "allgroup": allgroup
    })



@login_required
def get_org_tree(request):
    status = 1
    info = ""
    data = []
    select_id = request.POST.get("id", "")
    allgroup = Group.objects.exclude(state="9")
    try:
        rootnodes = UserInfo.objects.order_by("sort").exclude(state="9").filter(pnode=None, type="org")
        if len(rootnodes) > 0:
            for rootnode in rootnodes:
                root = {}
                root["text"] = rootnode.fullname
                root["id"] = rootnode.id
                root["type"] = "org"
                myallgroup = []
                for group in allgroup:
                    myallgroup.append({"groupname": group.name, "id": group.id})
                root["data"] = {
                    "remark": rootnode.remark, 
                    "pname": "无", 
                    "myallgroup": myallgroup,
                    "name": rootnode.fullname,
                }
                try:
                    if int(select_id) == rootnode.id:
                        root["state"] = {"opened": True, "selected": True}
                    else:
                        root["state"] = {"opened": True}
                except:
                    root["state"] = {"opened": True}
                root["children"] = get_org_node(rootnode, select_id, allgroup)
                data.append(root)
    except Exception as e:
        status = 0
        info = "获取流程树失败。"

    return JsonResponse({
        "status": status,
        "data": data,
        "info": info
    })


@login_required
def get_org_detail(request):
    status = 1
    info = ""
    data = {}

    user_id = request.POST.get("id", "")
    allgroup = Group.objects.exclude(state="9")
    try:
        cur_user = UserInfo.objects.get(id=int(user_id))
    except Exception as e:
        pass
    else:
        if cur_user.type == "org":
            myallgroup = []
            for group in allgroup:
                myallgroup.append({"groupname": group.name, "id": group.id})
            data = {
                "pname": cur_user.pnode.fullname if cur_user.pnode else "",
                "remark": cur_user.remark, 
                "myallgroup": myallgroup,
                "orgname": cur_user.fullname,
            }
        if cur_user.type == "user":
            noselectgroup = []
            selectgroup = []
            allselectgroup = cur_user.group.all()
            for group in allgroup:
                if group in allselectgroup:
                    selectgroup.append({"groupname": group.name, "id": group.id})
                else:
                    noselectgroup.append({"groupname": group.name, "id": group.id})
            data = {
                "pname": cur_user.pnode.fullname if cur_user.pnode else "",
                "username": cur_user.user.username, 
                "fullname": cur_user.fullname,
                "phone": cur_user.phone, 
                "email": cur_user.user.email, 
                "noselectgroup": noselectgroup,
                "selectgroup": selectgroup
            }

    return JsonResponse({
        "status": status,
        "data": data,
        "info": info
    })


@login_required
def org_user_save(request):
    status = 1
    info = "保存成功。"

    id = request.POST.get('id')
    pid = request.POST.get('pid')
    mytype = request.POST.get('mytype')
    allgroup = Group.objects.exclude(state="9")

    try:
        id = int(id)
    except:
        pass
    try:
        pid = int(pid)
    except:
        pass
    if mytype == "usersave":
        grouplist = request.POST.getlist('source')
        noselectgroup = []
        selectgroup = []
        for group in allgroup:
            if str(group.id) in grouplist:
                selectgroup.append({"groupname": group.name, "id": group.id})
            else:
                noselectgroup.append({"groupname": group.name, "id": group.id})
        username = request.POST.get('myusername', '')
        fullname = request.POST.get('fullname', '')
        phone = request.POST.get('phone', '')
        email = request.POST.get('email', '')
        password = request.POST.get('password', '')
        if id == 0:
            alluser = User.objects.filter(username=username).exclude(userinfo__state="9")
            if username.strip() == '':
                info = '用户名不能为空。'
                status = 0
            else:
                if password.strip() == '':
                    info = '密码不能为空。'
                    status = 0
                else:
                    if fullname.strip() == '':
                        info = '姓名不能为空。'
                        status = 0
                    else:
                        if alluser.exists():
                            info = '用户名:{0}已存在。'.format(username)
                            status = 0
                        else:
                            try:
                                newuser = User()
                                newuser.username = username
                                newuser.set_password(password)
                                newuser.email = email
                                newuser.save()
                                # 用户扩展信息 profile
                                profile = UserInfo()  # e*************************
                                profile.user_id = newuser.id
                                profile.phone = phone
                                profile.fullname = fullname
                                try:
                                    porg = UserInfo.objects.get(id=pid)
                                except:
                                    raise Http404()
                                profile.pnode = porg
                                profile.type = "user"
                                sort = 1
                                try:
                                    maxorg = UserInfo.objects.filter(pnode=porg).latest('sort')
                                    sort = maxorg.sort + 1
                                except:
                                    pass
                                profile.sort = sort
                                profile.save()
                                for group in grouplist:
                                    try:
                                        group = int(group)
                                        mygroup = allgroup.get(id=group)
                                        profile.group.add(mygroup)
                                    except Exception:
                                        raise Http404()
                                id = profile.id

                                save_syslog(request.user.id, 'new', '用户{0}'.format(fullname))

                            except Exception as e:
                                info = "保存用户失败。"
                                status = 0
        else:
            exalluser = User.objects.filter(username=username).exclude(userinfo__state="9").exclude(userinfo__id=id)
            if username.strip() == '':
                info = '用户名不能为空。'
                status = 0
            else:
                if fullname.strip() == '':
                    info = '姓名不能为空。'
                    status = 0
                else:
                    if exalluser.exists():
                    # if (len(exalluser) > 0 and exalluser[0].userinfo.id != id):
                        info = '用户名:{0}已存在。'.format(username)
                        status = 0
                    else:
                        try:
                            alluserinfo = UserInfo.objects.get(id=id)
                            alluser = alluserinfo.user
                            alluser.email = email
                            alluser.save()
                            # 用户扩展信息 profile
                            alluserinfo.phone = phone
                            alluserinfo.fullname = fullname
                            alluserinfo.save()
                            alluserinfo.group.clear()
                            for group in grouplist:
                                try:
                                    group = int(group)
                                    mygroup = allgroup.get(id=group)
                                    alluserinfo.group.add(mygroup)
                                except ValueError:
                                    raise Http404()

                            save_syslog(request.user.id, 'edit', '用户{0}'.format(fullname))

                        except:
                            info = '保存失败。'
                            status = 0

    if mytype == "orgsave":
        orgname = request.POST.get('orgname', '')
        remark = request.POST.get('remark', '')
        if id == 0:
            try:
                porg = UserInfo.objects.get(id=pid)
            except:
                raise Http404()
            allorg = UserInfo.objects.exclude(state="9").filter(fullname=orgname, pnode=porg)
            if orgname.strip() == '':
                info = '组织名称不能为空。'
                status = 0
            else:
                if allorg.exists():
                    info = '{0}已存在。'.format(orgname)
                    status = 0
                else:
                    try:
                        profile = UserInfo()  # e*************************
                        profile.fullname = orgname
                        profile.pnode = porg
                        profile.remark = remark
                        profile.type = "org"
                        sort = 1
                        try:
                            maxorg = UserInfo.objects.filter(pnode=porg).latest('sort')
                            sort = maxorg.sort + 1
                        except:
                            pass
                        profile.sort = sort
                        profile.save()
                        id = profile.id

                        save_syslog(request.user.id, 'new', '组织{0}'.format(orgname))

                    except ValueError:
                        raise Http404()
        else:
            try:
                porg = UserInfo.objects.get(id=pid)
            except:
                raise Http404()
            exalluser = UserInfo.objects.filter(fullname=orgname, pnode=porg).exclude(state="9")
            if orgname.strip() == '':
                info = '组织名称不能为空。'
                status = 0
            else:
                if (len(exalluser) > 0 and exalluser[0].id != id):
                    info = '{0}已存在。'.format(orgname)
                    status = 0
                else:
                    try:
                        alluserinfo = UserInfo.objects.get(id=id)
                        alluserinfo.fullname = orgname
                        alluserinfo.remark = remark
                        alluserinfo.save()

                        save_syslog(request.user.id, 'edit', '组织{0}'.format(orgname))

                    except:
                        info = '保存失败。'
                        status = 0

    return JsonResponse({
        "status": status,
        "info": info,
        "data": id
    })


@login_required
def orgdel(request):
    if 'id' in request.POST:
        id = request.POST.get('id', '')
        try:
            id = int(id)
        except:
            raise Http404()
        userinfo = UserInfo.objects.get(id=id)
        sort = userinfo.sort
        userinfo.state = "9"
        userinfo.sort = 9999
        userinfo.save()

        if userinfo.type == "user":
            user = userinfo.user
            user.is_active = 0
            user.save()

        userinfos = UserInfo.objects.filter(pnode=userinfo.pnode).filter(sort__gt=sort).exclude(state="9")
        if (len(userinfos) > 0):
            for myuserinfo in userinfos:
                try:
                    myuserinfo.sort = myuserinfo.sort - 1
                    myuserinfo.save()
                except:
                    pass
        content = ''
        if userinfo.type == 'org':
            content = '组织{0}'.format(userinfo.fullname)
        if userinfo.type == 'user':
            content = '用户{0}'.format(userinfo.fullname)
        save_syslog(request.user.id, 'delete', content)

        return HttpResponse(1)
    else:
        return HttpResponse(0)


@login_required
def orgmove(request):
    if 'id' in request.POST:
        id = request.POST.get('id', '')
        parent = request.POST.get('parent', '')
        old_parent = request.POST.get('old_parent', '')
        position = request.POST.get('position', '')
        old_position = request.POST.get('old_position', '')
        try:
            id = int(id)
        except:
            raise Http404()
        try:
            parent = int(parent)
        except:
            raise Http404()
        try:
            position = int(position)
        except:
            raise Http404()
        try:
            parent = int(parent)
        except:
            raise Http404()
        try:
            old_position = int(old_position)
        except:
            raise Http404()
        oldpuserinfo = UserInfo.objects.get(id=old_parent)
        oldsort = old_position + 1
        olduserinfos = UserInfo.objects.filter(pnode=oldpuserinfo).filter(sort__gt=oldsort)

        puserinfo = UserInfo.objects.get(id=parent)
        sort = position + 1
        userinfos = UserInfo.objects.filter(pnode=puserinfo).filter(sort__gte=sort).exclude(id=id).exclude(
            state="9")

        myuserinfo = UserInfo.objects.get(id=id)
        if puserinfo.type == "user":
            return HttpResponse("类型")
        else:
            usersame = UserInfo.objects.filter(pnode=puserinfo).filter(fullname=myuserinfo.fullname).exclude(
                id=id).exclude(state="9")
            if (len(usersame) > 0):
                return HttpResponse("重名")
            else:
                if (len(olduserinfos) > 0):
                    for olduserinfo in olduserinfos:
                        try:
                            olduserinfo.sort = olduserinfo.sort - 1
                            olduserinfo.save()
                        except:
                            pass
                if (len(userinfos) > 0):
                    for userinfo in userinfos:
                        try:
                            userinfo.sort = userinfo.sort + 1
                            userinfo.save()
                        except:
                            pass

                try:
                    myuserinfo.pnode = puserinfo
                    myuserinfo.sort = sort
                    myuserinfo.save()

                    save_syslog(request.user.id, 'edit', '{0}节点位置'.format(myuserinfo.fullname))

                except:
                    pass
                if parent != old_parent:
                    return HttpResponse(puserinfo.fullname + "^" + str(puserinfo.id))
                else:
                    return HttpResponse("0")


@login_required
def orgpassword(request):
    if 'id' in request.POST:
        id = request.POST.get('id')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        try:
            offset = int(id)
            userinfo = UserInfo.objects.get(id=id)
            user = userinfo.user
            user.set_password(password1)
            user.save()

            save_syslog(request.user.id, 'edit', '{0}密码'.format(userinfo.fullname))

            return HttpResponse("1")
        except:
            HttpResponse('修改密码失败，请于管理员联系。')


######################
# 角色管理
######################
@login_required
def group(request, funid):
    try:
        allgroup = Group.objects.all().exclude(state="9")

        return render(request, 'group.html',
                      {'username': request.user.userinfo.fullname,
                       "allgroup": allgroup, "pagefuns": getpagefuns(funid, request)})
    except:
        return HttpResponseRedirect("/index")


@login_required
def groupsave(request):
    if 'id' in request.POST:
        result = {}
        id = request.POST.get('id', '')
        name = request.POST.get('name', '')
        remark = request.POST.get('remark', '')
        try:
            id = int(id)
        except:
            raise Http404()
        if name.strip() == '':
            result["res"] = '角色名称不能为空。'
        else:
            if id == 0:
                allgroup = Group.objects.filter(name=name).exclude(state="9")
                if (len(allgroup) > 0):
                    result["res"] = name + '已存在。'
                else:
                    groupsave = Group()
                    groupsave.name = name
                    groupsave.remark = remark
                    groupsave.save()

                    save_syslog(request.user.id, 'new', '角色{0}'.format(name))

                    result["res"] = "新增成功。"
                    result["data"] = groupsave.id
            else:
                allgroup = Group.objects.filter(name=name).exclude(id=id).exclude(state="9")
                if (len(allgroup) > 0):
                    result["res"] = name + '已存在。'
                else:
                    try:
                        groupsave = Group.objects.get(id=id)
                        groupsave.name = name
                        groupsave.remark = remark
                        groupsave.save()

                        save_syslog(request.user.id, 'edit', '角色{0}'.format(name))

                        result["res"] = "修改成功。"

                    except:
                        result["res"] = "修改失败。"
        return HttpResponse(json.dumps(result))


@login_required
def groupdel(request):
    if 'id' in request.POST:
        result = ""
        id = request.POST.get('id', '')
        try:
            id = int(id)
        except:
            raise Http404()
        allgroup = Group.objects.filter(id=id)
        result = '角色不存在。'
        if (len(allgroup) > 0):
            groupsave = allgroup[0]
            groupsave.state = "9"
            groupsave.save()

            save_syslog(request.user.id, 'delete', '角色{0}'.format(allgroup[0].name))

            result = "删除成功。"
        else:
            result = '角色不存在。'
        return HttpResponse(result)


@login_required
def getusertree(request):
    if 'id' in request.POST:
        id = request.POST.get('id', '')
        try:
            id = int(id)
        except:
            raise Http404()

        treedata = []
        groupsave = Group.objects.get(id=id)
        selectusers = groupsave.userinfo_set.all()

        rootnodes = UserInfo.objects.order_by("sort").exclude(state="9").filter(pnode=None, type="org")

        if len(rootnodes) > 0:
            for rootnode in rootnodes:
                root = {}
                root["text"] = rootnode.fullname
                root["id"] = "user_" + str(rootnode.id)
                root["type"] = "org"
                root["state"] = {"opened": True}
                root["children"] = group_get_user_tree(rootnode, selectusers)
                treedata.append(root)
        treedata = json.dumps(treedata)
        return HttpResponse(treedata)


@login_required
def groupsaveusertree(request):
    if 'id' in request.POST:
        id = request.POST.get('id', '')
        selectedusers = request.POST.get('selecteduser', '')
        selectedusers = selectedusers.split(',')

        try:
            id = int(id)
        except:
            raise Http404()
        groupsave = Group.objects.get(id=id)
        groupsave.userinfo_set.clear()
        if len(selectedusers) > 0:
            for selecteduser in selectedusers:
                try:
                    myuser = UserInfo.objects.get(id=int(selecteduser.replace("user_", "")))
                    if myuser.type == "user":
                        myuser.group.add(groupsave)

                        save_syslog(request.user.id, 'edit', '角色{0}配置用户'.format(groupsave.name))

                except:
                    pass
        return HttpResponse("保存成功。")


@login_required
def getfuntree(request):
    if 'id' in request.POST:
        id = request.POST.get('id', '')
        try:
            id = int(id)
        except:
            raise Http404()

        treedata = []
        groupsave = Group.objects.get(id=id)
        selectfuns = groupsave.fun.all()

        rootnodes = Fun.objects.order_by("sort").filter(pnode=None, type="node")

        if len(rootnodes) > 0:
            for rootnode in rootnodes:
                root = {}
                root["text"] = rootnode.name
                root["id"] = "fun_" + str(rootnode.id)
                root["type"] = "node"
                root["state"] = {"opened": True}
                root["children"] = group_get_fun_tree(rootnode, selectfuns)
                treedata.append(root)
        treedata = json.dumps(treedata)
        return HttpResponse(treedata)


@login_required
def groupsavefuntree(request):
    if 'id' in request.POST:
        id = request.POST.get('id', '')
        selectedfuns = request.POST.get('selectedfun', '')
        selectedfuns = selectedfuns.split(',')

        try:
            id = int(id)
        except:
            raise Http404()
        groupsave = Group.objects.get(id=id)
        groupsave.fun.clear()
        if len(selectedfuns) > 0:
            for selectedfun in selectedfuns:
                try:
                    myfun = Fun.objects.get(id=int(selectedfun.replace("fun_", "")))
                    if myfun.type == "fun":
                        groupsave.fun.add(myfun)

                        save_syslog(request.user.id, 'edit', '角色{0}功能权限'.format(groupsave.name))

                except:
                    pass
        return HttpResponse("保存成功。")


@login_required
def get_all_client_tree(request):
    id = request.POST.get('id', '')
    tree_data = []
    status = 1
    try:
        groupsave = Group.objects.get(id=int(id))
        select_hosts = groupsave.host.all()
    except Exception:
        status = 0
        tree_data = []
    else:
        root_nodes = HostsManage.objects.order_by("sort").exclude(state="9").filter(pnode=None).filter(nodetype="NODE")

        for root_node in root_nodes:
            root = dict()
            root["text"] = root_node.host_name
            root["id"] = root_node.id
            root["type"] = root_node.nodetype
            root["data"] = {
                "name": root_node.host_name,
                "remark": root_node.remark,
                "pname": "无"
            }
            if root_node.id==1:
                root["text"] = "<img src = '/static/pages/images/c.png' height='24px'> " + root["text"]

            root["state"] = {"opened": True}
            root["children"] = get_all_client_node(root_node, select_hosts)
            tree_data.append(root)
        
    return JsonResponse({
        "ret": status,
        "data": tree_data
    })


def get_all_client_node(parent, select_hosts):
    nodes = []
    children = parent.children.order_by("sort").exclude(state="9")
    for child in children:
        node = dict()
        node["text"] = child.host_name
        node["id"] = child.id
        node["type"] = child.nodetype
        node["data"] = {
            "name": child.host_name,
            "remark": child.remark,
            "pname": parent.host_name
        }

        node["children"] = get_all_client_node(child, select_hosts)
        if child.id in [1,2,3]:
            node["state"] = {"opened": True}
        if child.id==2:
            node["text"] = "<img src = '/static/pages/images/s.png' height='24px'> " + node["text"]
        if child.id==3:
            node["text"] = "<img src = '/static/pages/images/d.png' height='24px'> " + node["text"]
        if child.nodetype=="NODE" and child.id not in [1,2,3]:
            node["text"] = "<i class='jstree-icon jstree-themeicon fa fa-folder icon-state-warning icon-lg jstree-themeicon-custom'></i>" + node["text"]

        if child.nodetype == "CLIENT":
            db_client = DbCopyClient.objects.exclude(state="9").filter(hostsmanage=child)
            if len(db_client) > 0:
                if db_client[0].dbtype=="1":
                    node["text"] = "<img src = '/static/pages/images/oracle.png' height='24px'> " + node["text"]
                if db_client[0].dbtype == "2":
                    node["text"] = "<img src = '/static/pages/images/mysql.png' height='24px'> " + node["text"]
            cv_client = CvClient.objects.exclude(state="9").filter(hostsmanage=child)
            if len(cv_client)>0:
                node["text"] = "<img src = '/static/pages/images/cv.png' height='24px'> " + node["text"]
            if child in select_hosts:
                node["state"] = {"selected": True}
        nodes.append(node)
    return nodes


@login_required
def group_save_host_tree(request):
    status = 1
    info = "主机权限配置成功。"
    id = request.POST.get('id', '')
    selected_hosts = request.POST.get('selected_hosts', '')
    selected_hosts = selected_hosts.split(',')

    try:
        groupsave = Group.objects.get(id=int(id))
    except Exception:
        status = 0
        info = "节点不存在。"
    else:
        groupsave.host.clear()
        selected_hosts = [int(x) for x in filter(lambda i: True if i else False, selected_hosts)] 
        hosts = HostsManage.objects.filter(id__in=selected_hosts).filter(nodetype="CLIENT")

        try:
            groupsave.host.add(*hosts)

            save_syslog(request.user.id, 'edit', '角色{0}主机权限'.format(groupsave.name))

        except Exception:
            status = 0
            info = "关联主机失败。"

    return JsonResponse({
        "status": status,
        "info": info
    })


def get_process_node(parent, select_process):
    nodes = []
    children = parent.children.order_by("sort").exclude(state="9").exclude(Q(type=None) | Q(type=""))
    for child in children:
        node = dict()
        node["text"] = child.name
        node["id"] = child.id
        # node["children"] = get_process_node(child, select_process)
        node["type"] = "NODE"
        param_list = []
        try:
            config = etree.XML(child.config)

            param_el = config.xpath("//param")
            for v_param in param_el:
                param_list.append({
                    "param_name": v_param.attrib.get("param_name", ""),
                    "variable_name": v_param.attrib.get("variable_name", ""),
                    "param_value": v_param.attrib.get("param_value", ""),
                })
        except Exception as e:
            print(e)

        node["data"] = {
            "pname": parent.name,
            "process_id": child.id,
            "process_code": child.code,
            "process_name": child.name,
            "process_remark": child.remark,
            "process_sign": child.sign,
            "process_rto": child.rto,
            "process_rpo": child.rpo,
            "process_sort": child.sort,
            "process_color": child.color,
            "type": child.type,
            "variable_param_list": param_list,
            "cv_client": child.hosts_id
        }
        if child in select_process:
            node["state"] = {"selected": True}

        nodes.append(node)
    return nodes


@login_required
def get_all_process_tree(request):
    id = request.POST.get('id', '')
    tree_data = []
    status = 1
    try:
        groupsave = Group.objects.get(id=int(id))
        select_process = groupsave.process.all()
    except Exception:
        status = 0
        tree_data = []
    else:
        root_nodes = Process.objects.order_by("sort").exclude(state="9").filter(pnode=None)
        for root_node in root_nodes:
            root = dict()
            root["text"] = root_node.name
            root["id"] = root_node.id
            root["data"] = {
                "pname": "无"
            }
            root["type"] = "NODE"
            root["state"] = {"opened": True}
            root["children"] = get_process_node(root_node, select_process)
            tree_data.append(root)
        
    return JsonResponse({
        "ret": status,
        "data": tree_data
    })


@login_required
def group_save_process_tree(request):
    status = 1
    info = "流程权限权限配置成功。"
    id = request.POST.get('id', '')
    selected_process = request.POST.get('selected_process', '')
    selected_process = selected_process.split(',')

    try:
        groupsave = Group.objects.get(id=int(id))
    except Exception:
        status = 0
        info = "节点不存在。"
    else:
        groupsave.process.clear()
        selected_process = [int(x) for x in filter(lambda i: True if i else False, selected_process)] 
        process = Process.objects.filter(id__in=selected_process).exclude(Q(type=None) | Q(type=""))

        try:
            groupsave.process.add(*process)
        except Exception:
            status = 0
            info = "关联主机失败。"

    return JsonResponse({
        "status": status,
        "info": info
    })


######################
# 功能管理
######################
@login_required
def function(request, funid):
    return render(request, 'function.html', {
        'username': request.user.userinfo.fullname,
        "pagefuns": getpagefuns(funid, request=request)
    })


@login_required
def get_fun_tree(request):
    status = 1
    info = ""
    data = []
    select_id = request.POST.get("id", "")

    try:
        rootnodes = Fun.objects.order_by("sort").filter(pnode=None)
        if len(rootnodes) > 0:
            for rootnode in rootnodes:
                root = {}
                root["text"] = rootnode.name
                root["id"] = rootnode.id
                root["type"] = "node"
                root["data"] = {"url": rootnode.url, "icon": rootnode.icon, "pname": "无", "new_window": rootnode.if_new_wd}
                try:
                    if int(select_id) == rootnode.id:
                        root["state"] = {"opened": True, "selected": True}
                    else:
                        root["state"] = {"opened": True}
                except:
                    root["state"] = {"opened": True}
                root["children"] = get_fun_node(rootnode, select_id)
                data.append(root)
    except Exception as e:
        status = 0
        info = "获取流程树失败:{0}。".format(e)
    return JsonResponse({
        "status": status,
        "data": data,
        "info": info
    })


@login_required
def get_fun_detail(request):
    status = 1
    info = ""
    data = {}

    fun_id = request.POST.get("id", "")

    try:
        fun_id = int(fun_id)
        cur_fun = Fun.objects.get(id=fun_id)
    except Exception as e:
        status = 0
        info = "获取功能信息失败。"
    else:
        data = {
            "name": cur_fun.name,
            "pname": cur_fun.pnode.name if cur_fun.pnode else "",
            "url": cur_fun.url, 
            "icon": cur_fun.icon, 
            "new_window": cur_fun.if_new_wd if cur_fun.if_new_wd else "0",
        }

    return JsonResponse({
        "status": status,
        "data": data,
        "info": info
    })


@login_required
def fun_save(request):
    status = 1
    info = "保存成功。"

    id = request.POST.get('id')
    pid = request.POST.get('pid')
    name = request.POST.get('name')
    mytype = request.POST.get('radio2')
    url = request.POST.get('url')
    icon = request.POST.get('icon')
    new_window = request.POST.get('new_window')
    try:
        id = int(id)
    except:
        pass
    try:
        pid = int(pid)
    except:
        pass

    if name.strip() == '':
        info = '功能名称不能为空。'
        status = 0
    else:
        try:
            pfun = Fun.objects.get(id=pid)
        except:
            info = "保存失败，父节点不存在。"
            status = 0
        else:
            try:
                if id == 0:
                    sort = 1

                    try:
                        maxfun = Fun.objects.filter(pnode=pfun).latest('sort')
                        sort = maxfun.sort + 1
                    except:
                        pass
                    funsave = Fun()
                    funsave.pnode = pfun
                    funsave.name = name
                    funsave.type = mytype
                    funsave.url = url
                    funsave.icon = icon
                    funsave.sort = sort if sort else None
                    funsave.if_new_wd = new_window
                    funsave.save()
                    id = funsave.id

                    save_syslog(request.user.id, 'new', '功能{0}'.format(name))

                else:
                    funsave = Fun.objects.get(id=id)
                    if funsave.type == "node" and mytype == "fun" and len(funsave.children.all()) > 0:
                        info = '节点下还有其他节点或功能，无法修改为功能。'
                        status = 0
                    else:
                        funsave.name = name
                        funsave.type = mytype
                        funsave.url = url
                        funsave.icon = icon
                        funsave.if_new_wd = new_window
                        funsave.save()

                        save_syslog(request.user.id, 'edit', '功能{0}'.format(name))

            except Exception as e:
                print(e)
                info = '保存失败。'
                status = 0

    return JsonResponse({
        "status": status,
        "info": info,
        "data": id
    })


@login_required
def fundel(request):
    if 'id' in request.POST:
        id = request.POST.get('id', '')
        try:
            id = int(id)
        except:
            raise Http404()
        allfun = Fun.objects.filter(id=id)
        if (len(allfun) > 0):
            sort = allfun[0].sort
            pfun = allfun[0].pnode
            allfun[0].delete()
            sortfuns = Fun.objects.filter(pnode=pfun).filter(sort__gt=sort)
            if len(sortfuns) > 0:
                for sortfun in sortfuns:
                    try:
                        sortfun.sort = sortfun.sort - 1
                        sortfun.save()
                    except:
                        pass

            save_syslog(request.user.id, 'delete', '功能{0}'.format(allfun[0].name))

            return HttpResponse(1)
        else:
            return HttpResponse(0)


@login_required
def funmove(request):
    if 'id' in request.POST:
        id = request.POST.get('id', '')
        parent = request.POST.get('parent', '')
        old_parent = request.POST.get('old_parent', '')
        position = request.POST.get('position', '')
        old_position = request.POST.get('old_position', '')
        try:
            id = int(id)
        except:
            raise Http404()
        try:
            parent = int(parent)
        except:
            raise Http404()
        try:
            position = int(position)
        except:
            raise Http404()
        try:
            parent = int(parent)
        except:
            raise Http404()
        try:
            old_position = int(old_position)
        except:
            raise Http404()
        oldpfun = Fun.objects.get(id=old_parent)
        oldsort = old_position + 1
        oldfuns = Fun.objects.filter(pnode=oldpfun).filter(sort__gt=oldsort)

        pfun = Fun.objects.get(id=parent)
        sort = position + 1
        funs = Fun.objects.filter(pnode=pfun).filter(sort__gte=sort).exclude(id=id)

        if pfun.type == "fun":
            return HttpResponse("类型")
        else:
            if (len(oldfuns) > 0):
                for oldfun in oldfuns:
                    try:
                        oldfun.sort = oldfun.sort - 1
                        oldfun.save()
                    except:
                        pass

            if (len(funs) > 0):
                for fun in funs:
                    try:
                        fun.sort = fun.sort + 1
                        fun.save()
                    except:
                        pass
            myfun = Fun.objects.get(id=id)
            try:
                myfun.pnode = pfun
                myfun.sort = sort
                myfun.save()

                save_syslog(request.user.id, 'edit', '{0}功能位置'.format(myfun.name))

            except:
                pass
            if parent != old_parent:
                return HttpResponse(pfun.name + "^" + str(pfun.id))
            else:
                return HttpResponse("0")



######################
#     字典管理        #
######################
def dictindex(request, funid):
    if request.user.is_authenticated():
        alldict = DictIndex.objects.order_by("sort").exclude(state="9")
        return render(request, 'dict.html',
                      {'username': request.user.userinfo.fullname,
                       "alldict": alldict, "pagefuns": getpagefuns(funid,request)})
    else:
        return HttpResponseRedirect("/login")


@login_required
def dictdel(request):
    if 'dictid' in request.POST:
        result = ""
        dictid = request.POST.get('dictid', '')
        try:
            dictid = int(dictid.replace("dict_", ""))
        except:
            raise Http404()
        alldict = DictIndex.objects.filter(id=dictid)
        if (len(alldict) > 0):
            dictsave = alldict[0]
            dictsave.state = "9"
            dictsave.save()

            save_syslog(request.user.id, 'delete', '字典{0}'.format(alldict[0].name))

            result = "删除成功。"
        else:
            result = '字典不存在。'
        return HttpResponse(result)


@login_required
def dictlistdel(request):
    if 'listid' in request.POST:
        result = ""
        listid = request.POST.get('listid', '')
        try:
            listid = int(listid.replace("list_", ""))
        except:
            raise Http404()
        alllist = DictList.objects.filter(id=listid)
        if (len(alllist) > 0):
            listsave = alllist[0]
            listsave.state = "9"
            listsave.save()

            save_syslog(request.user.id, 'delete', '条目{0}'.format(alllist[0].name))

            result = "删除成功。"
        else:
            result = '条目不存在。'
        return HttpResponse(result)


@login_required
def dictselect(request):
    if request.method == 'GET':
        result = []
        dictid = request.GET.get('dictid', '')
        try:
            dictid = int(dictid.replace("dict_", ""))
        except:
            raise Http404()
        alldict = DictIndex.objects.get(id=dictid)
        allDictList = DictList.objects.order_by("sort").filter(dictindex=alldict).exclude(state="9")
        if (len(allDictList) > 0):
            for dict_list in allDictList:
                result.append(
                    {"id": dict_list.id, "name": dict_list.name, "sort": dict_list.sort, "remark": dict_list.remark, "content": dict_list.content})
        return HttpResponse(json.dumps(result))


@login_required
def dictsave(request):
    if 'dictid' in request.POST:
        result = {}
        dictid = request.POST.get('dictid', '')
        dictname = request.POST.get('dictname', '')
        dictsort = request.POST.get('dictsort', '')
        dictremark = request.POST.get('dictremark', '')
        try:
            dictsort = int(dictsort)
        except:
            dictsort = 999999
        try:
            dictid = int(dictid.replace("dict_", ""))
        except:
            raise Http404()
        if dictname.strip() == '':
            result["res"] = '字典名称不能为空。'
        else:
            if dictid == 0:
                alldict = DictIndex.objects.filter(
                    name=dictname).exclude(state="9")
                if (len(alldict) > 0):
                    result["res"] = dictname + '已存在。'
                else:
                    dictsave = DictIndex()
                    dictsave.name = dictname
                    dictsave.sort = dictsort
                    dictsave.remark = dictremark
                    dictsave.save()
                    dictsave = DictIndex.objects.filter(name=dictname).exclude(state="9")

                    save_syslog(request.user.id, 'new', '字典{0}'.format(dictname))

                    result["res"] = "新增成功。"
                    result["data"] = dictsave[0].id
            else:
                alldict = DictIndex.objects.filter(
                    name=dictname).exclude(id=dictid).exclude(state="9")
                if (len(alldict) > 0):
                    result["res"] = dictname + '已存在。'
                else:
                    try:
                        dictsave = DictIndex.objects.get(id=dictid)
                        dictsave.name = dictname
                        dictsave.sort = dictsort
                        dictsave.remark = dictremark
                        dictsave.save()

                        save_syslog(request.user.id, 'edit', '字典{0}'.format(dictname))

                        result["res"] = "修改成功。"
                    except:
                        result["res"] = "修改失败。"
        return HttpResponse(json.dumps(result))


@login_required
def dictlistsave(request):
    if 'dictid' in request.POST:
        result = {}

        listid = request.POST.get('listid', '')
        dictid = request.POST.get('dictid', '')
        listname = request.POST.get('listname', '')
        listsort = request.POST.get('listsort', '')
        listremark = request.POST.get('listremark', '')
        listcontent = request.POST.get('listcontent', '')

        try:
            listsort = int(listsort)
        except:
            listsort = 999999
        try:
            dictid = int(dictid.replace("dict_", ""))
        except:
            raise Http404()
        try:
            listid = int(listid.replace("list_", ""))
        except:
            raise Http404()
        if listname.strip() == '':
            result["res"] = '条目名称不能为空。'
        else:
            alldict = DictIndex.objects.get(id=dictid)
            if listid == 0:

                alllist = DictList.objects.filter(
                    name=listname, dictindex=alldict).exclude(state="9")
                if (len(alllist) > 0):
                    result["res"] = listname + '已存在。'
                else:
                    listsave = DictList()
                    listsave.dictindex = alldict
                    listsave.name = listname
                    listsave.sort = listsort
                    listsave.remark = listremark
                    listsave.content = listcontent
                    listsave.save()
                    listsave = DictList.objects.filter(name=listname, dictindex=alldict).exclude(state="9")

                    save_syslog(request.user.id, 'new', '条目{0}'.format(listname))

                    result["res"] = "新增成功。"
                    result["data"] = listsave[0].id
            else:
                alllist = DictList.objects.filter(name=listname).filter(dictindex=alldict).exclude(id=listid).exclude(
                    state="9")
                if (len(alllist) > 0):
                    result["res"] = listname + '已存在。'
                else:
                    try:
                        listsave = DictList.objects.get(id=listid)
                        listsave.name = listname
                        listsave.sort = listsort
                        listsave.remark = listremark
                        listsave.content = listcontent
                        listsave.save()

                        save_syslog(request.user.id, 'edit', '条目{0}'.format(listname))

                        result["res"] = "修改成功。"
                    except:
                        result["res"] = "修改失败。"
        return HttpResponse(json.dumps(result))


# 系统日志

def syslog_index(request, funid):
    if request.user.is_authenticated():
        starttime = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime("%Y-%m-%d")
        endtime = datetime.datetime.now().strftime("%Y-%m-%d")
        type_dict = {
            'login': '登录',
            'new': '新增',
            'edit': '修改',
            'delete': '删除',
            'other': '其他',
            'WORKFLOW': '执行流程',
            'COMPONENT': '执行组件',

        }
        return render(request, 'syslog.html',
                      {'username': request.user.userinfo.fullname,
                       "pagefuns": getpagefuns(funid,request),
                       "starttime": starttime,
                       "endtime": endtime,
                       "type_dict": type_dict
                       })
    else:
        return HttpResponseRedirect("/login")


def job_xml_to_dict(component_xmlinfo, info_type):
    if component_xmlinfo and len(component_xmlinfo.strip()) > 0:
        info = []
        try:
            if info_type == 'finalinput':
                tmpInput = xmltodict.parse(component_xmlinfo)
                if "inputs" in tmpInput and tmpInput["inputs"] and "input" in tmpInput["inputs"] and tmpInput["inputs"][
                    "input"]:
                    tmpDTL = tmpInput["inputs"]["input"]
                    if str(type(tmpDTL)) == "<class 'collections.OrderedDict'>":
                        tmpDTL = [tmpDTL]
                    for curinput in tmpDTL:
                        info.append({"code": curinput["code"], "name": curinput["name"], "type": curinput["type"],
                                        "remark": curinput["remark"], "source": curinput["source"],
                                        "value": curinput["value"]})
            else:
                tmpoutput = xmltodict.parse(component_xmlinfo)
                if "outputs" in tmpoutput and tmpoutput["outputs"] and "output" in tmpoutput["outputs"] and \
                        tmpoutput["outputs"]["output"]:
                    tmpDTL = tmpoutput["outputs"]["output"]
                    if str(type(tmpDTL)) == "<class 'collections.OrderedDict'>":
                        tmpDTL = [tmpDTL]
                    for curoutput in tmpDTL:
                        info.append({"code": curoutput["code"], "name": curoutput["name"], "type": curoutput["type"],
                                    "remark": curoutput["remark"], "value": curoutput["value"]})
        except:
            pass
        return info


def syslog_data(request):
    if request.user.is_authenticated():
        startdate = request.GET.get('startdate', '')
        enddate = request.GET.get('enddate', '')
        start_time = datetime.datetime.strptime(startdate, '%Y-%m-%d').strftime('%Y-%m-%d %H:%M:%S')
        end_time = (datetime.datetime.strptime(enddate, '%Y-%m-%d') + datetime.timedelta(days=1) - datetime.timedelta(
            seconds=1)).strftime('%Y-%m-%d %H:%M:%S')
        sys_user = request.GET.get('user', '')
        sys_type = request.GET.get('type', '')
        type_dict = {
            'login': '登录',
            'new': '新增',
            'edit': '修改',
            'delete': '删除',
            'other': '其他',
            'WORKFLOW': '执行流程',
            'COMPONENT': '执行组件',
            'NOTEXIST': '组件不存在',
            "PAUSE": "暂停",
            "RUN": "运行",
            "STOP": "停止",
            "ERROR": "错误",
            "BREAK": "跳出",
            "SKIP": "跳过",
            "WAIT": "等待",
            "DONE": "完成",
            "": "未开始"
        }
        log_list = []
        # syslog表中日志信息
        cursor = connection.cursor()
        syslog_sql = "select drm_syslog.id, drm_syslog.datatime, drm_syslog.type, drm_syslog.content, " \
                   "drm_userinfo.fullname from drm_syslog,drm_userinfo where drm_syslog.user_id=drm_userinfo.user_id " \
                   "and (drm_syslog.state is null or drm_syslog.state != '9')"
        if len(start_time.strip()) > 0:
            syslog_sql += " and drm_syslog.datatime >='" + start_time + "'"
        if len(end_time.strip()) > 0:
            syslog_sql += " and drm_syslog.datatime <='" + end_time + "'"
        if sys_user:
            syslog_sql += " and drm_userinfo.fullname like '%" + sys_user + "%'"
        if sys_type != "":
            syslog_sql += " and drm_syslog.type ='" + str(sys_type) + "'"
        syslog_sql += " order by drm_syslog.datatime desc"
        cursor.execute(syslog_sql)
        syslog_rows = cursor.fetchall()
        for syslog in syslog_rows:
            id = syslog[0]
            datatime = syslog[1].strftime('%Y-%m-%d %H:%M:%S') if syslog[1] else ""
            log_type = type_dict.get(syslog[2])
            content = syslog[3]
            user = syslog[4]
            log = '{user}{type}{content}。'.format(**{
                'user': '<span style="color:#3598DC">{0}</span>'.format(user),
                'type': '<span style="color:#F7CA18">{0}</span>'.format(log_type),
                'content': '<span style="color:#26C281">{0}</span>'.format(content),
            })
            log_list.append({
                'id': id,
                'datatime': datatime,
                'user': user,
                'type': log_type,
                'log': log,
            })

        # job表中组件日志信息
        joblog_zj_sql = "select drm_tsdrmjob.id, drm_tsdrmjob.createtime, drm_tsdrmjob.type, drm_userinfo.fullname," \
                        "drm_tsdrmcomponent.shortname, drm_tsdrmjob.state,drm_tsdrmjob.guid,drm_tsdrmjob.finalinput," \
                        "drm_tsdrmjob.output from drm_tsdrmjob,drm_userinfo,drm_tsdrmcomponent " \
                        "where drm_tsdrmjob.startuser_id=drm_userinfo.id and drm_tsdrmjob.modelguid = drm_tsdrmcomponent.guid " \
                        "and (drm_tsdrmjob.state is null or (drm_tsdrmjob.state != '9' and drm_tsdrmjob.state!='REJECT')) " \
                        "and drm_tsdrmjob.pjob_id is null and drm_tsdrmjob.type = 'COMPONENT'"
        if len(start_time.strip()) > 0:
            joblog_zj_sql += " and drm_tsdrmjob.createtime >='" + start_time + "'"
        if len(end_time.strip()) > 0:
            joblog_zj_sql += " and drm_tsdrmjob.createtime <='" + end_time + "'"
        if sys_user:
            joblog_zj_sql += " and drm_userinfo.fullname like '%" + sys_user + "%'"
        if sys_type != "":
            joblog_zj_sql += " and drm_tsdrmjob.type ='" + str(sys_type) + "'"
        joblog_zj_sql += " order by drm_tsdrmjob.createtime desc"
        cursor.execute(joblog_zj_sql)
        joblog_zj_rows = cursor.fetchall()
        for joblog_zj in joblog_zj_rows:
            id_zj = joblog_zj[0] if joblog_zj[0] else ""
            datatime_zj = joblog_zj[1].strftime('%Y-%m-%d %H:%M:%S') if joblog_zj[1] else ""
            type_zj = type_dict.get(joblog_zj[2]) if joblog_zj[2] else ""
            user_zj = joblog_zj[3] if joblog_zj[3] else ""
            shortname_zj = joblog_zj[4] if joblog_zj[4] else ""
            state_zj = type_dict.get(joblog_zj[5]) if joblog_zj[5] else ""
            guid_zj = joblog_zj[6] if joblog_zj[6] else ""
            content_zj = shortname_zj + state_zj
            finalinput_zj = job_xml_to_dict(joblog_zj[7], 'finalinput') if joblog_zj[7] else ""
            output_zj = job_xml_to_dict(joblog_zj[8], 'output') if joblog_zj[8] else ""
            log_zj = '{user}{type}{content}。'.format(**{
                'user': '<span style="color:#3598DC">{0}</span>'.format(user_zj),
                'type': '<span style="color:#F7CA18">{0}</span>'.format(type_zj),
                'content': '<span style="color:#26C281">{0}</span>'.format(content_zj),
            })
            log_list.append({
                'id': id_zj,
                'datatime': datatime_zj,
                'type': type_zj,
                'user': user_zj,
                'shortname': shortname_zj,
                'state': state_zj,
                'guid': guid_zj,
                'finalinput': finalinput_zj,
                'output': output_zj,
                'log': log_zj,
            })

        # job表中流程日志信息
        joblog_lc_sql = "select drm_tsdrmjob.id,drm_tsdrmjob.createtime,drm_tsdrmjob.type,drm_userinfo.fullname," \
                        "drm_tsdrmjob.name,drm_tsdrmjob.state,drm_tsdrmjob.guid,drm_tsdrmjob.finalinput," \
                        "drm_tsdrmjob.output from drm_tsdrmjob,drm_userinfo where drm_tsdrmjob.startuser_id=drm_userinfo.id " \
                        "and (drm_tsdrmjob.state is null or (drm_tsdrmjob.state != '9' and drm_tsdrmjob.state!='REJECT')) " \
                        "and drm_tsdrmjob.pjob_id is null and drm_tsdrmjob.type = 'WORKFLOW'"
        if len(start_time.strip()) > 0:
            joblog_lc_sql += " and drm_tsdrmjob.createtime >='" + start_time + "'"
        if len(end_time.strip()) > 0:
            joblog_lc_sql += " and drm_tsdrmjob.createtime <='" + end_time + "'"
        if sys_user:
            joblog_lc_sql += " and drm_userinfo.fullname like '%" + sys_user + "%'"
        if sys_type != "":
            joblog_lc_sql += " and drm_tsdrmjob.type ='" + str(sys_type) + "'"
        joblog_lc_sql += " order by drm_tsdrmjob.createtime desc"
        cursor.execute(joblog_lc_sql)
        joblog_lc_rows = cursor.fetchall()
        for joblog_lc in joblog_lc_rows:
            id_lc = joblog_lc[0] if joblog_lc[0] else ""
            datatime_lc = joblog_lc[1].strftime('%Y-%m-%d %H:%M:%S') if joblog_lc[1] else ""
            type_lc = type_dict.get(joblog_lc[2]) if joblog_lc[2] else ""
            user_lc = joblog_lc[3] if joblog_lc[3] else ""
            shortname_lc = joblog_lc[4] if joblog_lc[4] else ""
            state_lc = type_dict.get(joblog_lc[5]) if joblog_lc[5] else ""
            guid_lc = joblog_lc[6] if joblog_lc[6] else ""
            content_lc = shortname_lc + state_lc
            finalinput_lc = job_xml_to_dict(joblog_lc[7], 'finalinput') if joblog_lc[7] else ""
            output_lc = job_xml_to_dict(joblog_lc[8], 'output') if joblog_lc[8] else ""
            log_lc = '{user}{type}{content}。'.format(**{
                'user': '<span style="color:#3598DC">{0}</span>'.format(user_lc),
                'type': '<span style="color:#F7CA18">{0}</span>'.format(type_lc),
                'content': '<span style="color:#26C281">{0}</span>'.format(content_lc),
            })
            log_list.append({
                'id': id_lc,
                'datatime': datatime_lc,
                'type': type_lc,
                'user': user_lc,
                'shortname': shortname_lc,
                'state': state_lc,
                'guid': guid_lc,
                'finalinput': finalinput_lc,
                'output': output_lc,
                'log': log_lc,
            })
        return JsonResponse({
            'data': log_list
        })
    else:
        return HttpResponseRedirect('/login')


