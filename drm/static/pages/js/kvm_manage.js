function getkvmtree() {
     $.ajax({
        type: "POST",
        dataType: "json",
        url: "../get_kvm_tree/",
        data: {
            id: $('#id').val(),
        },
        success: function (data) {
            if (data.ret == 0) {
                alert(data.data)
            } else {
                console.log(data.data, '555')
                $('#loading').hide();
                $('#showdata').show();
                $('#kvm_mem_cpu_disk_data').val(JSON.stringify(data.data[0].kvm_memory_disk_cpu_data));
                $('#tree_kvm_manage').jstree({
                    'core': {
                        "themes": {
                            "responsive": false
                        },
                        "check_callback": true,
                        'data': data.data
                    },
                    "types": {
                        "NODE": {
                            "icon": "fa fa-folder icon-state-warning icon-lg"
                        },
                        "PROCESS": {
                            "icon": "fa fa-file-code-o icon-state-warning icon-lg"
                        }
                    },
                    "contextmenu": {
                        "items": {
                            "create": null,
                            "rename": null,
                            "remove": null,
                            "ccp": null,

                        }
                    },
                    "plugins": ["contextmenu", "dnd", "types", "role"]
                })
                    .bind('select_node.jstree', function (event, data) {
                        $("#form_div").show();
                        var type = data.node.original.type;
                        $("#id").val(data.node.id);
                        $("#pid").val(data.node.parent);
                        $("#utils_id").val(data.node.id);
                        $("#my_type").val(type);
                        $("#title").text(data.node.data.name);
                        $('#pname').val(data.node.data.pname);

                        if (data.node.parent == "#") {
                            $("#node").show();
                            $("#kvm_info").hide();
                            $("#node_id").val(data.node.id);
                            $("#node_pname").val(data.node.data.pname);
                            $("#node_name").val(data.node.data.name);


                            $("#host_ip").val(data.node.original.kvm_credit.KvmHost);
                            $("#hostname").val(data.node.original.memory_disk_cpu_data.hostname);
                            $("#os").val(data.node.original.memory_disk_cpu_data.os);
                            $("#cpu").val(data.node.original.memory_disk_cpu_data.cpu_count + '个');


                            var memory_disk_cpu_data = data.node.original.memory_disk_cpu_data;
                            $('#memory_space input').eq(0).val(memory_disk_cpu_data["memory_usage"].toFixed(0)).trigger('change');
                            $('#memory_space h4').eq(1).text(memory_disk_cpu_data["mem_used"] + " GB/" + memory_disk_cpu_data["mem_total"] + " GB");

                            $('#disk_space input').eq(0).val(memory_disk_cpu_data["disk_usage"].toFixed(0)).trigger('change');
                            $('#disk_space h4').eq(1).text(memory_disk_cpu_data["disk_used"] + " GB/" + memory_disk_cpu_data["disk_total"] + " GB");

                            $('#cpu_space input').eq(0).val(memory_disk_cpu_data["cpu_usage"].toFixed(0)).trigger('change');
                            $('#cpu_space h4').eq(1).text(memory_disk_cpu_data["cpu_usage"] + " %/" + '100' + " %")


                        }
                        if (type == 'KVM') {
                            // 虚拟机
                            $("#node").hide();
                            $("#kvm_info").show();
                            $("#kvm_undefine").hide();
                            var kvm_info = data.node.original.kvm_info;
                            $("#kvm_node_pname").val(data.node.data.pname);
                            $("#kvm_name").val(kvm_info.kvm_name);
                            $("#kvm_state").val(kvm_info.kvm_state);
                            $("#kvm_cpu").val(kvm_info.kvm_cpu + '个');
                            $("#kvm_memory").val(kvm_info.kvm_memory + 'MB');
                            $("#kvm_disk").val(kvm_info.kvm_disk);
                            $("#kvm_os").val(kvm_info.kvm_os);

                            try {
                                var kvm_memory_disk_cpu_data = JSON.parse($('#kvm_mem_cpu_disk_data').val())
                            }catch(e){}

                            var mem_data = kvm_memory_disk_cpu_data["kvm_mem_usage"][kvm_info.kvm_name];
                            var cpu_data = kvm_memory_disk_cpu_data["kvm_cpu_usage"][kvm_info.kvm_name];
                            if (kvm_info.kvm_state == '运行中'){
                                $('#kvm_memory_space input').eq(0).val(mem_data["mem_usage"].toFixed(0)).trigger('change');
                                $('#kvm_memory_space h4').eq(1).text(mem_data["mem_used"] + " GB/" + mem_data["mem_total"] + " GB");
                                if (cpu_data["cpu_usage"] < 0.5) {
                                    $('#kvm_cpu_space input').eq(0).val(1).trigger('change');
                                }else{
                                    $('#kvm_cpu_space input').eq(0).val(cpu_data["cpu_usage"].toFixed(0)).trigger('change');
                                }
                                $('#kvm_cpu_space h4').eq(1).text(cpu_data["cpu_usage"] + " %/" + '100' + " %")
                            }

                            if (kvm_info.kvm_state == '关闭'){
                                $('#kvm_memory_space input').eq(0).val(0).trigger('change');
                                $('#kvm_memory_space h4').eq(1).text(0 + " GB/" + kvm_info.kvm_memory/1024 + " GB");
                                $('#kvm_cpu_space input').eq(0).val(0).trigger('change');
                                $('#kvm_cpu_space h4').eq(1).text('0' + " %/" + '100' + " %");
                            }

                            for (var i = 0; i < kvm_memory_disk_cpu_data["kvm_disk_data"].length; i++) {
                                var filesystem = (kvm_memory_disk_cpu_data["kvm_disk_data"][i]['filesystem']).split('data/vmdata/')[1];
                                if (kvm_info.kvm_name == filesystem){
                                    $('#kvm_disk_space input').eq(0).val(kvm_memory_disk_cpu_data["kvm_disk_data"][i]["disk_usage"].toFixed(0)).trigger('change');
                                    $('#kvm_disk_space h4').eq(1).text(kvm_memory_disk_cpu_data["kvm_disk_data"][i]["used"] + " GB/" + kvm_memory_disk_cpu_data["kvm_disk_data"][i]["total"] + " GB");
                                    break
                                }
                            }
                        }
                        if (type == 'COPY') {
                            // 实例
                            $("#node").hide();
                            $("#kvm_info").show();
                            $("#kvm_undefine").show();
                            $("#kvm_node_pname").val(data.node.data.pname);
                            $("#kvm_node_pname").val(data.node.data.pname);
                            var kvm_info = data.node.original.kvm_info;
                            $("#kvm_name").val(kvm_info.kvm_name);
                            $("#kvm_state").val(kvm_info.kvm_state);
                            $("#kvm_cpu").val(kvm_info.kvm_cpu + '个');
                            $("#kvm_memory").val(kvm_info.kvm_memory + 'MB');
                            $("#kvm_disk").val(kvm_info.kvm_disk);
                            $("#kvm_os").val(kvm_info.kvm_os);

                            try {
                                var kvm_memory_disk_cpu_data = JSON.parse($('#kvm_mem_cpu_disk_data').val())
                            }catch(e){}

                            var mem_data = kvm_memory_disk_cpu_data["kvm_mem_usage"][kvm_info.kvm_name];
                            var cpu_data = kvm_memory_disk_cpu_data["kvm_cpu_usage"][kvm_info.kvm_name];
                            if (kvm_info.kvm_state == '运行中'){
                                $('#kvm_memory_space input').eq(0).val(mem_data["mem_usage"].toFixed(0)).trigger('change');
                                $('#kvm_memory_space h4').eq(1).text(mem_data["mem_used"] + " GB/" + mem_data["mem_total"] + " GB");

                                if (cpu_data["cpu_usage"] < 0.5) {
                                    $('#kvm_cpu_space input').eq(0).val(1).trigger('change');
                                }else{
                                    $('#kvm_cpu_space input').eq(0).val(cpu_data["cpu_usage"].toFixed(0)).trigger('change');
                                }

                                $('#kvm_cpu_space h4').eq(1).text(cpu_data["cpu_usage"] + " %/" + '100' + " %")
                            }
                            if (kvm_info.kvm_state == '关闭'){
                                $('#kvm_memory_space input').eq(0).val(0).trigger('change');
                                $('#kvm_memory_space h4').eq(1).text(0 + " GB/" + kvm_info.kvm_memory/1024 + " GB");
                                $('#kvm_cpu_space input').eq(0).val(0).trigger('change');
                                $('#kvm_cpu_space h4').eq(1).text('0' + " %/" + '100' + " %")
                            }

                            for (var i = 0; i < kvm_memory_disk_cpu_data["kvm_disk_data"].length; i++) {
                                var filesystem = (kvm_memory_disk_cpu_data["kvm_disk_data"][i]['filesystem']).split('data/vmdata/')[1];
                                if (kvm_info.kvm_name.replace('@', '-') == filesystem){
                                    $('#kvm_disk_space input').eq(0).val(kvm_memory_disk_cpu_data["kvm_disk_data"][i]["disk_usage"].toFixed(0)).trigger('change');
                                    $('#kvm_disk_space h4').eq(1).text(kvm_memory_disk_cpu_data["kvm_disk_data"][i]["used"] + " GB/" + kvm_memory_disk_cpu_data["kvm_disk_data"][i]["total"] + " GB");
                                    break
                                }
                            }

                        }
                    });

            }
        }
    });

}


