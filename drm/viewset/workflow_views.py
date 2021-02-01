# 流程管理
from .commv_views import *
from .basic_views import getpagefuns
from django.contrib.auth.decorators import login_required

######################
# 流程管理
######################
@login_required
def workflow(request, funid):
    grouplist = Group.objects.all().exclude(state='9')
    return render(request, 'workflow.html',
                  {'username': request.user.userinfo.fullname, "pagefuns": getpagefuns(funid, request=request),"grouplist": grouplist})
