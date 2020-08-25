function inArray(search, array) {
    for (var i in array) {
        if (JSON.stringify(array[i]) == JSON.stringify(search)) {
            return true;
        }
    }
    return false;
}

function displayAgentParams(agent_type) {
    if (agent_type.indexOf("Oracle") != -1) {
        $('#cv_orcl').show();
        $('#cv_filesystem').hide();
        $('#cv_mssql').hide();
        $('#cv_select_file').hide();
    } else if (agent_type.indexOf("File System") != -1) {
        $('#cv_orcl').hide();
        $('#cv_filesystem').show();
        $('#cv_mssql').hide();
        $('#cv_select_file').show();
    } else if (agent_type.indexOf("SQL Server") != -1) {
        $('#cv_orcl').hide();
        $('#cv_filesystem').hide();
        $('#cv_mssql').show();
        $('#cv_select_file').hide();
    }
}


//主机
function getClientree() {
    $.ajax({
        type: 'POST',
        dataType: 'json',
        url: '../get_client_tree/',
        data: {
            'id': $("#id").val(),
        },
        success: function (data) {
            if (data.ret == 0) {
                alert(data.data)
            }
            else {
                $('#tree_client').jstree({
                    'core': {
                        "themes": {
                            "responsive": false
                        },
                        "check_callback": true,
                        'data': data.data
                    },

                    "types": {
                        "NODE": {
                            "icon": false
                        },
                        "CLIENT": {
                            "icon": false
                        }
                    },
                    "contextmenu": {
                        "items": {
                            "create": null,
                            "rename": null,
                            "remove": null,
                            "ccp": null,
                            "新建节点": {
                                "label": "新建节点",
                                "action": function (data) {
                                    var inst = jQuery.jstree.reference(data.reference),
                                        obj = inst.get_node(data.reference);
                                    if (obj.type == "CLIENT") {
                                        alert("无法在客户端下新建节点。");
                                    } else {
                                        $("#title").text("新建");
                                        $("#id").val("0");
                                        $("#pid").val(obj.id);
                                        $("#my_type").val("NODE");
                                        $("#node_name").val("");
                                        $("#node_pname").val(obj.data["name"]);
                                        $("#node_remark").val("");

                                        $("#client").hide();
                                        $("#node").show();
                                        $("#node_save").show()
                                        $("#client_save").hide()
                                    }
                                }
                            },
                            "新建客户端": {
                                "label": "新建客户端",
                                "action": function (data) {
                                    var inst = jQuery.jstree.reference(data.reference),
                                        obj = inst.get_node(data.reference);
                                    if (obj.type == "CLIENT") {
                                        alert("无法在客户端下新建客户端。");
                                    } else {
                                        $('#tabcheck2').attr("style", "color: #cbd5dd");
                                        $("#tabcheck2").parent().attr("style", "pointer-events:none;");
                                        $('#tabcheck3').attr("style", "color: #cbd5dd");
                                        $("#tabcheck3").parent().attr("style", "pointer-events:none;");
                                        $("#tabcheck1").click();
                                        $("#title").text("新建")
                                        $("#pname").val(obj.data["name"])
                                        $("#id").val("0");
                                        $("#pid").val(obj.id);
                                        $("#my_type").val("CLIENT");
                                        $("#host_ip").val("");
                                        $("#host_name").val("");
                                        $("#os").val("");
                                        $("#username").val("");
                                        $("#password").val("");
                                        $("#remark").val("");
                                        $('#param_se').empty();

                                        $("#client").show()
                                        $("#node").hide()
                                        $("#node_save").hide()
                                        $("#client_save").show()
                                    }
                                }
                            },
                            "删除": {
                                "label": "删除",
                                "action": function (data) {
                                    var inst = jQuery.jstree.reference(data.reference),
                                        obj = inst.get_node(data.reference);
                                    if (obj.children.length > 0)
                                        alert("节点下还有其他节点或客户端，无法删除。");
                                    else {
                                        if (confirm("确定要删除？删除后不可恢复。")) {
                                            $.ajax({
                                                type: "POST",
                                                url: "../clientdel/",
                                                data:
                                                {
                                                    id: obj.id,
                                                },
                                                success: function (data) {
                                                    if (data == 1) {
                                                        inst.delete_node(obj);
                                                        alert("删除成功！");
                                                    } else
                                                        alert("删除失败，请于管理员联系。");
                                                },
                                                error: function (e) {
                                                    alert("删除失败，请于管理员联系。");
                                                }
                                            });
                                        }
                                    }
                                }
                            },

                        }
                    },
                    "plugins": ["contextmenu", "dnd", "types", "role"]
                })
                    .on('move_node.jstree', function (e, data) {
                        var moveid = data.node.id;
                        if (data.old_parent == "#") {
                            alert("根节点禁止移动。");
                            location.reload()
                        } else {
                            if (data.parent == "#") {
                                alert("禁止新建根节点。");
                                location.reload()
                            } else {
                                $.ajax({
                                    type: "POST",
                                    url: "../client_move/",
                                    data:
                                    {
                                        id: data.node.id,
                                        parent: data.parent,
                                        old_parent: data.old_parent,
                                        position: data.position,
                                        old_position: data.old_position,
                                    },
                                    success: function (data) {
                                        if (data == "重名") {
                                            alert("目标节点下存在重名。");
                                            location.reload()
                                        } else {
                                            if (data == "客户端") {
                                                alert("不能移动至客户端下。");
                                                location.reload()
                                            } else {
                                                if (data != "0") {
                                                    if (selectid == moveid) {
                                                        var res = data.split('^')
                                                        $("#pid").val(res[1])
                                                        $("#pname").val(res[0])
                                                        $("#node_pname").val(res[0])
                                                    }
                                                }
                                            }
                                        }
                                    },
                                    error: function (e) {
                                        alert("移动失败，请于管理员联系。");
                                        location.reload()
                                    }
                                });


                            }
                        }
                    })
                    .bind('select_node.jstree', function (event, data) {
                        $("#form_div").show();
                        var type = data.node.original.type;

                        $("#id").val(data.node.id);
                        $("#pid").val(data.node.parent);
                        $("#my_type").val(type);
                        $("#title").text(data.node.data.name);

                        if (type == "CLIENT") {
                            $("#tabcheck1").click();
                            $.ajax({
                                type: "POST",
                                dataType: 'json',
                                url: "../get_client_detail/",
                                data: {
                                    id: data.node.id,
                                },
                                success: function (data) {
                                    if (data.ret == 1) {
                                        //基础信息
                                        $("#host_ip").val(data.data.host_ip);
                                        $("#host_name").val(data.data.host_name);
                                        $("#os").val(data.data.os);
                                        $("#username").val(data.data.username);
                                        $("#password").val(data.data.password);
                                        $("#remark").val(data.data.remark);
                                        // 动态参数
                                        $('#param_se').empty();
                                        var variable_param_list = data.data.variable_param_list;
                                        for (var i = 0; i < variable_param_list.length; i++) {
                                            $('#param_se').append('<option value="' + variable_param_list[i].variable_name + '">' + variable_param_list[i].param_name + ':' + variable_param_list[i].variable_name + ':' + variable_param_list[i].param_value + '</option>');
                                        }

                                        //cv信息
                                        if (JSON.stringify(data.cvinfo) != '{}') {
                                            $("#tabcheck2_1").click();
                                            $("#div_creatcv").hide();
                                            $("#div_cv").show();
                                            $("#cv_del").show();
                                            $("#cv_id").val(data.cvinfo.id);
                                            $("#cvclient_type").val(data.cvinfo.type);
                                            if ($("#cvclient_type").val() == "2") {
                                                $("#sourcediv").hide();
                                            }
                                            else {
                                                $("#sourcediv").show();
                                            }
                                            $("#cvclient_utils_manage").val(data.cvinfo.utils_id);
                                            getCvClient();
                                            getCvDestination();
                                            $("#cvclient_source").val(data.cvinfo.client_id);
                                            getCvAgenttype();
                                            $("#cvclient_agentType").val(data.cvinfo.agentType);
                                            getCvInstance()
                                            $("#cvclient_instance").val(data.cvinfo.instanceName);
                                            if (data.cvinfo.destination_id == data.cvinfo.id) {
                                                $("#cvclient_destination").val('self');
                                            }
                                            else {
                                                $("#cvclient_destination").val(data.cvinfo.destination_id);
                                            }

                                            // oracle
                                            $("#cvclient_copy_priority").val(data.cvinfo.copy_priority);
                                            $("#cvclient_db_open").val(data.cvinfo.db_open);
                                            $("#cvclient_log_restore").val(data.cvinfo.log_restore);
                                            $("#cvclient_data_path").val(data.cvinfo.data_path);
                                            // File System
                                            var overWrite = data.cvinfo.overWrite;
                                            var destPath = data.cvinfo.destPath;
                                            var sourcePaths = data.cvinfo.sourcePaths;
                                            if (overWrite == "True") {
                                                $('input[name="cv_overwrite"]:last').prop("checked", true);
                                            } else {
                                                $('input[name="cv_overwrite"]:first').prop("checked", true);
                                            }

                                            if (destPath == "same") {
                                                $('input[name="cv_path"]:first').prop("checked", true);
                                            } else {
                                                $('input[name="cv_path"]:last').prop("checked", true);
                                                $('#cv_mypath').val(destPath);
                                            }

                                            $('#cv_fs_se_1').empty();
                                            for (var i = 0; i < sourcePaths.length; i++) {
                                                $('#cv_fs_se_1').append("<option value='" + sourcePaths[i] + "'>" + sourcePaths[i] + "</option>");
                                            }
                                            // 加载tree
                                            try {
                                                if ($('#cvclient_agentType').val().indexOf("File System") != -1) {
                                                    getFileTree();
                                                    if ($('#cvclient_type').val() == 2) { // 目标端
                                                        $('#cv_select_file').hide();
                                                    } else {
                                                        $('#cv_select_file').show();
                                                    }
                                                }
                                            } catch (e) { }

                                            // SQL Server
                                            var mssqlOverWrite = data.cvinfo.mssqlOverWrite;
                                            if (mssqlOverWrite == "False") {
                                                $('#cv_isoverwrite').prop("checked", false);
                                            } else {
                                                $('#cv_isoverwrite').prop("checked", true);
                                            }

                                            get_cv_detail();
                                            if ($("#cvclient_type").val() == "1" || $("#cvclient_type").val() == "3") {
                                                $("#tabcheck2_2").parent().show();
                                                $("#tabcheck2_3").parent().show();
                                                $("#tabcheck2_4").parent().show();
                                            } else {
                                                $("#tabcheck2_2").parent().hide();
                                                $("#tabcheck2_3").parent().hide();
                                                $("#tabcheck2_4").parent().hide();
                                            }

                                            // 应用类型 -> 参数展示
                                            displayAgentParams(data.cvinfo.agentType);
                                        }
                                        else {
                                            $("#div_creatcv").show();
                                            $("#div_cv").hide();
                                            $("#cv_del").hide();
                                        }

                                        //dbcopy信息
                                        if (JSON.stringify(data.dbcopyinfo) != '{}') {
                                            $("#dbcopy_dbtype").prop("disabled", "disabled");
                                            $("#tabcheck3_1").click();
                                            $("#div_creatdbcopy").hide();
                                            $("#div_dbcopy").show();
                                            $("#dbcopy_id").val(data.dbcopyinfo.id);
                                            $("#dbcopy_dbtype").val(data.dbcopyinfo.dbtype);
                                            $("#dbcopy_hosttype").val(data.dbcopyinfo.hosttype);
                                            //oracle
                                            if ($("#dbcopy_dbtype").val() == "1") {
                                                $("#mysqldiv").hide();
                                                $("#oraclediv").show();
                                                $("#dbcopy_oracle_del").show();
                                                $("#dbcopy_oracleusername").val(data.dbcopyinfo.dbusername);
                                                $("#dbcopy_oraclepassword").val(data.dbcopyinfo.dbpassowrd);
                                                $("#dbcopy_oracleinstance").val(data.dbcopyinfo.dbinstance);
                                                if (data.dbcopyinfo.std_id != null) {
                                                    $("#dbcopy_std").val(data.dbcopyinfo.std_id);
                                                } else {
                                                    $("#dbcopy_std").val("none");
                                                }
                                                if ($("#dbcopy_hosttype").val() == "1") {
                                                    $("#dbcopy_std_div").show();
                                                    $("#tabcheck3_2").parent().show();
                                                    $("#tabcheck3_3").parent().show();
                                                    get_dbcopy_oracle_detail();
                                                } else {
                                                    $("#dbcopy_std_div").hide();
                                                    $("#tabcheck3_2").parent().hide();
                                                    $("#tabcheck3_3").parent().hide();
                                                }
                                            }
                                            else {
                                                $("#dbcopy_oracleusername").val("");
                                                $("#dbcopy_oraclepassword").val("");
                                                $("#dbcopy_oracleinstance").val("");
                                                $("#dbcopy_std").val("none");
                                            }
                                            //mysql
                                            if ($("#dbcopy_dbtype").val() == "2") {
                                                $("#mysqldiv").show();
                                                $("#oraclediv").hide();
                                                $("#dbcopy_mysql_del").show();
                                                $("#dbcopy_mysqlusername").val(data.dbcopyinfo.dbusername);
                                                $("#dbcopy_mysqlpassword").val(data.dbcopyinfo.dbpassowrd);
                                                $("#dbcopy_mysqlcopyusername").val(data.dbcopyinfo.copyusername);
                                                $("#dbcopy_mysqlcopypassword").val(data.dbcopyinfo.copypassowrd);
                                                $("#dbcopy_mysqlbinlog").val(data.dbcopyinfo.binlog);
                                                $("#dbcopy_mysql_std").val(data.dbcopyinfo.std_id);
                                                $("#dbcopy_mysql_std").select2({
                                                    width: null
                                                });

                                                if ($("#dbcopy_hosttype").val() == "1") {
                                                    $("#dbcopy_mysql_std_div").show();
                                                    $("#tabcheck3_2").parent().show();
                                                    $("#tabcheck3_3").parent().show();
                                                    get_dbcopy_mysql_detail();
                                                } else {
                                                    $("#dbcopy_mysql_std_div").hide();
                                                    $("#tabcheck3_2").parent().hide();
                                                    $("#tabcheck3_3").parent().hide();
                                                }
                                            }
                                        }
                                        else {
                                            $("#div_creatdbcopy").show();
                                            $("#div_dbcopy").hide();
                                        }

                                        //kvm信息
                                        if (JSON.stringify(data.kvminfo) != '{}') {
                                            $("#tabcheck4_1").click();
                                            $("#div_creatkvm").hide();
                                            $("#div_kvm").show();
                                            $("#kvm_del").show();
                                            $("#kvm_id").val(data.cvinfo.id);

                                            $("#kvm_machine_platform").val(data.kvminfo.utils_id);
                                            $("#kvm_machine").val(data.kvminfo.name);
                                            $("#kvm_filesystem").val(data.kvminfo.filesystem);


                                            //get_kvm_detail();
                                            $("#tabcheck4_1").parent().show();
                                            $("#tabcheck4_2").parent().show();
                                            $("#tabcheck3_3").parent().show();
                                        }
                                        else {
                                            $("#div_creatkvm").show();
                                            $("#div_kvm").hide();
                                            $("#kvm_del").hide();
                                        }
                                    }
                                    else {
                                        $("#host_id").val("0");
                                        $("#host_ip").val("");
                                        $("#host_name").val("");
                                        $("#os").val("");
                                        $("#username").val("");
                                        $("#password").val("");
                                        $("#remark").val("");
                                        $('#param_se').empty();
                                        alert(data.info);
                                    }
                                },
                                error: function (e) {
                                    alert("页面出现错误，请于管理员联系。");
                                }
                            });
                            $("#client").show()
                            $("#node").hide()
                        }
                        if (type == "NODE") {
                            $("#node_pname").val(data.node.data.pname)
                            $("#node_name").val(data.node.data.name)
                            $("#node_remark").val(data.node.data.remark)
                            $("#client").hide()
                            $("#node").show()
                        }
                        if (data.node.id == "1" || data.node.id == "2" || data.node.id == "3") {
                            $("#node_save").hide()
                            $("#client_save").hide()
                        } else {
                            $("#node_save").show()
                            $("#client_save").show()
                        }
                    });
            }
        }
    });
}

