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
    try:
        errors = []
        title = "请选择组织"
        selectid = ""
        id = ""
        pid = ""
        pname = ""
        noselectgroup = []
        selectgroup = []
        username = ""
        fullname = ""
        orgname = ""
        phone = ""
        email = ""
        password = ""
        mytype = ""
        remark = ""
        hiddendiv = "hidden"
        hiddenuser = "hidden"
        hiddenorg = "hidden"
        newpassword = "hidden"
        editpassword = ""
        allgroup = Group.objects.exclude(state="9")
        if request.method == 'POST':
            hiddendiv = ""
            id = request.POST.get('id')
            pid = request.POST.get('pid')
            mytype = request.POST.get('mytype')
            try:
                id = int(id)

            except:
                raise Http404()
            try:
                pid = int(pid)
            except:
                raise Http404()

            if 'usersave' in request.POST:
                hiddenuser = ""
                hiddenorg = "hidden"
                grouplist = request.POST.getlist('source')
                noselectgroup = []
                selectgroup = []
                for group in allgroup:
                    if str(group.id) in grouplist:
                        selectgroup.append({"groupname": group.name, "id": group.id})
                    else:
                        noselectgroup.append({"groupname": group.name, "id": group.id})
                pname = request.POST.get('pname')
                username = request.POST.get('myusername', '')
                fullname = request.POST.get('fullname', '')
                phone = request.POST.get('phone', '')
                email = request.POST.get('email', '')
                password = request.POST.get('password', '')
                if id == 0:
                    newpassword = ""
                    editpassword = "hidden"
                    selectid = pid
                    title = "新建"
                    alluser = User.objects.filter(username=username)
                    if username.strip() == '':
                        errors.append('用户名不能为空。')
                    else:
                        if password.strip() == '':
                            errors.append('密码不能为空。')
                        else:
                            if fullname.strip() == '':
                                errors.append('姓名不能为空。')
                            else:
                                if (len(alluser) > 0):
                                    errors.append('用户名:' + username + '已存在。')
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
                                            except ValueError:
                                                raise Http404()
                                        title = fullname
                                        selectid = profile.id
                                        id = profile.id
                                        newpassword = "hidden"
                                        editpassword = ""
                                    except ValueError:
                                        raise Http404()
                else:
                    selectid = id
                    title = fullname
                    exalluser = User.objects.filter(username=username)
                    if username.strip() == '':
                        errors.append('用户名不能为空。')
                    else:
                        if fullname.strip() == '':
                            errors.append('姓名不能为空。')
                        else:
                            if (len(exalluser) > 0 and exalluser[0].userinfo.id != id):
                                errors.append('用户名:' + username + '已存在。')
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
                                    title = fullname
                                except:
                                    errors.append('保存失败。')

            else:
                if 'orgsave' in request.POST:
                    hiddenuser = "hidden"
                    hiddenorg = ""
                    pname = request.POST.get('orgpname')
                    orgname = request.POST.get('orgname', '')
                    remark = request.POST.get('remark', '')
                    if id == 0:
                        selectid = pid
                        title = "新建"
                        try:
                            porg = UserInfo.objects.get(id=pid)
                        except:
                            raise Http404()
                        allorg = UserInfo.objects.filter(fullname=orgname, pnode=porg)
                        if orgname.strip() == '':
                            errors.append('组织名称不能为空。')
                        else:
                            if (len(allorg) > 0):
                                errors.append(orgname + '已存在。')
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
                                    title = orgname
                                    selectid = profile.id
                                    id = profile.id
                                except ValueError:
                                    raise Http404()
                    else:
                        selectid = id
                        title = orgname
                        try:
                            porg = UserInfo.objects.get(id=pid)
                        except:
                            raise Http404()
                        exalluser = UserInfo.objects.filter(fullname=orgname, pnode=porg).exclude(state="9")
                        if orgname.strip() == '':
                            errors.append('组织名称不能为空。')
                        else:
                            if (len(exalluser) > 0 and exalluser[0].id != id):
                                errors.append(username + '已存在。')
                            else:
                                try:
                                    alluserinfo = UserInfo.objects.get(id=id)
                                    alluserinfo.fullname = orgname
                                    alluserinfo.remark = remark
                                    alluserinfo.save()
                                    title = orgname
                                except:
                                    errors.append('保存失败。')
        treedata = []
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
                root["data"] = {"remark": rootnode.remark, "pname": "无", "myallgroup": myallgroup}
                try:
                    if int(selectid) == rootnode.id:
                        root["state"] = {"opened": True, "selected": True}
                    else:
                        root["state"] = {"opened": True}
                except:
                    root["state"] = {"opened": True}
                root["children"] = get_org_tree(rootnode, selectid, allgroup)
                treedata.append(root)
        treedata = json.dumps(treedata)
        return render(request, 'organization.html',
                      {'username': request.user.userinfo.fullname, 'errors': errors, "id": id, "orgname": orgname,
                       "pid": pid, "pname": pname, "fullname": fullname, "phone": phone, "myusername": username,
                       "email": email, "password": password, "noselectgroup": noselectgroup,
                       "selectgroup": selectgroup, "remark": remark, "title": title, "mytype": mytype,
                       "hiddenuser": hiddenuser, "hiddenorg": hiddenorg, "newpassword": newpassword,
                       "editpassword": editpassword, "hiddendiv": hiddendiv, "treedata": treedata,
                       "pagefuns": getpagefuns(funid, request=request)})

    except:
        return HttpResponseRedirect("/index")


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
        node["children"] = get_process_node(child, select_process)
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
    try:
        errors = []
        title = "请选择功能"
        selectid = ""
        id = ""
        pid = ""
        pname = ""
        name = ""
        mytype = ""
        url = ""
        icon = ""
        hiddendiv = "hidden"

        if request.method == 'POST':
            hiddendiv = ""
            id = request.POST.get('id')
            pid = request.POST.get('pid')
            pname = request.POST.get('pname')
            name = request.POST.get('name')
            mytype = request.POST.get('radio2')
            url = request.POST.get('url')
            icon = request.POST.get('icon')
            try:
                id = int(id)

            except:
                raise Http404()
            try:
                pid = int(pid)
            except:
                raise Http404()
            if id == 0:
                selectid = pid
                title = "新建"
            else:

                selectid = id
                title = name

            if name.strip() == '':
                errors.append('功能名称不能为空。')

            else:
                try:
                    pfun = Fun.objects.get(id=pid)
                except:
                    raise Http404()
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
                        funsave.save()
                        title = name
                        id = funsave.id
                        selectid = id
                    else:
                        funsave = Fun.objects.get(id=id)
                        if funsave.type == "node" and mytype == "fun" and len(funsave.children.all()) > 0:
                            errors.append('节点下还有其他节点或功能，无法修改为功能。')
                        else:
                            funsave.name = name
                            funsave.type = mytype
                            funsave.url = url
                            funsave.icon = icon
                            funsave.save()
                            title = name
                except:
                    errors.append('保存失败。')
        treedata = []
        rootnodes = Fun.objects.order_by("sort").filter(pnode=None)
        if len(rootnodes) > 0:
            for rootnode in rootnodes:
                root = {}
                root["text"] = rootnode.name
                root["id"] = rootnode.id
                root["type"] = "node"
                root["data"] = {"url": rootnode.url, "icon": rootnode.icon, "pname": "无"}
                try:
                    if int(selectid) == rootnode.id:
                        root["state"] = {"opened": True, "selected": True}
                    else:
                        root["state"] = {"opened": True}
                except:
                    root["state"] = {"opened": True}
                root["children"] = get_fun_tree(rootnode, selectid)
                treedata.append(root)
        treedata = json.dumps(treedata)
        return render(request, 'function.html',
                      {'username': request.user.userinfo.fullname, 'errors': errors, "id": id,
                       "pid": pid, "pname": pname, "name": name, "url": url, "icon": icon, "title": title,
                       "mytype": mytype, "hiddendiv": hiddendiv, "treedata": treedata,
                       "pagefuns": getpagefuns(funid, request=request)})
    except:
        return HttpResponseRedirect("/index")


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
            except:
                pass
            if parent != old_parent:
                return HttpResponse(pfun.name + "^" + str(pfun.id))
            else:
                return HttpResponse("0")