$(document).ready(function () {
    $('#loading').show();
    $('#showdata').hide();
    getkvmtree();

    var Dashboard = function () {

        return {
            componentsKnobDials: function () {
                //knob does not support ie8 so skip it
                if (!jQuery().knob || App.isIE8()) {
                    return;
                }

                // general knob
                $(".knob").knob({
                    'dynamicDraw': true,
                    'thickness': 0.2,
                    'tickColorizeValues': true,
                    'skin': 'tron'
                });
            },

            init: function () {
                this.componentsKnobDials();
            }
        };

    }();

    if (App.isAngularJsApp() === false) {
        jQuery(document).ready(function () {
            Dashboard.init(); // init metronic core componets
        });
    }


    $('#kvm_suspend').click(function () {
        if (confirm("确定要暂停该虚拟机？")) {
            $.ajax({
                type: "POST",
                dataType: 'json',
                url: "../kvm_suspend/",
                data:
                    {
                        utils_id: $("#utils_id").val(),
                        kvm_name: $("#kvm_name").val(),
                        kvm_state: $("#kvm_state").val(),
                    },
                success: function (data) {
                    var myres = data["res"];
                    if (myres == "暂停成功。") {
                        getkvmtree();
                    }
                    alert(myres);
                },
                error: function (e) {
                    alert("页面出现错误，请于管理员联系。");
                }
            });
        }
    });


    $('#kvm_resume').click(function () {
        $.ajax({
            type: "POST",
            dataType: 'json',
            url: "../kvm_resume/",
            data:
                {
                    utils_id: $("#utils_id").val(),
                    kvm_name: $("#kvm_name").val(),
                    kvm_state: $("#kvm_state").val(),
                },
            success: function (data) {
                var myres = data["res"];
                if (myres == "运行成功。") {
                    getkvmtree();
                }
                alert(myres);
            },
            error: function (e) {
                alert("页面出现错误，请于管理员联系。");
            }
        });

    });


    $('#kvm_shutdown').click(function () {
        if (confirm("确定要关闭该虚拟机？")) {
            $.ajax({
                type: "POST",
                dataType: 'json',
                url: "../kvm_shutdown/",
                data:
                    {
                        utils_id: $("#utils_id").val(),
                        kvm_name: $("#kvm_name").val(),
                        kvm_state: $("#kvm_state").val(),
                    },
                success: function (data) {
                    var myres = data["res"];
                    if (myres == "关闭成功。") {
                        getkvmtree();
                    }
                    alert(myres);
                },
                error: function (e) {
                    alert("页面出现错误，请于管理员联系。");
                }
            });
        }
    });


    $('#kvm_reboot').click(function () {
        $.ajax({
            type: "POST",
            dataType: 'json',
            url: "../kvm_reboot/",
            data:
                {
                    utils_id: $("#utils_id").val(),
                    kvm_name: $("#kvm_name").val(),
                    kvm_state: $("#kvm_state").val(),
                },
            success: function (data) {
                var myres = data["res"];
                if (myres == "重启成功。") {
                    getkvmtree();
                }
                alert(myres);
            },
            error: function (e) {
                alert("页面出现错误，请于管理员联系。");
            }
        });

    });


    $('#kvm_undefine').click(function () {
       if (confirm("确定要删除该虚拟机？")) {
            $.ajax({
                type: "POST",
                url: "../kvm_delete/",
                data:
                    {
                        utils_id: $("#utils_id").val(),
                        kvm_name: $("#kvm_name").val(),
                        kvm_state: $("#kvm_state").val(),
                    },
                success: function (data) {
                    var myres = data["res"];
                    if (myres == "删除成功。") {
                        getkvmtree();
                    }
                    alert(myres);
                },
                error: function (e) {
                    alert("删除失败，请于管理员联系。");
                }
            });
        }

    });


    $('#kvm_clone').click(function () {
        $('#static01').modal('show');
        $('#loading1').hide();
        $('#kvm_clone_div').show();

        $('#kvm_name_old').val($('#kvm_name').val());
        $('#kvm_name_new').val('')
    });


    $('#kvm_clone_save').click(function () {
        $('#kvm_clone_div').hide();
        $('#loading1').show();
        $.ajax({
            type: "POST",
            dataType: 'json',
            url: "../kvm_clone_save/",
            data:
                {
                    utils_id: $("#utils_id").val(),
                    kvm_name_old: $("#kvm_name_old").val(),
                    kvm_name_new: $("#kvm_name_new").val(),
                    kvm_state: $("#kvm_state").val(),
                },
            success: function (data) {
                var myres = data["res"];
                if (myres == "克隆成功。") {
                    $('#loading1').hide();
                    $('#static01').modal('hide');
                    getkvmtree();
                }
                alert(myres);
                $('#loading1').hide();
                $('#kvm_clone_div').show();
            },
            error: function (e) {
                alert("页面出现错误，请于管理员联系。");
                $('#loading1').hide();
                $('#kvm_clone_div').show();
            }
        });
    });


    $('#kvm_destroy').click(function () {
        if (confirm("确定要断电该虚拟机？")) {
            $.ajax({
                type: "POST",
                dataType: 'json',
                url: "../kvm_destroy/",
                data:
                    {
                        utils_id: $("#utils_id").val(),
                        kvm_name: $("#kvm_name").val(),
                        kvm_state: $("#kvm_state").val(),
                    },
                success: function (data) {
                    var myres = data["res"];
                    if (myres == "断电成功。") {
                        getkvmtree();
                    }
                    alert(myres);
                },
                error: function (e) {
                    alert("页面出现错误，请于管理员联系。");
                }
            });
        }
    });


    $('#kvm_start').click(function () {
        $.ajax({
            type: "POST",
            dataType: 'json',
            url: "../kvm_start/",
            data:
                {
                    utils_id: $("#utils_id").val(),
                    kvm_name: $("#kvm_name").val(),
                    kvm_state: $("#kvm_state").val(),

                },
            success: function (data) {
                var myres = data["res"];
                if (myres == "开机成功。") {
                    getkvmtree();
                }
                alert(myres);
            },
            error: function (e) {
                alert("页面出现错误，请于管理员联系。");
            }
        });
    });



});