//commvault
function get_cv_detail() {
    var table = $('#cv_backup_his').DataTable();
    table.ajax.url("../client_cv_get_backup_his?id=" + $('#cv_id').val()
    ).load();
    // 目标客户端
    var dest_client = $('#cvclient_destination').val();
    if (dest_client == "self") {
        dest_client = $('#cv_id').val();
    }
    var table1 = $('#cv_restore_his').DataTable();
    table1.ajax.url("../client_cv_get_restore_his?id=" + dest_client
    ).load();

    $('#cv_r_sourceClient').val($("#cvclient_source").find("option:selected").text());
    $('#cv_r_destClient').val($('#cvclient_destination').val());

    // Oracle
    $('#cv_r_copy_priority').val($('#cvclient_copy_priority').val());
    $('#cv_r_db_open').val($('#cvclient_db_open').val());
    $('#cv_r_log_restore').val($('#cvclient_log_restore').val());
    $('#cv_r_data_path').val($('#cvclient_data_path').val());

    // SQL Server
    if ($('#cv_isoverwrite').is(':checked')) {
        $('#cv_r_isoverwrite').prop("checked", true);
    } else {
        $('#cv_r_isoverwrite').prop("checked", false);
    }

    // File System
    // cv_overwrite cv_path  cv_mypath cv_fs_se_1
    // cv_r_overwrite cv_r_path cv_r_mypath cv_r_fs_se_1
    var cv_overwrite = $('input[name="cv_overwrite"]:checked').val();
    if (cv_overwrite == "TRUE") {
        $('input[name="cv_r_overwrite"]:last').prop("checked", true);
    } else {
        $('input[name="cv_r_overwrite"]:first').prop("checked", true);
    }
    var cv_path = $('input[name="cv_path"]:checked').val();
    var cv_mypath = $('#cv_mypath').val();
    if (cv_path == 1) {  // 相同文件
        $('input[name="cv_r_path"]:first').prop("checked", true);
    } else {
        $('input[name="cv_r_path"]:last').prop("checked", true);
        $('#cv_r_mypath').val(cv_mypath);
    }
    var cv_fs_se_1 = $('#cv_fs_se_1').html();
    $('#cv_r_fs_se_1').empty().append(cv_fs_se_1);
}

function getCvInstance() {
    $("#cvclient_instance").empty();
    try {
        var clientdata = JSON.parse($("#cvclient_client_info").val());
        var instancelist = [];
        for (var i = 0; i < clientdata.length; i++) {
            if (clientdata[i].clientid == $("#cvclient_source").val() && clientdata[i].agent == $("#cvclient_agentType").val()) {
                if (instancelist.indexOf(clientdata[i].instance) == -1) {
                    instancelist.push(clientdata[i].instance);
                }
            }
        }
        for (var i = 0; i < instancelist.length; i++) {
            $("#cvclient_instance").append('<option value="' + instancelist[i] + '">' + instancelist[i] + '</option>');
        }
    } catch (e){
        console.log(e)
    }

}

function getCvAgenttype() {
    $("#cvclient_agentType").empty();
    try {
        var clientdata = JSON.parse($("#cvclient_client_info").val());
        var agentlist = [];
        for (var i = 0; i < clientdata.length; i++) {
            if (clientdata[i].clientid == $("#cvclient_source").val()) {
                if (agentlist.indexOf(clientdata[i].agent) == -1) {
                    agentlist.push(clientdata[i].agent);
                }
            }
        }
        for (var i = 0; i < agentlist.length; i++) {
            $("#cvclient_agentType").append('<option value="' + agentlist[i] + '">' + agentlist[i] + '</option>');
        }
    } catch (e){
        console.log(e)
    }

    getCvInstance();
}

