from django.conf.urls import url
from django.views.generic.base import RedirectView
from .viewset.basic_views import *
from .viewset.system_views import *
from .viewset.dashboard_views import *
from .viewset.config_views import *
from .viewset.monitor_views import *
from .viewset.commv_views import *
from .viewset.report_views import *
from .viewset.workflow_views import *
from .viewset.test import *


urlpatterns = [
    url(r'^test/$', test),
    url(r'^tsdrmstart1/$', tsdrmstart1),
    url(r'^tsdrmstart2/$', tsdrmstart2),
    url(r'^tsdrmstop/$', tsdrmstop),
    url(r'^tsdrmpause/$', tsdrmpause),
    url(r'^tsdrmretry1/$', tsdrmretry1),
    url(r'^tsdrmretry2/$', tsdrmretry2),

    url(r'^favicon.ico$', RedirectView.as_view(url=r'static/pages/images/logo/favicon.ico')),
    url(r'^$', index, {'funid': '2'}),
    url(r'^processindex/(\d+)/$', processindex),
    url(r'^index/$', index, {'funid': '2'}),
    url(r'^get_process_rto/$', get_process_rto),
    url(r'^get_daily_processrun/$', get_daily_processrun),
    url(r'^get_process_index_data/$', get_process_index_data),
    url(r'^monitor/$', monitor),
    url(r'^get_monitor_data/$', get_monitor_data),
    url(r'^get_clients_status/$', get_clients_status),

    # 用户登录
    url(r'^login/$', login),
    url(r'^userlogin/$', userlogin),
    url(r'^forgetPassword/$', forgetPassword),
    url(r'^resetpassword/([0-9a-zA-Z]{8}-[0-9a-zA-Z]{4}-[0-9a-zA-Z]{4}-[0-9a-zA-Z]{4}-[0-9a-zA-Z]{12})/$',
        resetpassword),
    url(r'^reset/$', reset),
    url(r'^password/$', password),
    url(r'^userpassword/$', userpassword),

    # 系统维护
    url(r'^organization/$', organization, {'funid': '61'}),
    url(r'^get_org_tree/$', get_org_tree),
    url(r'^get_org_detail/$', get_org_detail),
    url(r'^org_user_save/$', org_user_save),
    url(r'^orgdel/$', orgdel),
    url(r'^orgmove/$', orgmove),
    url(r'^orgpassword/$', orgpassword),
    url(r'^group/$', group, {'funid': '62'}),
    url(r'^groupsave/$', groupsave),
    url(r'^groupdel/$', groupdel),
    url(r'^getusertree/$', getusertree),
    url(r'^groupsaveusertree/$', groupsaveusertree),
    url(r'^getfuntree/$', getfuntree),
    url(r'^groupsavefuntree/$', groupsavefuntree),
    url(r'^function/$', function, {'funid': '63'}),
    url(r'^get_fun_tree/$', get_fun_tree),
    url(r'^get_fun_detail/$', get_fun_detail),
    url(r'^fun_save/$', fun_save),
    url(r'^fundel/$', fundel),
    url(r'^funmove/$', funmove),
    url(r'^get_all_client_tree/$', get_all_client_tree),
    url(r'^group_save_host_tree/$', group_save_host_tree),
    url(r'^get_all_process_tree/$', get_all_process_tree),
    url(r'^group_save_process_tree/$', group_save_process_tree),


    # 工具管理
    url(r'^util_manage/$', util_manage, {'funid': '88'}),
    url(r'^util_manage_save/$', util_manage_save),
    url(r'^util_manage_data/$', util_manage_data),
    url(r'^util_manage_del/$', util_manage_del),

    # 客户端管理
    url(r'^target/$', target, {'funid': '71'}),
    url(r'^target_data/$', target_data),
    url(r'^target_save/$', target_save),
    url(r'^target_del/$', target_del),

    url(r'^origin/$', origin, {'funid': '70'}),
    url(r'^origin_data/$', origin_data),
    url(r'^origin_save/$', origin_save),
    url(r'^origin_del/$', origin_del),

    # 预案管理
    url(r'^script/$', script, {'funid': '32'}),
    url(r'^scriptdel/$', scriptdel),
    url(r'^script_move/$', script_move),
    url(r'^get_script_detail/$', get_script_detail),
    url(r'^get_script_tree/$', get_script_tree),
    url(r'^script_save/$', script_save),

    url(r'^processconfig/$', processconfig, {'funid': '31'}),
    url(r'^processscriptsave/$', processscriptsave),
    url(r'^get_script_data/$', get_script_data),
    url(r'^remove_script/$', remove_script),
    url(r'^setpsave/$', setpsave),
    url(r'^custom_step_tree/$', custom_step_tree),
    url(r'^get_step_detail/$', get_step_detail),
    url(r'^del_step/$', del_step),
    url(r'^move_step/$', move_step),
    url(r'^get_all_groups/$', get_all_groups),
    url(r'^processdesign/$', process_design, {"funid": "33"}),
    url(r'^get_process_tree/$', get_process_tree),
    url(r'^get_process_detail/$', get_process_detail),
    url(r'^process_save/$', process_save),
    url(r'^process_del/$', process_del),
    url(r'^process_move/$', process_move),
    url(r'^verify_items_save/$', verify_items_save),
    url(r'^get_verify_items_data/$', get_verify_items_data),
    url(r'^remove_verify_item/$', remove_verify_item),
    url(r'^display_params/$', display_params),
    url(r'^load_hosts_params/$', load_hosts_params),
    url(r'^get_error_solved_process/$', get_error_solved_process),
    url(r'^solve_error/$', solve_error),
    url(r'^get_error_sovled_status/$', get_error_sovled_status),

    # Oracle恢复
    url(r'^oracle_restore/(?P<process_id>\d+)$', oracle_restore),
    url(r'^oracle_restore_data/$', oracle_restore_data),
    url(r'^cv_oracle_run/$', cv_oracle_run),
    url(r'^cv_oracle/(\d+)/$', cv_oracle, {'funid': '96'}),

    url(r'^getrunsetps/$', getrunsetps),
    url(r'^cv_oracle_continue/$', cv_oracle_continue),
    url(r'^processsignsave/$', processsignsave),
    url(r'^get_current_scriptinfo/$', get_current_scriptinfo),
    url(r'^ignore_current_script/$', ignore_current_script),
    url(r'^stop_current_process/$', stop_current_process),
    url(r'^verify_items/$', verify_items),
    url(r'^show_result/$', show_result),
    url(r'^reject_invited/$', reject_invited),
    
    url(r'^reload_task_nums/$', reload_task_nums),
    url(r'^delete_current_process_run/$', delete_current_process_run),
    url(r'^get_celery_tasks_info/$', get_celery_tasks_info),
    url(r'^revoke_current_task/$', revoke_current_task),
    url(r'^get_script_log/$', get_script_log),
    url(r'^save_task_remark/$', save_task_remark),
    url(r'^get_server_time_very_second/$', get_server_time_very_second),

    url(r'^get_force_script_info/$', get_force_script_info),


    # 历史查询
    url(r'^custom_pdf_report/$', custom_pdf_report),
    url(r'^restore_search/$', restore_search, {'funid': '64'}),
    url(r'^restore_search_data/$', restore_search_data),
    url(r'^tasksearch/$', tasksearch, {'funid': '65'}),
    url(r'^tasksearchdata/$', tasksearchdata),

    # 其他
    url(r'^downloadlist/$', downloadlist, {'funid': '7'}),
    url(r'^download/$', download),
    url(r'^download_list_data/$', download_list_data),
    url(r'^knowledge_file_del/$', knowledge_file_del),

    # 邀请
    url(r'^invite/$', invite),
    url(r'^get_all_users/$', get_all_users),

    # 通讯录
    url(r'^contact/$', contact, {'funid': '67'}),
    url(r'^get_contact_tree/$', get_contact_tree),
    url(r'^get_contact_info/$', get_contact_info),

    # 服务器信息配置
    url(r'^serverconfig/$', serverconfig, {'funid': '72'}),
    url(r'^serverconfigsave/$', serverconfigsave),



    # 自主恢复
    url(r'^manualrecovery/$', manualrecovery, {'funid': '79'}),
    url(r'^manualrecoverydata/$', manualrecoverydata),

    url(r'^dooraclerecovery/$', dooraclerecovery),
    url(r'^oraclerecoverydata/$', oraclerecoverydata),

    # 演练概况
    url(r'^get_process_run_facts/$', get_process_run_facts),

    # 流程计划
    url(r'^process_schedule/$', process_schedule, {'funid': '84'}),
    url(r'^process_schedule_save/$', process_schedule_save),
    url(r'^process_schedule_data/$', process_schedule_data),
    url(r'^change_periodictask/$', change_periodictask),
    url(r'^process_schedule_del/$', process_schedule_del),

    # 仪表盘
    url(r'^dashboard/$', dashboard, {'funid': '89'}),
    url(r'^get_dashboard/$', get_dashboard),
    url(r'^get_frameworkstate/$', get_frameworkstate),
    url(r'^cv_joblist/$', cv_joblist, {'funid': '92'}),
    url(r'^get_cv_joblist/$', get_cv_joblist),
    url(r'^get_client_name/$', get_client_name),
    url(r'^display_error_job/$', display_error_job, {'funid': '93'}),
    url(r'^get_display_error_job/$', get_display_error_job),
    url(r'^get_top5_app_capacity/$', get_top5_app_capacity),

    #灾备基础框架
    url(r'^framework/$', framework, {'funid': '90'}),
    url(r'^get_framework/$', get_framework),
    url(r'^get_csinfo/$', get_csinfo),

    # 客户端监控
    url(r'^client_list/$', client_list, {'funid': '91'}),
    url(r'^get_client_info/$', get_client_info),
    url(r'^get_backup_content/$', get_backup_content),
    url(r'^get_schedule_policy/$', get_schedule_policy),
    url(r'^get_storage_policy/$', get_storage_policy),
    url(r'^get_backup_status/$', get_backup_status),

    # 健康度
    url(r'^sla/$', sla, {'funid': '94'}),
    url(r'^get_cv_sla/$', get_cv_sla),

    # 磁盘空间
    url(r'^disk_space/$', disk_space, {'funid': '95'}),
    url(r'^get_disk_space/$', get_disk_space),
    url(r'^get_disk_space_daily/$', get_disk_space_daily),
    url(r'^get_ma_disk_space/$', get_ma_disk_space),
    url(r'^get_kvm_disk_space/$', get_kvm_disk_space),

    #数据库复制运行情况
    url(r'^get_adg_copy_status/$', get_adg_copy_status),
    url(r'^get_mysql_copy_status/$', get_mysql_copy_status),

    # 客户端管理
    url(r'^client_manage/$', client_manage, {'funid': '69'}),
    url(r'^get_client_tree/$', get_client_tree),
    url(r'^clientdel/$', clientdel),
    url(r'^client_move/$', client_move),
    url(r'^client_node_save/$', client_node_save),
    url(r'^get_client_detail/$', get_client_detail),
    url(r'^client_client_save/$', client_client_save),
    url(r'^get_cvinfo/$', get_cvinfo),
    url(r'^client_cv_save/$', client_cv_save),
    url(r'^client_cv_del/$', client_cv_del),
    url(r'^client_cv_get_backup_his/$', client_cv_get_backup_his),
    url(r'^client_cv_recovery/$', client_cv_recovery),
    url(r'^client_cv_get_restore_his/$', client_cv_get_restore_his),
    url(r'^get_cv_process/$', get_cv_process),
    url(r'^get_dbcopyinfo/$', get_dbcopyinfo),
    url(r'^client_dbcopy_save/$', client_dbcopy_save),
    url(r'^client_dbcopy_del/$', client_dbcopy_del),
    url(r'^get_adg_status/$', get_adg_status),
    url(r'^client_dbcopy_get_his/$', client_dbcopy_get_his),
    url(r'^client_dbcopy_mysql_save/$', client_dbcopy_mysql_save),
    url(r'^get_mysql_status/$', get_mysql_status),
    url(r'^get_file_tree/$', get_file_tree),
    url(r'^host_save/$', host_save),
    url(r'^hosts_manage_data/$', hosts_manage_data),
    url(r'^kvm_data/$', kvm_data),
    url(r'^kvm_machine_data/$', kvm_machine_data),
    url(r'^kvm_save/$', kvm_save),
    url(r'^kvm_del/$', kvm_del),
    url(r'^kvm_copy_create/$', kvm_copy_create),
    url(r'^kvm_copy_data/$', kvm_copy_data),
    url(r'^kvm_copy_del/$', kvm_copy_del),
    url(r'^kvm_power_on/$', kvm_power_on),
    url(r'^kvm_start/$', kvm_start),
    url(r'^kvm_destroy/$', kvm_destroy),

    # 虚拟机管理
    url(r'^kvm_manage/$', kvm_manage, {'funid': '118'}),
    url(r'^get_kvm_tree/$', get_kvm_tree),
    url(r'^get_kvm_detail/$', get_kvm_detail),
    url(r'^get_kvm_task_data/$', get_kvm_task_data),
    url(r'^kvm_suspend/$', kvm_suspend),
    url(r'^kvm_resume/$', kvm_resume),
    url(r'^kvm_shutdown/$', kvm_shutdown),
    url(r'^kvm_reboot/$', kvm_reboot),
    url(r'^kvm_delete/$', kvm_delete),
    url(r'^kvm_reboot/$', kvm_reboot),
    url(r'^kvm_clone_save/$', kvm_clone_save),
    url(r'^kvm_destroy/$', kvm_destroy),
    url(r'^kvm_machine_create/$', kvm_machine_create),
    url(r'^kvm_power/$', kvm_power),

    # 模板管理
    url(r'^kvm_template/$', kvm_template, {'funid': '119'}),
    url(r'^kvm_template_data/$', kvm_template_data),
    url(r'^kvm_template_save/$', kvm_template_save),
    url(r'^kvm_template_del/$', kvm_template_del),
    url(r'^get_kvm_template/$', get_kvm_template),

    # 流程管理（新）
    url(r'^workflow/(\d+)/$', workflow, {'funid': '120'}),
    url(r'^workflow_readonly/(\d+)/$', workflow_readonly, {'funid': '120'}),
    url(r'^workflowlist/$', workflowlist, {'funid': '120'}),
    url(r'^get_workflow_tree/$', get_workflow_tree),
    url(r'^get_workflow_detail/$', get_workflow_detail),
    url(r'^workflow_save/$', workflow_save),
    url(r'^workflow_del/$', workflow_del),
    url(r'^workflow_move/$', workflow_move),
    url(r'^workflow_getdata/$', workflow_getdata),
    url(r'^workflow_draw_save/$', workflow_draw_save),
    url(r'^workflow_instance/$', workflow_instance, {'funid': '123'}),
    url(r'^workflow_instance_data/$', workflow_instance_data),
    url(r'^workflow_instance_save/$', workflow_instance_save),
    url(r'^workflow_instance_del/$', workflow_instance_del),
    url(r'^workflow_instance_run/$', workflow_instance_run),
    url(r'^workflow_monitor/(\d+)/$', workflow_monitor, {'funid': '124'}),
    url(r'^workflow_monitor_getdata/$', workflow_monitor_getdata),
    url(r'^workflow_job/$', workflow_job, {'funid': '124'}),
    url(r'^workflow_job_data/$', workflow_job_data),
    url(r'^workflow_job_del/$', workflow_job_del),
    url(r'^workflow_monitor_stop/$', workflow_monitor_stop),
    url(r'^workflow_monitor_pause/$', workflow_monitor_pause),
    url(r'^workflow_monitor_retry/$', workflow_monitor_retry),
    url(r'^workflow_monitor_skip/$', workflow_monitor_skip),
]