function getCvClient() {
    $("#cvclient_source").empty();
    var utildata = JSON.parse($("#cvclient_utils_manage_info").val());
    for (var i = 0; i < utildata.length; i++) {
        if (utildata[i].utils_manage == $("#cvclient_utils_manage").val()) {
            var clientlist = [];
            for (var j = 0; j < utildata[i].instance_list.length; j++) {
                var client = { "clientid": utildata[i].instance_list[j].clientid, "clientname": utildata[i].instance_list[j].clientname };
                if (!inArray(client, clientlist)) {
                    clientlist.push(client);
                }
            }
            for (var j = 0; j < clientlist.length; j++) {
                $("#cvclient_source").append('<option value="' + clientlist[j].clientid + '">' + clientlist[j].clientname + '</option>');
            }
            $("#cvclient_client_info").val(JSON.stringify(utildata[i].instance_list))
            break;
        }
    }
    getCvAgenttype();
}

function getCvDestination() {
    $("#cvclient_destination").empty();
    $("#cv_r_destClient").empty();

    var destinationdata = JSON.parse($("#cvclient_u_destination").val());
    for (var i = 0; i < destinationdata.length; i++) {
        if (destinationdata[i].utilid == $("#cvclient_utils_manage").val()) {
            for (var j = 0; j < destinationdata[i].destination_list.length; j++) {
                $("#cvclient_destination").append('<option value="' + destinationdata[i].destination_list[j].id + '">' + destinationdata[i].destination_list[j].name + '</option>');
                $("#cv_r_destClient").append('<option value="' + destinationdata[i].destination_list[j].id + '">' + destinationdata[i].destination_list[j].name + '</option>');
            }
            break;
        }
    }
    $("#cvclient_destination").append('<option value="self">' + "本机" + '</option>');
    $("#cv_r_destClient").append('<option value="self">' + "本机" + '</option>');
}

function getCvinfo() {
    $.ajax({
        type: 'POST',
        dataType: 'json',
        url: '../get_cvinfo/',
        success: function (data) {
            for (var i = 0; i < data.u_destination.length; i++) {
                $("#cvclient_utils_manage").append('<option value="' + data.u_destination[i].utilid + '">' + data.u_destination[i].utilname + '</option>');
            }
            $("#cvclient_utils_manage_info").val(JSON.stringify(data.data))
            $("#cvclient_u_destination").val(JSON.stringify(data.u_destination))
            getCvClient();
            getCvDestination();
            $('#loading').hide();
            $('#showdata').show();
        }
    });

}

function getFileTree() {
    var setting = {
        async: {
            enable: true,
            url: '../get_file_tree/',
            autoParam: ["id"],
            otherParam: { "cv_id": $('#cv_id').val() },
            dataFilter: filter
        },
        check: {
            enable: true,
            chkStyle: "checkbox",               //多选
            chkboxType: { "Y": "s", "N": "ps" }  //不级联父节点选择
        },
        view: {
            showLine: false
        },

    };

    function filter(treeId, parentNode, childNodes) {
        if (!childNodes) return null;
        for (var i = 0, l = childNodes.length; i < l; i++) {
            childNodes[i].name = childNodes[i].name.replace(/\.n/g, '.');
        }
        return childNodes;
    }

    $.fn.zTree.init($("#cv_fs_tree"), setting);
}
//数据库复制
function get_dbcopy_oracle_detail() {
    var table = $('#dbcopy_his').DataTable();
    table.ajax.url("../client_dbcopy_get_his?id=" + $('#id').val() + "&type=ADG"
    ).load();
    $('#adgstate_div').show();
    $('#mysqlstate_div').hide();
    $.ajax({
        type: "POST",
        dataType: 'json',
        url: "../get_adg_status/",
        data:
        {
            id: $("#id").val(),
            dbcopy_id: $("#dbcopy_id").val(),
            dbcopy_std: $("#dbcopy_std").val(),
        },
        success: function (data) {
            $(".ldbimg").attr("src", "/static/pages/images/adg/db3.png");
            $(".rdbimg").attr("src", "/static/pages/images/adg/db3.png");
            $(".sync").attr("src", "/static/pages/images/adg/sync_r.png");
            //数据库状态
            l_host_name = data["data"][0].host_name;
            l_db_status = data["data"][0].db_status;
            l_switchover_status = data["data"][0].switchover_status;

            r_host_name = data["data"][1].host_name;
            r_db_status = data["data"][1].db_status;
            r_switchover_status = data["data"][1].switchover_status;
            $(".ldbname").text(l_host_name);
            $(".ldbsta").text(l_db_status);
            $(".rdbname").text(r_host_name);
            $(".rdbsta").text(r_db_status);

            if (l_db_status == "OPEN") {
                $(".ldbimg").attr("src", "/static/pages/images/adg/db1.png");
            }
            if (l_db_status == "READ ONLY WITH APPLY") {
                $(".ldbimg").attr("src", "/static/pages/images/adg/db1.png");
            }
            if (l_db_status == "READ WRITE") {
                $(".ldbimg").attr("src", "/static/pages/images/adg/db1.png");
            }
            if (l_db_status == "READ ONLY") {
                $(".ldbimg").attr("src", "/static/pages/images/adg/db1.png");
            }
            if (l_db_status == "MOUNT") {
                $(".ldbimg").attr("src", "/static/pages/images/adg/db2.png");
            }
            if (r_db_status == "OPEN") {
                $(".rdbimg").attr("src", "/static/pages/images/adg/db1.png");
            }
            if (r_db_status == "READ ONLY WITH APPLY") {
                $(".rdbimg").attr("src", "/static/pages/images/adg/db1.png");
            }
            if (r_db_status == "READ WRITE") {
                $(".rdbimg").attr("src", "/static/pages/images/adg/db1.png");
            }
            if (r_db_status == "MOUNT") {
                $(".rdbimg").attr("src", "/static/pages/images/adg/db2.png");
            }
            if (r_db_status == "READ ONLY") {
                $(".rdbimg").attr("src", "/static/pages/images/adg/db1.png");
            }
            if (l_switchover_status == "PRIMARY") {
                $(".sync").attr("src", "/static/pages/images/adg/sync_r.gif");
            }
            if (r_switchover_status == "PRIMARY") {
                $(".sync").attr("src", "/static/pages/images/adg/sync_l.gif");
            }
            //流程
            var processtext = ""
            for (var i = 0; i < data["process"].length; i++) {
                processtext += "<div  class='form-group'><button onclick=\"runprocess(" + data["process"][i].process_id + ",'1')\"  type='button' class=' btn  green'>切换:" + data["process"][i].process_name + "</button> ";
                if (data["process"][i].back_id != null && data["process"][i].back_id != "") {
                    processtext += "<button onclick=\"runprocess(" + data["process"][i].process_id + ",'2')\" type='button' class='backprocessbtn btn  green'>回切</button>";
                }
                processtext += "</div>"
            }
            $("#processdiv").empty();
            $("#processdiv").append(processtext);
        },
        error: function (e) {
            ;
        }
    });
}
function get_dbcopy_mysql_detail() {
    var table = $('#dbcopy_his').DataTable();
    table.ajax.url("../client_dbcopy_get_his?id=" + $('#id').val() + "&type=MYSQL"
    ).load();
    $('#adgstate_div').hide();
    $('#mysqlstate_div').show();
    $.ajax({
        type: "POST",
        dataType: 'json',
        url: "../get_mysql_status/",
        data:
        {
            id: $("#id").val(),
            dbcopy_id: $("#dbcopy_id").val(),
            dbcopy_mysql_std: JSON.stringify($("#dbcopy_mysql_std").val()),
        },
        success: function (data) {
            //数据库状态
            $(".mysqlcount").hide();
            $(".mysqlsync").hide();
            $(".mysqlsync").attr("src", "/static/pages/images/adg/sync_r.png");
            $(".mysqlhost").attr("src", "/static/pages/images/adg/db3.png");
            $(".mysqltest").text("")
            var hostcount = data["data"].length;
            $("#mysql_count_" + hostcount.toString()).show();
            if (hostcount > 4) {
                $("#mysql_count_4").show();
            }
            for (var i = 0; i < data["data"].length; i++) {
                num = data["data"][i].num;
                conn_status = data["data"][i].conn_status;
                host_name = data["data"][i].host_name;
                host_ip = data["data"][i].host_ip;
                io_state = data["data"][i].io_state;
                sql_state = data["data"][i].sql_state;
                masternum = data["data"][i].masternum;

                $("#dbhost_" + hostcount.toString() + "_" + num.toString()).text(host_name);
                $("#dbip_" + hostcount.toString() + "_" + num.toString()).text(host_ip);
                if (conn_status == 1) {
                    $("#mysqlimg_" + hostcount.toString() + "_" + num.toString()).attr("src", "/static/pages/images/adg/db1.png");
                }
                $("#sync_" + hostcount.toString() + "_" + masternum.toString() + "_" + num.toString()).show();
                if (io_state == "Yes" && sql_state == "Yes") {
                    $("#sync_" + hostcount.toString() + "_" + masternum.toString() + "_" + num.toString()).attr("src", "/static/pages/images/adg/sync_r.gif");
                }

            }

            //流程
            var processtext = ""
            for (var i = 0; i < data["process"].length; i++) {
                processtext += "<div  class='form-group'><button onclick=\"runprocess(" + data["process"][i].process_id + ",'1')\"  type='button' class=' btn  green'>切换:" + data["process"][i].process_name + "</button> ";
                if (data["process"][i].back_id != null && data["process"][i].back_id != "") {
                    processtext += "<button onclick=\"runprocess(" + data["process"][i].process_id + ",'2')\" type='button' class='backprocessbtn btn  green'>回切</button>";
                }
                processtext += "</div>"
            }
            $("#processdiv").empty();
            $("#processdiv").append(processtext);
        },
        error: function (e) {
            ;
        }
    });
}

function getDbcopyStd() {
    $("#dbcopy_std").empty();

    var stddata = JSON.parse($("#dbcopy_u_std").val());
    for (var i = 0; i < stddata.length; i++) {
        if (stddata[i].type == "1") {
            $("#dbcopy_std").append('<option value="' + stddata[i].id + '">' + stddata[i].name + '</option>');
        }
    }
    $("#dbcopy_std").append('<option value="none">' + "无" + '</option>');
}
function getDbcopyMysqlStd() {
    $("#dbcopy_mysql_std").empty();

    var stddata = JSON.parse($("#dbcopy_u_std").val());
    for (var i = 0; i < stddata.length; i++) {
        if (stddata[i].type == "2") {
            $("#dbcopy_mysql_std").append('<option value="' + stddata[i].id + '">' + stddata[i].name + '</option>');
        }
    }

    $("#dbcopy_mysql_std").select2({
        width: null
    });
}


function getDbcopyinfo() {
    $.ajax({
        type: 'POST',
        dataType: 'json',
        url: '../get_dbcopyinfo/',
        success: function (data) {
            $("#dbcopy_u_std").val(JSON.stringify(data.u_std));
            getDbcopyStd();
            getDbcopyMysqlStd();
        }
    });

}

function runprocess(processid, process_type) {
    $("#static").modal({ backdrop: "static" });
    $('#recovery_time').datetimepicker({
        format: 'yyyy-mm-dd hh:ii:ss',
        pickerPosition: 'top-right'
    });
    // 写入当前时间
    var myDate = new Date();
    $("#run_time").val(myDate.toLocaleString());
    $("#processid").val(processid);
    $("#process_type").val(process_type);
}

//kvm
function kvmFunction() {
        $.ajax({
            type: "POST",
            dataType: 'json',
            url: "../kvm_data/",
            data: {
                utils_kvm_id: $('#kvm_machine_platform').val()
            },
            success: function (data) {
            if (data.ret == 0) {
                alert(data.data)
            } else {
                for (i = 0; i < data.kvm_list.length; i++) {
                    $("#kvm_machine").append('<option value="'+ data.kvm_list[i].name + '">'+ data.kvm_list[i].name + '</option>')
                }
                for (i = 0; i < data.kvm_filesystem_list.length; i++) {
                    $("#kvm_filesystem").append('<option value="'+ data.kvm_filesystem_list[i] + '">'+ data.kvm_filesystem_list[i] + '</option>')
                }

                $("#kvm_machine_platform").val(data.kvm_machine_list[0].utils_id);
                $("#kvm_machine").val(data.kvm_machine_list[0].name);
                $("#kvm_filesystem").val(data.kvm_machine_list[0].filesystem);


                $('#zfs_snapshot').dataTable({
                    "bAutoWidth": true,
                    "bSort": false,
                    "iDisplayLength": 25,
                    "bProcessing": true,
                    "ajax": "../zfs_snapshot_data/?utils_id=" + $('#kvm_machine_platform').val() + "&filesystem=" + $('#kvm_filesystem').val(),
                    "columns": [
                        {"data": "name"},
                        {"data": null}
                    ],

                    "columnDefs": [{
                        "targets": -1,
                        "data": null,
                        "width": "100px",
                        "defaultContent": "<button  id='edit' title='挂载快照' data-toggle='modal'  data-target='#static03'  class='btn btn-xs btn-primary' type='button'><i class='fa fa-edit'></i></button>" +
                            "<button title='删除快照'  id='delrow' class='btn btn-xs btn-primary' type='button'><i class='fa fa-trash-o'></i></button>"
                    }
                    ],
                    "oLanguage": {
                        "sLengthMenu": "每页显示 _MENU_ 条记录",
                        "sZeroRecords": "抱歉， 没有找到",
                        "sInfo": "从 _START_ 到 _END_ /共 _TOTAL_ 条数据",
                        "sInfoEmpty": "没有数据",
                        "sInfoFiltered": "(从 _MAX_ 条数据中检索)",
                        "sSearch": "搜索",
                        "oPaginate": {
                            "sFirst": "首页",
                            "sPrevious": "前一页",
                            "sNext": "后一页",
                            "sLast": "尾页"
                        },
                        "sZeroRecords": "没有检索到数据",
                    },
                });

            }
        }
        });
    }

$(document).ready(function () {
    //主机
    $(".tabbed>ul>li").click(function () {
        var aa = this.firstElementChild;
        aa.click();
    });
    $('#loading').show();
    $('#showdata').hide();

    getClientree();

    $('#node_save').click(function () {
        $.ajax({
            type: "POST",
            dataType: 'json',
            url: "../client_node_save/",
            data: {
                id: $("#id").val(),
                pid: $("#pid").val(),
                node_name: $("#node_name").val(),
                node_remark: $("#node_remark").val(),
            },
            success: function (data) {
                if (data.ret == 1) {
                    if ($("#id").val() == "0") {
                        $('#tree_client').jstree('create_node', $("#pid").val(), {
                            "text": "<i class='jstree-icon jstree-themeicon fa fa-folder icon-state-warning icon-lg jstree-themeicon-custom'></i>" + $("#node_name").val(),
                            "id": data.nodeid,
                            "type": "NODE",
                            "data": { "remark": $("#node_remark").val(), "name": $("#node_name").val(), "pname": $("#pname").val() },
                            "icon": false,
                        }, "last", false, false);
                        $("#id").val(data.nodeid)
                        $('#tree_client').jstree('deselect_all')
                        $('#tree_client').jstree('select_node', $("#id").val(), true)
                    }
                    else {
                        var curnode = $('#tree_client').jstree('get_node', $("#id").val());
                        var newtext = curnode.text.replace(curnode.data["name"], $("#node_name").val())
                        curnode.text = newtext
                        curnode.data["remark"] = $("#node_remark").val()
                        curnode.data["name"] = $("#node_name").val()
                        $('#tree_client').jstree('set_text', $("#id").val(), newtext);
                    }
                }
                alert(data.info);
            },
            error: function (e) {
                alert("页面出现错误，请于管理员联系。");
            }
        });
    });
    $('#client_save').click(function () {
        var params_list = [];

        // 构造参数Map>> Array (动态参数)
        $('#param_se option').each(function () {
            // 构造单个参数信息
            var txt_param_list = $(this).text().split(":");
            var val_param = $(this).prop("value");
            var param_dict = {
                "param_name": txt_param_list[0],
                "variable_name": val_param,
                "param_value": txt_param_list[2]
            };
            params_list.push(param_dict)
        });

        $.ajax({
            type: "POST",
            dataType: 'json',
            url: "../client_client_save/",
            data: {
                id: $("#id").val(),
                pid: $("#pid").val(),
                host_ip: $("#host_ip").val(),
                host_name: $("#host_name").val(),
                os: $("#os").val(),
                username: $("#username").val(),
                password: $("#password").val(),
                remark: $("#remark").val(),
                config: JSON.stringify(params_list)
            },
            success: function (data) {
                if (data.ret == 1) {
                    if ($("#id").val() == "0") {
                        $('#tree_client').jstree('create_node', $("#pid").val(), {
                            "text": $("#host_name").val(),
                            "id": data.nodeid,
                            "type": "CLIENT",
                            "data": { "remark": $("#node_remark").val(), "name": $("#node_name").val(), "pname": $("#pname").val() },
                            "icon": false,
                        }, "last", false, false);
                        $("#id").val(data.nodeid)
                        $('#tree_client').jstree('deselect_all')
                        $('#tree_client').jstree('select_node', $("#id").val(), true)
                        $('#tabcheck2').removeAttr("style", "color: #cbd5dd");
                        $("#tabcheck2").parent().removeAttr("style", "pointer-events:none;");
                        $('#tabcheck3').removeAttr("style", "color: #cbd5dd");
                        $("#tabcheck3").parent().removeAttr("style", "pointer-events:none;");
                    }
                    else {
                        var curnode = $('#tree_client').jstree('get_node', $("#id").val());
                        var newtext = curnode.text.replace(curnode.data["name"], $("#host_name").val())
                        curnode.text = newtext
                        curnode.data["name"] = $("#host_name").val()
                        $('#tree_client').jstree('set_text', $("#id").val(), newtext);
                    }
                    $("#title").val($("#node_name").val())
                }
                alert(data.info);
            },
            error: function (e) {
                alert("页面出现错误，请于管理员联系。");
            }
        });
    });

    $('#param_se').contextmenu({
        target: '#context-menu2',
        onItem: function (context, e) {
            if ($(e.target).text() == "新增") {
                $('#param_operate').val('new');

                // 清空所有子节点
                $('#params').empty();

                // 新增节点
                $("#params").append(
                    '<div class="form-group">' +
                    '<label class="col-md-2 control-label"><span style="color:red; "></span>参数名称</label>' +
                    '<div class="col-md-10">' +
                    '<input id="param_name" type="text" name="param_name" class="form-control" placeholder="">' +
                    '<div class="form-control-focus"></div>' +
                    '</div>' +
                    '</div>' +
                    '<div class="form-group">' +
                    '<label class="col-md-2 control-label"><span style="color:red; "></span>变量设置</label>' +
                    '<div class="col-md-10">' +
                    '<input id="variable_name" type="text" name="variable_name" class="form-control" placeholder="">' +
                    '<div class="form-control-focus"></div>' +
                    '</div>' +
                    '</div>' +
                    '<div class="form-group">' +
                    '<label class="col-md-2 control-label"><span style="color:red; "></span>参数值</label>' +
                    '<div class="col-md-10">' +
                    '<input id="param_value" type="text" name="param_value" class="form-control" placeholder="">' +
                    '<div class="form-control-focus"></div>' +
                    '</div>' +
                    '</div>'
                );

                $("button#param_edit").click();
            }
            if ($(e.target).text() == "修改") {
                $('#param_operate').val('edit');
                if ($("#param_se").find('option:selected').length == 0)
                    alert("请选择要修改的参数。");
                else {
                    if ($("#param_se").find('option:selected').length > 1)
                        alert("修改时请不要选择多条记录。");
                    else {
                        var alpha_param = $("#param_se").val();
                        var params_t = $("#param_se").find('option:selected').text();

                        var params_t_list = params_t.split(":");

                        var txt_param = params_t_list[0];
                        var v_param = params_t_list[2];

                        $("#params").empty();
                        $("#params").append(
                            '<div class="form-group">' +
                            '<label class="col-md-2 control-label"><span style="color:red; "></span>参数名称</label>' +
                            '<div class="col-md-10">' +
                            '<input id="param_name" type="text" name="param_name" value="' + txt_param + '" class="form-control" placeholder="">' +
                            '<div class="form-control-focus"></div>' +
                            '</div>' +
                            '</div>' +
                            '<div class="form-group">' +
                            '<label class="col-md-2 control-label"><span style="color:red; "></span>变量设置</label>' +
                            '<div class="col-md-10">' +
                            '<input id="variable_name" readonly type="text" name="variable_name" value="' + alpha_param + '" class="form-control" placeholder="">' +
                            '<div class="form-control-focus"></div>' +
                            '</div>' +
                            '</div>' +
                            '<div class="form-group">' +
                            '<label class="col-md-2 control-label"><span style="color:red; "></span>参数值</label>' +
                            '<div class="col-md-10">' +
                            '<input id="param_value" type="text" name="param_value" value="' + v_param + '" class="form-control" placeholder="">' +
                            '<div class="form-control-focus"></div>' +
                            '</div>' +
                            '</div>'
                        );
                        $("button#param_edit").click();
                    }
                }

            }
            if ($(e.target).text() == "删除") {
                $('#param_operate').val('delete');
                if ($("#param_se").find('option:selected').length == 0)
                    alert("请选择要删除的参数。");
                else {
                    if (confirm("确定要删除该参数吗？")) {
                        $("#param_se").find('option:selected').remove();
                    }
                }
            }
        }
    });
    $('#params_save').click(function () {
        var param_operate = $('#param_operate').val();
        var param_name = $('#param_name').val();
        var variable_name = $('#variable_name').val();
        var param_value = $('#param_value').val();

        if (param_operate == "new") {
            $('#param_se').append('<option value="' + variable_name + '">' + param_name + ':' + variable_name + ':' + param_value + '</option>');
        }
        if (param_operate == "edit") {
            // 指定value的option修改text
            $('#param_se option[value="' + variable_name + '"]').text(param_name + ':' + variable_name + ':' + param_value);
        }
        $("#static01").modal("hide");
    });

    //cv
    getCvinfo();
    $('#creatcv').click(function () {  // 创建commvault保护
        $("#div_creatcv").hide();
        $("#div_cv").show();
        $("#cv_del").hide();
        $("#tabcheck2_1").click();
        $("#tabcheck2_2").parent().hide();
        $("#tabcheck2_3").parent().hide();
        $("#tabcheck2_4").parent().hide();

        $("#cv_id").val("0");
        $("#cvclient_type").val("1");

        /**
         * 创建commvault保护时
         * 新建要清除目录
         * 新建要隐藏选择目录按钮
         * 新建要清除树
         */
        $('#cv_select_file').hide();
        try {
            $.fn.zTree.getZTreeObj("cv_fs_tree").destroy();
        } catch(e){}
        $('#cv_fs_se_1').empty();
        $('#cvclient_agentType').change();  // 主从触发更改操作
    });

    $("#cvclient_utils_manage").change(function () {
        getCvClient();
        getCvDestination();
        // 应用类型 -> 参数展示
        var cv_agent = $('#cvclient_agentType').val();
        displayAgentParams(cv_agent);
    });
    $("#cvclient_source").change(function () {
        getCvAgenttype();
        // 应用类型 -> 参数展示
        var cv_agent = $('#cvclient_agentType').val();
        displayAgentParams(cv_agent);
    });
    $("#cvclient_agentType").change(function () {
        getCvInstance();

        var cv_agent = $(this).val();
        console.log(cv_agent);
        // 应用类型 -> 参数展示
        displayAgentParams(cv_agent);
    });
    $("#cvclient_type").change(function () {
        if ($("#cvclient_type").val() == "2") {
            $("#sourcediv").hide();
        }
        else {
            $("#sourcediv").show();
        }
    });

    $('#cv_save').click(function () {
        var cv_iscover = $("input[name='cv_overwrite']:checked").val();
        var cv_mypath = "same"
        if ($("input[name='cv_path']:checked").val() == "2") {
            cv_mypath = $('#cv_mypath').val()
        }
        var cv_selectedfile = ""
        $("#cv_fs_se_1 option").each(function () {
            var txt = $(this).val();
            cv_selectedfile = cv_selectedfile + txt + "*!-!*"
        });
        var mssql_iscover = "FALSE"
        if ($('#cv_isoverwrite').is(':checked')) {
            mssql_iscover = "TRUE"
        }
        $.ajax({
            type: "POST",
            dataType: 'json',
            url: "../client_cv_save/",
            data: {
                id: $("#id").val(),
                cv_id: $("#cv_id").val(),
                cvclient_type: $("#cvclient_type").val(),
                cvclient_utils_manage: $("#cvclient_utils_manage").val(),
                cvclient_source: $("#cvclient_source").val(),
                cvclient_clientname: $("#cvclient_source").find("option:selected").text(),
                cvclient_agentType: $("#cvclient_agentType").val(),
                cvclient_instance: $("#cvclient_instance").val(),
                cvclient_destination: $("#cvclient_destination").val(),

                // Oracle
                cvclient_copy_priority: $("#cvclient_copy_priority").val(),
                cvclient_db_open: $("#cvclient_db_open").val(),
                cvclient_log_restore: $("#cvclient_log_restore").val(),
                cvclient_data_path: $("#cvclient_data_path").val(),

                // File System
                cv_iscover: cv_iscover,
                cv_mypath: cv_mypath,
                cv_selectedfile: cv_selectedfile,

                // SQL Server
                mssql_iscover: mssql_iscover
            },
            success: function (data) {
                if (data.ret == 1) {
                    if ($("#cv_id").val() == "0") {
                        $("#cv_id").val(data.cv_id);
                        $("#cv_del").show();
                        if ($("#cvclient_type").val() == "1" || $("#cvclient_type").val() == "3") {
                            $("#tabcheck2_2").parent().show();
                            $("#tabcheck2_3").parent().show();
                            $("#tabcheck2_4").parent().show();
                        }
                        else {
                            $("#tabcheck2_2").parent().hide();
                            $("#tabcheck2_3").parent().hide();
                            $("#tabcheck2_4").parent().hide();
                        }
                        var curnode = $('#tree_client').jstree('get_node', $("#id").val());
                        var newtext = "<img src = '/static/pages/images/cv.png' height='24px'> " + curnode.text
                        $('#tree_client').jstree('set_text', $("#id").val(), newtext);
                    }
                    if ($("#cvclient_type").val() == "2" || $("#cvclient_type").val() == "3") {
                        var destinationdata = JSON.parse($("#cvclient_u_destination").val());
                        for (var i = 0; i < destinationdata.length; i++) {
                            if (destinationdata[i].utilid == $("#cvclient_utils_manage").val()) {
                                var cur_destination = { "name": $("#cvclient_source").find("option:selected").text(), "id": data.cv_id }
                                if (!inArray(cur_destination, destinationdata[i].destination_list)) {
                                    destinationdata[i].destination_list.push(cur_destination);
                                    $("#cvclient_u_destination").val(JSON.stringify(destinationdata));
                                    $("#cvclient_destination").append('<option value="' + data.cv_id + '">' + $("#cvclient_source").find("option:selected").text() + '</option>');
                                    $("#cv_r_destClient").append('<option value="' + data.cv_id + '">' + $("#cvclient_source").find("option:selected").text() + '</option>');
                                }
                                break;
                            }
                        }
                    }
                    get_cv_detail();
                    // 加载tree
                    try {
                        if ($('#cvclient_agentType').val().indexOf("File System") != -1) {
                            getFileTree();
                            if ($('#cvclient_type').val() == 2) { // 目标端
                                $('#cv_select_file').hide();
                            } else {
                                $('#cv_select_file').show();
                            }
                        }
                    } catch (e) { }
                }
                alert(data.info);
            },
            error: function (e) {
                alert("页面出现错误，请于管理员联系。");
            }
        });
    });
    $('#cv_del').click(function () {
        if (confirm("确定要删除？删除后不可恢复。")) {
            $.ajax({
                type: "POST",
                url: "../client_cv_del/",
                data:
                {
                    id: $("#cv_id").val(),
                },
                success: function (data) {
                    if (data == 1) {
                        $("#div_creatcv").show();
                        $("#div_cv").hide();
                        $("#cv_del").hide();
                        var curnode = $('#tree_client').jstree('get_node', $("#id").val());
                        var newtext = curnode.text.replace("<img src = '/static/pages/images/cv.png' height='24px'> ", "")
                        $('#tree_client').jstree('set_text', $("#id").val(), newtext);

                        if ($("#cvclient_type").val() == "2" || $("#cvclient_type").val() == "3") {
                            var destinationdata = JSON.parse($("#cvclient_u_destination").val());
                            for (var i = 0; i < destinationdata.length; i++) {
                                if (destinationdata[i].utilid == $("#cvclient_utils_manage").val()) {
                                    for (var j = 0; j < destinationdata[i].destination_list.length; j++) {
                                        if (destinationdata[i].destination_list[j].id == $("#cv_id").val()) {
                                            destinationdata[i].destination_list.splice(j, 1)
                                            $("#cvclient_u_destination").val(JSON.stringify(destinationdata));

                                            break;
                                        }
                                    }
                                    $("#cvclient_destination option[value='" + $("#cv_id").val() + "']").remove();
                                    $("#cv_r_destClient option[value='" + $("#cv_id").val() + "']").remove();
                                    break;
                                }
                            }

                        }
                        alert("删除成功！");
                    } else
                        alert("删除失败，请于管理员联系。");
                },
                error: function (e) {
                    alert("删除失败，请于管理员联系。");
                }
            });
        }
    })

    $('#cv_backup_his').dataTable({
        "bAutoWidth": true,
        "bProcessing": true,
        "bSort": false,
        "destroy": true,
        //"ajax": "../../oraclerecoverydata?origin_id=" + origin_id,
        "columns": [
            { "data": "jobId" },
            { "data": "jobType" },
            { "data": "Level" },
            { "data": "StartTime" },
            { "data": "LastTime" },
            { "data": null },
        ],
        "columnDefs": [{
            "targets": -1,
            "data": null,
            "defaultContent": "<button  id='select' title='选择'  class='btn btn-xs btn-primary' type='button'><i class='fa fa-check'></i></button>"
        }],

        "oLanguage": {
            "sLengthMenu": "&nbsp;&nbsp;每页显示 _MENU_ 条记录",
            "sInfo": "从 _START_ 到 _END_ /共 _TOTAL_ 条数据",
            "sInfoEmpty": '',
            "sInfoFiltered": "(从 _MAX_ 条数据中检索)",
            "sSearch": "搜索",
            "oPaginate": {
                "sFirst": "首页",
                "sPrevious": "前一页",
                "sNext": "后一页",
                "sLast": "尾页"
            },
            "sZeroRecords": "没有检索到数据",
        }
    });
    $('#cv_backup_his tbody').on('click', 'button#select', function () {
        $('#tabcheck2_3').click();
        var table = $('#cv_backup_his').DataTable();
        var data = table.row($(this).parents('tr')).data();
        var pre_last_time = "";
        try {
            pre_last_time = table.row($(this).parents('tr').next()).data().LastTime;
        } catch (e) {
            //..
        }
        $('#cv_r_pre_restore_time').val(pre_last_time);
        $("#cv_r_datetimepicker").val(data.LastTime);
        $("input[name='optionsRadios'][value='1']").prop("checked", false);
        $("input[name='optionsRadios'][value='2']").prop("checked", true);
        $("#cv_r_browseJobId").val(data.jobId);
        $("#cv_r_data_sp").val(data.data_sp);
    });

    $('#cv_restore_his').dataTable({
        "bAutoWidth": true,
        "bProcessing": true,
        "bSort": false,
        "destroy": true,
        //"ajax": "../../oraclerecoverydata?origin_id=" + origin_id,
        "columns": [
            { "data": "jobid" },
            { "data": "jobType" },
            { "data": "starttime" },
            { "data": "endtime" },
            { "data": "jobstatus" }
        ],

        "oLanguage": {
            "sLengthMenu": "&nbsp;&nbsp;每页显示 _MENU_ 条记录",
            "sZeroRecords": "抱歉， 没有找到",
            "sInfo": "从 _START_ 到 _END_ /共 _TOTAL_ 条数据",
            "sInfoEmpty": '',
            "sInfoFiltered": "(从 _MAX_ 条数据中检索)",
            "sSearch": "搜索",
            "oPaginate": {
                "sFirst": "首页",
                "sPrevious": "前一页",
                "sNext": "后一页",
                "sLast": "尾页"
            },
            "sZeroRecords": "没有检索到数据",

        }
    });
    $('#cv_r_datetimepicker').datetimepicker({
        format: 'yyyy-mm-dd hh:ii:ss',
        pickerPosition: 'top-right'
    });

    $('#cv_r_recovery').click(function () {
        if ($("input[name='optionsRadios']:checked").val() == "2" && $('#cv_r_datetimepicker').val() == "")
            alert("请输入时间。");
        else {
            if ($('#cv_r_destClient').val() == "")
                alert("请选择目标客户端。");
            else {
                var myrestoreTime = "";
                if ($("input[name='optionsRadios']:checked").val() == "2" && $('#cv_r_datetimepicker').val() != "") {
                    myrestoreTime = $('#cv_r_datetimepicker').val();
                }
                var destClient = $('#cv_r_destClient option:selected').text().trim();
                if ($('#cv_r_destClient').val() == "self") {
                    destClient = $('#cv_r_sourceClient').val()
                }

                // 区分应用
                var agent = $("#cvclient_agentType").val();
                if (agent.indexOf("Oracle") != -1) {
                    $.ajax({
                        type: "POST",
                        url: "../../client_cv_recovery/",
                        data: {
                            cv_id: $('#cv_id').val(),
                            sourceClient: $('#cv_r_sourceClient').val(),
                            destClient: destClient,
                            restoreTime: myrestoreTime,
                            browseJobId: $("#cv_r_browseJobId").val(),
                            // 判断是oracle还是oracle rac
                            agent: agent,
                            data_path: $("#cv_r_data_path").val(),
                            copy_priority: $("#cv_r_copy_priority").val(),
                            data_sp: $("#cv_r_data_sp").val(),
                        },
                        success: function (data) {
                            alert(data);
                            var table1 = $('#cv_restore_his').DataTable();
                            table1.ajax.reload();
                        },
                        error: function (e) {
                            alert("恢复失败，请于客服联系。");
                        }
                    });
                } else if (agent.indexOf('File System') != -1) {
                    if ($("input[name='cv_r_path']:checked").val() == "2" && $('#cv_r_mypath').val() == "")
                        alert("请输入指定路径。");
                    else {
                        var iscover = $("input[name='cv_r_overwrite']:checked").val();
                        var mypath = "same"
                        if ($("input[name='cv_r_path']:checked").val() == "2")
                            mypath = $('#cv_r_mypath').val()
                        var selectedfile = ""
                        $("#cv_r_fs_se_1 option").each(function () {
                            var txt = $(this).val();
                            selectedfile = selectedfile + txt + "*!-!*"
                        });
                        $.ajax({
                            type: "POST",
                            url: "../../client_cv_recovery/",
                            data: {
                                cv_id: $('#cv_id').val(),
                                sourceClient: $('#cv_r_sourceClient').val(),
                                destClient: destClient,
                                restoreTime: myrestoreTime,
                                browseJobId: $("#cv_r_browseJobId").val(),
                                agent: agent,

                                iscover: iscover,
                                mypath: mypath,
                                selectedfile: selectedfile,
                            },
                            success: function (data) {
                                alert(data);
                                var table1 = $('#cv_restore_his').DataTable();
                                table1.ajax.reload();
                            },
                            error: function (e) {
                                alert("恢复失败，请于客服联系。");
                            }
                        });
                    }
                } else if (agent.indexOf('SQL Server') != -1) {
                    var mssql_iscover = "FALSE"
                    if ($('#cv_r_isoverwrite').is(':checked')) {
                        mssql_iscover = "TRUE"
                    }
                    $.ajax({
                        type: "POST",
                        url: "../../client_cv_recovery/",
                        data: {
                            cv_id: $('#cv_id').val(),
                            sourceClient: $('#cv_r_sourceClient').val(),
                            destClient: destClient,
                            restoreTime: myrestoreTime,
                            browseJobId: $("#cv_r_browseJobId").val(),
                            agent: agent,

                            mssql_iscover: mssql_iscover,
                        },
                        success: function (data) {
                            alert(data);
                            var table1 = $('#cv_restore_his').DataTable();
                            table1.ajax.reload();
                        },
                        error: function (e) {
                            alert("恢复失败，请于客服联系。");
                        }
                    });
                }




            }
        }
    });

    /*
        自主恢复 
            参数
    */
    $('#navtabs2 a').on("click", function () {
        var a_id = $(this).prop('id');
        if (a_id == 'tabcheck2_3') {
            var agent_type = $('#cvclient_agentType').val();
            if (agent_type.indexOf("Oracle") != -1) {
                $('#cv_r_orcl').show();
                $('#cv_r_mssql').hide();
                $('#cv_r_filesystem').hide();
            } else if (agent_type.indexOf("SQL Server") != -1) {
                $('#cv_r_mssql').show();
                $('#cv_r_orcl').hide();
                $('#cv_r_filesystem').hide();
            } else if (agent_type.indexOf("File System") != -1) {
                $('#cv_r_mssql').hide();
                $('#cv_r_orcl').hide();
                $('#cv_r_filesystem').show();
            } else {
                $('#cv_r_mssql').hide();
                $('#cv_r_orcl').hide();
                $('#cv_r_filesystem').hide();
            }
        }
    });

    $('#cv_selectpath').click(function () {
        $('#cv_fs_se_1').empty();
        var cv_fs_tree = $.fn.zTree.getZTreeObj("cv_fs_tree");
        var nodes = cv_fs_tree.getCheckedNodes(true);
        for (var k = 0, length = nodes.length; k < length; k++) {
            var halfCheck = nodes[k].getCheckStatus();
            if (!halfCheck.half) {
                $("#cv_fs_se_1").append("<option value='" + nodes[k].id + "'>" + nodes[k].id + "</option>");
            }
        }
        if (nodes.length == 0)
            $("#cv_fs_se_1").append("<option value=''></option>");
    })


    //db复制
    getDbcopyinfo();
    $("#dbcopy_dbtype").change(function () {
        if ($("#dbcopy_dbtype").val() == "1") {
            $("#oraclediv").show();
            $("#mysqldiv").hide();
        }
        if ($("#dbcopy_dbtype").val() == "2") {
            $("#mysqldiv").show();
            $("#oraclediv").hide();
        }
    });
    $("#dbcopy_hosttype").change(function () {
        if ($("#dbcopy_hosttype").val() == "1") {
            $("#dbcopy_std_div").show();
            $("#dbcopy_mysql_std_div").show();
        } else {
            $("#dbcopy_std_div").hide();
            $("#dbcopy_mysql_std_div").hide();
        }
    });
    $('#creatdbcopy').click(function () {
        $("#div_creatdbcopy").hide();
        $("#div_dbcopy").show();
        $("#dbcopy_oracle_del").hide();
        $("#dbcopy_mysql_del").hide();
        $("#dbcopy_dbtype").removeProp("disabled");
        $("#tabcheck3_1").click();
        $("#tabcheck3_2").parent().hide();
        $("#tabcheck3_3").parent().hide();

        $("#dbcopy_id").val("0");
        $("#dbcopy_dbtype").val("1");
        $("#dbcopy_hosttype").val("1");
        $("#dbcopy_oracleusername").val("");
        $("#dbcopy_oraclepassword").val("");
        $("#dbcopy_oracleinstance").val("");
        $("#dbcopy_mysqlusername").val("");
        $("#dbcopy_mysqlpassword").val("");
        $("#dbcopy_mysqlcopyusername").val("");
        $("#dbcopy_mysqlcopypassword").val("");
        $("#dbcopy_mysqlbinlog").val("");
        $("#mysqldiv").hide();
        $("#oraclediv").show();
        $("#dbcopy_std_div").show();
        $("#dbcopy_mysql_std_div").show();

    });
    $('#dbcopy_oracle_save').click(function () {
        $.ajax({
            type: "POST",
            dataType: 'json',
            url: "../client_dbcopy_save/",
            data: {

                id: $("#id").val(),
                dbcopy_id: $("#dbcopy_id").val(),
                dbcopy_dbtype: $("#dbcopy_dbtype").val(),
                dbcopy_hosttype: $("#dbcopy_hosttype").val(),
                dbcopy_oracleusername: $("#dbcopy_oracleusername").val(),
                dbcopy_oraclepassword: $("#dbcopy_oraclepassword").val(),
                dbcopy_oracleinstance: $("#dbcopy_oracleinstance").val(),
                dbcopy_std: $("#dbcopy_std").val(),
            },
            success: function (data) {
                if (data.ret == 1) {
                    if ($("#dbcopy_id").val() == "0") {
                        $("#dbcopy_id").val(data.dbcopy_id);
                        $("#dbcopy_del").show();
                        if ($("#dbcopy_hosttype").val() == "1") {
                            $("#tabcheck3_2").parent().show();
                            $("#tabcheck3_3").parent().show();
                        }
                        else {
                            $("#tabcheck3_2").parent().hide();
                            $("#tabcheck3_3").parent().hide();
                        }
                        var curnode = $('#tree_client').jstree('get_node', $("#id").val());
                        var newtext = curnode
                        newtext = "<img src = '/static/pages/images/oracle.png' height='24px'> " + curnode.text
                        $('#tree_client').jstree('set_text', $("#id").val(), newtext);
                    }
                    //刷新备库下拉菜单
                    if ($("#dbcopy_hosttype").val() == "2") {
                        var std = $("#dbcopy_std").val();
                        var stddata = JSON.parse($("#dbcopy_u_std").val());
                        var cur_std = { "name": $("#host_name").val() + "(" + $("#host_ip").val() + ")", "id": data.dbcopy_id, "type": $("#dbcopy_dbtype").val() }
                        if (!inArray(cur_std, stddata)) {
                            stddata.push(cur_std);
                            $("#dbcopy_u_std").val(JSON.stringify(stddata));
                        }
                        getDbcopyStd();
                        $("#dbcopy_std").val(std);
                    }
                    if ($("#dbcopy_hosttype").val() == "1") {
                        var stddata = JSON.parse($("#dbcopy_u_std").val());
                        for (var i = 0; i < stddata.length; i++) {
                            if (stddata[i].id == $("#dbcopy_id").val()) {
                                stddata.splice(i, 1)
                                $("#dbcopy_u_std").val(JSON.stringify(stddata));
                                break;
                            }
                        }
                        $("#dbcopy_std option[value='" + $("#dbcopy_id").val() + "']").remove();
                    }
                    if ($("#dbcopy_hosttype").val() == "1") {
                        $("#tabcheck3_2").parent().show();
                        $("#tabcheck3_3").parent().show();
                        get_dbcopy_oracle_detail();
                    }
                    else {
                        $("#tabcheck3_2").parent().hide();
                        $("#tabcheck3_3").parent().hide();
                    }
                    $("#dbcopy_oracle_del").show();
                    $("#dbcopy_dbtype").prop("disabled", "disabled");
                }
                alert(data.info);
            },
            error: function (e) {
                alert("页面出现错误，请于管理员联系。");
            }
        });
    });
    $('#dbcopy_mysql_save').click(function () {
        $.ajax({
            type: "POST",
            dataType: 'json',
            url: "../client_dbcopy_mysql_save/",
            data: {

                id: $("#id").val(),
                dbcopy_id: $("#dbcopy_id").val(),
                dbcopy_dbtype: $("#dbcopy_dbtype").val(),
                dbcopy_hosttype: $("#dbcopy_hosttype").val(),
                dbcopy_mysqlusername: $("#dbcopy_mysqlusername").val(),
                dbcopy_mysqlpassword: $("#dbcopy_mysqlpassword").val(),
                dbcopy_mysqlcopyusername: $("#dbcopy_mysqlcopyusername").val(),
                dbcopy_mysqlcopypassword: $("#dbcopy_mysqlcopypassword").val(),
                dbcopy_mysqlbinlog: $("#dbcopy_mysqlbinlog").val(),
                dbcopy_mysql_std: JSON.stringify($("#dbcopy_mysql_std").val()),
            },
            success: function (data) {
                if (data.ret == 1) {
                    if ($("#dbcopy_id").val() == "0") {
                        $("#dbcopy_id").val(data.dbcopy_id);
                        if ($("#dbcopy_hosttype").val() == "1") {
                            $("#tabcheck3_2").parent().show();
                            $("#tabcheck3_3").parent().show();
                        }
                        else {
                            $("#tabcheck3_2").parent().hide();
                            $("#tabcheck3_3").parent().hide();
                        }
                        var curnode = $('#tree_client').jstree('get_node', $("#id").val());
                        var newtext = curnode
                        newtext = "<img src = '/static/pages/images/mysql.png' height='24px'> " + curnode.text
                        $('#tree_client').jstree('set_text', $("#id").val(), newtext);
                    }
                    //刷新备库下拉菜单
                    if ($("#dbcopy_hosttype").val() == "2") {
                        var std = $("#dbcopy_mysql_std").val();
                        var stddata = JSON.parse($("#dbcopy_u_std").val());
                        var cur_std = { "name": $("#host_name").val() + "(" + $("#host_ip").val() + ")", "id": data.dbcopy_id, "type": $("#dbcopy_dbtype").val() }
                        if (!inArray(cur_std, stddata)) {
                            stddata.push(cur_std);
                            $("#dbcopy_u_std").val(JSON.stringify(stddata));
                        }
                        getDbcopyMysqlStd();
                        $("#dbcopy_mysql_std").val(std);
                        $("#dbcopy_mysql_std").select2({
                            width: null
                        });
                    }
                    if ($("#dbcopy_hosttype").val() == "1") {
                        var stddata = JSON.parse($("#dbcopy_u_std").val());
                        for (var i = 0; i < stddata.length; i++) {
                            if (stddata[i].id == $("#dbcopy_id").val()) {
                                stddata.splice(i, 1)
                                $("#dbcopy_u_std").val(JSON.stringify(stddata));
                                break;
                            }
                        }
                        $("#dbcopy_mysql_std option[value='" + $("#dbcopy_id").val() + "']").remove();
                        $("#dbcopy_mysql_std").select2({
                            width: null
                        });
                    }
                    if ($("#dbcopy_hosttype").val() == "1") {
                        $("#tabcheck3_2").parent().show();
                        $("#tabcheck3_3").parent().show();
                        get_dbcopy_mysql_detail();
                    }
                    else {
                        $("#tabcheck3_2").parent().hide();
                        $("#tabcheck3_3").parent().hide();
                    }
                    $("#dbcopy_mysql_del").show();
                    $("#dbcopy_dbtype").prop("disabled", "disabled");
                }
                alert(data.info);
            },
            error: function (e) {
                alert("页面出现错误，请于管理员联系。");
            }
        });
    });
    $('#dbcopy_oracle_del').click(function () {
        if (confirm("确定要删除？删除后不可恢复。")) {
            $.ajax({
                type: "POST",
                url: "../client_dbcopy_del/",
                data:
                {
                    id: $("#dbcopy_id").val(),
                },
                success: function (data) {
                    if (data == 1) {
                        $("#div_creatdbcopy").show();
                        $("#div_dbcopy").hide();
                        $("#dbcopy_oracle_del").hide();

                        var curnode = $('#tree_client').jstree('get_node', $("#id").val());
                        var newtext = curnode
                        if ($("#dbcopy_dbtype").val() == "1") {
                            newtext = curnode.text.replace("<img src = '/static/pages/images/oracle.png' height='24px'> ", "")
                        }
                        $('#tree_client').jstree('set_text', $("#id").val(), newtext);
                        //刷新备库下拉菜单
                        var stddata = JSON.parse($("#dbcopy_u_std").val());
                        for (var i = 0; i < stddata.length; i++) {
                            if (stddata[i].id == $("#dbcopy_id").val()) {
                                stddata.splice(i, 1)
                                $("#dbcopy_u_std").val(JSON.stringify(stddata));
                                break;
                            }
                        }
                        $("#dbcopy_std option[value='" + $("#dbcopy_id").val() + "']").remove();

                        alert("删除成功！");
                    } else
                        alert("删除失败，请于管理员联系。");
                },
                error: function (e) {
                    alert("删除失败，请于管理员联系。");
                }
            });
        }
    })
    $('#dbcopy_mysql_del').click(function () {
        if (confirm("确定要删除？删除后不可恢复。")) {
            $.ajax({
                type: "POST",
                url: "../client_dbcopy_del/",
                data:
                {
                    id: $("#dbcopy_id").val(),
                },
                success: function (data) {
                    if (data == 1) {
                        $("#div_creatdbcopy").show();
                        $("#div_dbcopy").hide();
                        $("#dbcopy_oracle_del").hide();
                        $("#dbcopy_mysql_del").hide();

                        var curnode = $('#tree_client').jstree('get_node', $("#id").val());
                        var newtext = curnode
                        if ($("#dbcopy_dbtype").val() == "1") {
                            newtext = curnode.text.replace("<img src = '/static/pages/images/mysql.png' height='24px'> ", "")
                        }
                        $('#tree_client').jstree('set_text', $("#id").val(), newtext);
                        //刷新备库下拉菜单
                        var stddata = JSON.parse($("#dbcopy_u_std").val());
                        for (var i = 0; i < stddata.length; i++) {
                            if (stddata[i].id == $("#dbcopy_id").val()) {
                                stddata.splice(i, 1)
                                $("#dbcopy_u_std").val(JSON.stringify(stddata));
                                break;
                            }
                        }
                        $("#dbcopy_mysql_std option[value='" + $("#dbcopy_id").val() + "']").remove();

                        alert("删除成功！");
                    } else
                        alert("删除失败，请于管理员联系。");
                },
                error: function (e) {
                    alert("删除失败，请于管理员联系。");
                }
            });
        }
    })
    $("#confirm").click(function () {
        var process_id = $("#process_id").val();

        // 非邀请流程启动
        // $.ajax({
        //     type: "POST",
        //     dataType: 'json',
        //     url: "../cv_oracle_run/",
        //     data:
        //         {
        //             processid: process_id,
        //             run_person: $("#run_person").val(),
        //             run_time: $("#run_time").val(),
        //             run_reason: $("#run_reason").val(),
        //             process_type:$("#process_type").val()
        //         },
        //     success: function (data) {
        //         if (data["res"] == "新增成功。") {
        //             window.location.href = data["data"];
        //         } else
        //             alert(data["res"]);
        //     },
        //     error: function (e) {
        //         alert("流程启动失败，请于管理员联系。");
        //     }
        // });
    });
    $('#dbcopy_his').dataTable({
        "bAutoWidth": true,
        "bSort": false,
        "bProcessing": true,
        //"ajax": "../oracle_restore_data/",
        "fnServerParams": function (aoData) {
            aoData.push({
                name: "process_id",
                value: $("#process_id").val()
            })
        },
        "columns": [
            { "data": "processrun_id" },
            { "data": "process_name" },
            { "data": "process_type" },
            { "data": "createuser" },
            { "data": "state" },
            { "data": "run_reason" },
            { "data": "starttime" },
            { "data": "endtime" },
            { "data": "process_id" },
            { "data": "process_url" },
            { "data": null },
        ],
        "columnDefs": [{
            "targets": 1,
            "render": function (data, type, full) {
                return full.state != "计划" ? "<td><a href='process_url' target='_blank'>data</a></td>".replace("data", full.process_name).replace("process_url", "/processindex/" + full.processrun_id + "?s=true") : "<td>" + full.process_name + "</td>"
            }
        }, {
            "visible": false,
            "targets": -2  // 倒数第一列
        }, {
            "visible": false,
            "targets": -3  // 倒数第一列
        }, {
            "targets": -1,  // 指定最后一列添加按钮；
            "data": null,
            "width": "60px",  // 指定列宽；
            "render": function (data, type, full) {
                return "<td><button class='btn btn-xs btn-primary' type='button'><a href='/custom_pdf_report/?processrunid&processid'><i class='fa fa-arrow-circle-down' style='color: white'></i></a></button><button title='删除'  id='delrow' class='btn btn-xs btn-primary' type='button'><i class='fa fa-trash-o'></i></button></td>".replace("processrunid", "processrunid=" + full.processrun_id).replace("processid", "processid=" + full.process_id)
            }
        }],

        "oLanguage": {
            "sLengthMenu": "&nbsp;&nbsp;每页显示 _MENU_ 条记录",
            "sZeroRecords": "抱歉， 没有找到",
            "sInfo": "从 _START_ 到 _END_ /共 _TOTAL_ 条数据",
            "sInfoEmpty": '',
            "sInfoFiltered": "(从 _MAX_ 条数据中检索)",
            "sSearch": "搜索",
            "oPaginate": {
                "sFirst": "首页",
                "sPrevious": "前一页",
                "sNext": "后一页",
                "sLast": "尾页"
            },
            "sZeroRecords": "没有检索到数据",

        }
    });
    $('#dbcopy_his tbody').on('click', 'button#delrow', function () {
        if (confirm("确定要删除该条数据？")) {
            var table = $('#sample_1').DataTable();
            var data = table.row($(this).parents('tr')).data();
            $.ajax({
                type: "POST",
                url: "../../delete_current_process_run/",
                data:
                {
                    processrun_id: data.processrun_id
                },
                success: function (data) {
                    if (data == 1) {
                        table.ajax.reload();
                        alert("删除成功！");
                    } else
                        alert("删除失败，请于管理员联系。");
                },
                error: function (e) {
                    alert("删除失败，请于管理员联系。");
                }
            });

        }
    });

    //kvm

    kvmFunction();
    $('#creatkvm').click(function () {
        $("#div_creatkvm").hide();
        $("#div_kvm").show();
        $("#kvm_del").hide();
        $("#tabcheck4_1").click();
        $("#tabcheck4_2").parent().hide();
        $("#tabcheck4_3").parent().hide();

        $("#kvm_id").val("0");
    });
    $('#kvm_protect_save').click(function () {
        $.ajax({
            type: "POST",
            dataType: 'json',
            url: "../kvm_save/",
            data:
                {
                    kvm_id:$("#kvm_id").val(),
                    util_kvm_id: $("#kvm_machine_platform").val(),
                    name: $("#kvm_machine").val(),
                    filesystem: $("#kvm_filesystem").val(),
                },
            success: function (data) {
                if (data.ret == 1) {
                    if ($("#kvm_id").val() == "0") {
                        $("#kvm_id").val(data.kvm_id);
                        $("#kvm_del").show();
                        $("#tabcheck4_2").parent().show();
                        $("#tabcheck4_3").parent().show();
                        var curnode = $('#tree_client').jstree('get_node', $("#id").val());
                        var newtext = curnode
                        newtext = "<img src = '/static/pages/images/ts.png' height='24px'> " + curnode.text
                        $('#tree_client').jstree('set_text', $("#id").val(), newtext);
                    }
                }
                //get_kvm_detail();
                alert(data.info);
            },
            error: function (e) {
                alert("页面出现错误，请于管理员联系。");
            }
        });
    });
    $('#kvm_machine_platform').change(function () {
        kvmFunction();
    });
    $('#zfs_snapshot_create').click(function () {
        $.ajax({
            type: "POST",
            dataType: 'json',
            url: "../kvm_data/",
            data: {
                utils_kvm_id: $('#kvm_machine_platform').val()
            },
            success: function (data) {
                if (data.ret == 0) {
                    alert(data.data)
                } else {
                    for (i = 0; i < data.kvm_filesystem_list.length; i++) {
                        $("#kvm_filesystem1").append('<option value="' + data.kvm_filesystem_list[i] + '">' + data.kvm_filesystem_list[i] + '</option>')
                    }
                }
            }
        });
        $('#snapshot_name').val("")
    });
    $('#zfs_snapshot_save').click(function () {
        var table = $('#zfs_snapshot').DataTable();

        $.ajax({
            type: "POST",
            dataType: 'json',
            url: "../zfs_snapshot_save/",
            data:
                {
                    util_kvm_id: $("#kvm_machine_platform").val(),
                    filesystem: $("#kvm_filesystem").val(),
                    snapshot_name: $("#snapshot_name").val(),
                },
            success: function (data) {
                var myres = data["res"];
                if (myres == "创建成功。") {
                    $("#id").val(data["data"]);
                    $('#static02').modal('hide');
                    table.ajax.reload();
                }
                alert(myres);
            },
            error: function (e) {
                alert("页面出现错误，请于管理员联系。");
            }
        });
    });
    $('#zfs_snapshot tbody').on('click', 'button#edit', function () {
        var table = $('#zfs_snapshot').DataTable();
        var data = table.row($(this).parents('tr')).data();
        $("#snapshot_id").val(data.id);
        $("#utils_id").val(data.utils_id);
        $("#snapshot_name1").val(data.name);
        var kvm_copy_name = $("#snapshot_name1").val().split('/');
        $('#kvm_copy_name').val(kvm_copy_name[1]);
        $("#kvm_copy_ip").val("");
        $("#kvm_copy_hostname").val("")

    });
    $('#zfs_snapshot tbody').on('click', 'button#delrow', function () {
        if (confirm("确定要删除该条数据？")) {
            var table = $('#zfs_snapshot').DataTable();
            var data = table.row($(this).parents('tr')).data();
            $.ajax({
                type: "POST",
                url: "../zfs_snapshot_del/",
                data:
                    {
                        id: data.id,
                        utils_id: $('#kvm_machine_platform').val(),
                        snapshot_name: data.name
                    },
                success: function (data) {
                    var myres = data["res"];
                    if (myres == "删除成功。") {
                        table.ajax.reload();
                    }
                    alert(myres);
                },
                error: function (e) {
                    alert("删除失败，请于管理员联系。");
                }
            });
        }
    });
    $('#zfs_snapshot_mount').click(function () {
        $.ajax({
            type: "POST",
            dataType: 'json',
            url: "../zfs_snapshot_mount/",
            data:
                {
                    utils_id: $("#kvm_machine_platform").val(),
                    snapshot_name: $("#snapshot_name1").val(),
                    kvm_copy_name: $("#kvm_copy_name").val(),
                    kvm_copy_ip: $("#kvm_copy_ip").val(),
                    kvm_copy_hostname: $("#kvm_copy_hostname").val(),

                    kvm_machine: $("#kvm_machine").val(),
                },
            success: function (data) {
                var myres = data["res"];
                if (myres == "创建成功。") {
                    $("#id").val(data["data"]);
                    $('#static02').modal('hide');
                    table.ajax.reload();
                }
                alert(myres);
            },
            error: function (e) {
                alert("页面出现错误，请于管理员联系。");
            }
        });
    });
    $('#kvm_copy').dataTable({
        "bAutoWidth": true,
        "bSort": false,
        "iDisplayLength": 25,
        "bProcessing": true,
        "ajax": "",
        "columns": [
            { "data": "id" },
            { "data": "kvm_copy_ip" },
            { "data": "kvm_copy_name" },
            { "data": "kvm_copy_hostname" },
            { "data": "createtime" },
            { "data": "createuser" },
            { "data": null }
        ],

        "columnDefs": [{
            "targets": -1,
            "data": null,
            "width": "100px",
            "defaultContent": "<button title='删除副本'  id='delrow' class='btn btn-xs btn-primary' type='button'><i class='fa fa-trash-o'></i></button>"
        }
        ],
        "oLanguage": {
            "sLengthMenu": "每页显示 _MENU_ 条记录",
            "sZeroRecords": "抱歉， 没有找到",
            "sInfo": "从 _START_ 到 _END_ /共 _TOTAL_ 条数据",
            "sInfoEmpty": "没有数据",
            "sInfoFiltered": "(从 _MAX_ 条数据中检索)",
            "sSearch": "搜索",
            "oPaginate": {
                "sFirst": "首页",
                "sPrevious": "前一页",
                "sNext": "后一页",
                "sLast": "尾页"
            },
            "sZeroRecords": "没有检索到数据",
        },
    });
    $('#kvm_copy tbody').on('click', 'button#delrow', function () {
        if (confirm("确定要删除该条数据？")) {
            var table = $('#kvm_copy').DataTable();
            var data = table.row($(this).parents('tr')).data();
            $.ajax({
                type: "POST",
                url: "",
                data:
                {
                    id: data.id,
                },
                success: function (data) {
                    if (data == 1) {
                        table.ajax.reload();
                        alert("删除成功！");
                    } else
                        alert("删除失败，请于管理员联系。");
                },
                error: function (e) {
                    alert("删除失败，请于管理员联系。");
                }
            });
        }
    });


});


