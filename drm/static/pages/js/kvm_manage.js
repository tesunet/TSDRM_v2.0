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
                alert(data.data);
                $('#loading').hide();
                $('#loading2').hide();
                $('#showdata').show();
            } else {
                $('#loading').hide();
                $('#loading2').hide();
                $('#showdata').show();
                $('#tree_kvm_manage').jstree({
                    'core': {
                        "themes": {
                            "responsive": false
                        },
                        "check_callback": true,
                        'data': data.data
                    },
                    "types": {
                        "KVM": {
                            "icon": false
                        },
                        "COPY": {
                            "icon": false
                        },
                        "ROOT": {
                            "icon": false
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
                        var kvm_id = '';
                        var utils_id = '';
                        var kvm_name = '';
                        var utils_ip = '';
                        if (data.node.data){
                            // 刷新整个页面之后，点击此虚拟机节点，获取数据
                            kvm_id = data.node.data.id;
                            utils_id = data.node.data.utils_id;
                            kvm_name = data.node.data.name;
                            utils_ip = data.node.original.ip;
                            $("#form_div").show();
                            $("#id").val(data.node.id);
                            $("#pid").val(data.node.parent);
                            $("#my_type").val(type);
                            $("#title").text(kvm_name);

                            $("#kvm_id").val(kvm_id);
                            $("#kvm_name").val(kvm_name);
                            $("#kvm_state").val(data.node.data.state);
                            $("#utils_id").val(utils_id);
                            $("#utils_ip").val(utils_ip);
                        }else {
                            //新建虚拟机、克隆虚拟机之后树节点展示此虚机信息，点击此虚拟机节点，获取数据
                            kvm_id = data.node.original.kvm_id;
                            utils_id = data.node.original.utils_id;
                            kvm_name = data.node.original.kvm_name;
                            utils_ip = data.node.original.utils_ip;
                            $("#form_div").show();
                            $("#id").val(data.node.id);
                            $("#pid").val(data.node.parent);
                            $("#title").text(kvm_name);

                            $("#kvm_id").val(kvm_id);
                            $("#kvm_name").val(kvm_name);
                            $("#kvm_state").val(data.node.original.kvm_state);
                            $("#utils_id").val(utils_id);
                            $("#utils_ip").val(utils_ip);
                        }
                        // 根节点
                        if (data.node.parent == "#") {
                            $("#loading2").show();
                            $("#form_div").hide();
                            $("#host_ip").val(data.node.original.kvm_credit.KvmHost);

                            $.ajax({
                                type: "POST",
                                dataType: 'json',
                                url: "../get_kvm_detail/",
                                data: {
                                    utils_id: utils_id,
                                },
                                success: function (data) {
                                    if (data.ret == 1) {
                                        $("#node").show();
                                        $("#kvm_info").hide();
                                        $("#loading2").hide();
                                        $("#form_div").show();

                                        var data = data.data.memory_disk_cpu_data;
                                        $("#hostname").val(data.hostname);
                                        $("#os").val(data.os);
                                        $("#cpu").val(data.cpu_count + '个');
                                        $('#memory_space input').eq(0).val(data["memory_usage"].toFixed(0)).trigger('change');
                                        $('#memory_space h4').eq(1).text(data["mem_used"] + "/" + data["mem_total"] + " GB");
                                        $('#disk_space input').eq(0).val(data["disk_usage"].toFixed(0)).trigger('change');
                                        $('#disk_space h4').eq(1).text(data["disk_used"] + "/" + data["disk_total"] + " GB");
                                        $('#cpu_space input').eq(0).val(data["cpu_usage"].toFixed(0)).trigger('change');
                                        $('#cpu_space h4').eq(1).text(data["cpu_usage"] + " %")


                                        $("#all_host_ip").val(data.all_host_ip);
                                        $("#host_file").val(data.host_file);


                                    } else {
                                        alert(data.data);
                                        $("#loading2").hide();
                                        $("#form_div").hide();
                                    }
                                },
                                error: function (e) {
                                    alert("页面出现错误，请于管理员联系。");
                                    $("#loading2").hide();
                                    $("#form_div").hide();
                                }
                            });
                            var os_image = data.node.original.kvm_template.os_image;
                            var disk_image = data.node.original.kvm_template.disk_image;
                            var base_image = data.node.original.kvm_template.base_image;
                            var windb_image = data.node.original.kvm_template.windb_image;
                            var linuxdb_image = data.node.original.kvm_template.linuxdb_image;

                            $('#select_kvm_template').empty();
                            $('#select_kvm_storage').empty();

                            var os_image_pre = '<optgroup label="' + '/home/images/os-image' + '" class="dropdown-header">';
                            for (i = 0; i < os_image.length; i++) {
                                os_image_pre += '<option value="' + os_image[i] + '">' + os_image[i] + '</option>'
                            }
                            os_image_pre += '</optgroup>';
                            $('#select_kvm_template').append(os_image_pre);

                            var disk_image_pre = '<option selected value="" ></option>';
                            disk_image_pre += '<optgroup label="' + '/home/images/disk-image' + '" class="dropdown-header">';
                            for (i = 0; i < disk_image.length; i++) {
                                disk_image_pre += '<option value="' + disk_image[i] + '">' + disk_image[i] + '</option>'
                            }
                            disk_image_pre += '</optgroup>';

                            disk_image_pre += '<optgroup label="' + '/home/images/windb-image' + '" class="dropdown-header">';
                            for (i = 0; i < windb_image.length; i++) {
                                disk_image_pre += '<option value="' + windb_image[i] + '">' + windb_image[i] + '</option>'
                            }
                            disk_image_pre += '</optgroup>';

                            disk_image_pre += '<optgroup label="' + '/home/images/linuxdb-image' + '" class="dropdown-header">';
                            for (i = 0; i < linuxdb_image.length; i++) {
                                disk_image_pre += '<option value="' + linuxdb_image[i] + '">' + linuxdb_image[i] + '</option>'
                            }
                            disk_image_pre += '</optgroup>';

                            disk_image_pre += '<optgroup label="' + '/home/images/base-image' + '" class="dropdown-header">';
                            for (i = 0; i < base_image.length; i++) {
                                disk_image_pre += '<option value="' + base_image[i] + '">' + base_image[i] + '</option>'
                            }
                            disk_image_pre += '</optgroup>';

                            $('#select_kvm_storage').append(disk_image_pre)
                        }
                        // KVM虚拟机
                        else {
                            $("#loading2").show();
                            $("#form_div").hide();

                            $.ajax({
                                type: "POST",
                                dataType: 'json',
                                url: "../get_kvm_detail/",
                                data: {
                                    kvm_id: kvm_id,
                                    utils_id: utils_id,
                                    kvm_name: kvm_name,
                                    utils_ip: utils_ip
                                },
                                success: function (data) {
                                    if (data.ret == 1) {
                                        $("#node").hide();
                                        $("#kvm_info").show();
                                        $("#loading2").hide();
                                        $("#form_div").show();
                                        // KVM虚机的基础信息页面展示数据
                                        var kvm_info = data.data.kvm_info_data;
                                        $("#kvm_cpu").val(kvm_info.kvm_cpu + '个');
                                        $("#kvm_memory").val(kvm_info.kvm_memory + 'MB');
                                        $("#kvm_disk").val(kvm_info.kvm_disk);
                                        $("#kvm_os").val(kvm_info.kvm_os);
                                        $("#kvm_ip").val(data.data.ip);
                                        $("#kvm_hostname").val(data.data.hostname);
                                        $("#kvm_password").val(data.data.password);

                                        $("#kvm_all_host_ip").val(kvm_info.all_host_ip);
                                        $("#kvm_host_file").val(kvm_info.host_file);


                                        // 任务栏：给电、断电、关闭、重启、暂停、唤醒、克隆、删除、激活按钮展示
                                        // kvmcopy表中没有此kvm虚拟机的信息，意为此虚机没有激活，只展示激活按钮，
                                        // 激活的虚机根据此虚机的状态展示：给电、断电、关闭、重启、暂停、唤醒、克隆、删除按钮
                                        if ($("#kvm_ip").val() == '' && $("#kvm_hostname").val() == '') {
                                            $("#kvm_suspend").hide();
                                            $("#kvm_resume").hide();
                                            $("#kvm_shutdown").hide();
                                            $("#kvm_reboot").hide();
                                            $("#kvm_clone").hide();
                                            $("#kvm_destroy").hide();
                                            $("#kvm_start").hide();
                                            $("#kvm_undefine").hide();
                                            $("#kvm_edit_cpu_mem").hide();
                                            $("#kvm_power").show();
                                        } else if ($("#kvm_ip").val() != '' && $("#kvm_hostname").val() != '') {
                                            $("#kvm_suspend").show();
                                            $("#kvm_resume").show();
                                            $("#kvm_shutdown").show();
                                            $("#kvm_reboot").show();
                                            $("#kvm_clone").show();
                                            $("#kvm_destroy").show();
                                            $("#kvm_start").show();
                                            $("#kvm_undefine").show();
                                            $("#kvm_edit_cpu_mem").show();
                                            $("#kvm_power").hide();
                                            if ($("#kvm_state").val() == '运行中') {
                                                $("#kvm_start").hide();
                                                $("#kvm_resume").hide();
                                                $("#kvm_undefine").hide();
                                                $("#kvm_clone").hide();
                                                $("#kvm_shutdown").show();
                                                $("#kvm_destroy").show();
                                                $("#kvm_suspend").show();
                                                $("#kvm_reboot").show();
                                                $("#kvm_edit_cpu_mem").hide();
                                            } else if ($("#kvm_state").val() == '关闭') {
                                                $("#kvm_start").show();
                                                $("#kvm_resume").hide();
                                                $("#kvm_suspend").hide();
                                                $("#kvm_shutdown").hide();
                                                $("#kvm_destroy").hide();
                                                $("#kvm_reboot").hide();
                                                $("#kvm_clone").show();
                                                $("#kvm_undefine").show();
                                                $("#kvm_edit_cpu_mem").show();
                                            } else if ($("#kvm_state").val() == '暂停') {
                                                $("#kvm_start").hide();
                                                $("#kvm_shutdown").hide();
                                                $("#kvm_resume").show();
                                                $("#kvm_suspend").hide();
                                                $("#kvm_destroy").show();
                                                $("#kvm_clone").show();
                                                $("#kvm_reboot").hide();
                                                $("#kvm_undefine").hide();
                                                $("#kvm_edit_cpu_mem").hide();
                                            }
                                        }
                                        // 内存空间使用情况、cpu使用率、磁盘空间使用情况信息根据虚机的状态展示
                                        var kvm_diskcpumemory_data = data.data.kvm_diskcpumemory_data;
                                        if ($("#kvm_state").val() == '运行中' || $("#kvm_state").val() == '暂停') {
                                            $('#kvm_memory_space input').eq(0).val(kvm_diskcpumemory_data["mem_usage"].toFixed(0)).trigger('change');
                                            $('#kvm_memory_space h4').eq(1).text(kvm_diskcpumemory_data["mem_used"] + "/" + kvm_diskcpumemory_data["mem_total"] + " GB");
                                            if (kvm_diskcpumemory_data["cpu_usage"] < 0.5) {
                                                $('#kvm_cpu_space input').eq(0).val(1).trigger('change');
                                            } else {
                                                $('#kvm_cpu_space input').eq(0).val(kvm_diskcpumemory_data["cpu_usage"].toFixed(0)).trigger('change');
                                            }
                                            $('#kvm_cpu_space h4').eq(1).text(kvm_diskcpumemory_data["cpu_usage"] + " %")
                                        }

                                        if ($("#kvm_state").val() == '关闭') {
                                            $('#kvm_memory_space input').eq(0).val(0).trigger('change');
                                            $('#kvm_memory_space h4').eq(1).text(0 + "/" + (kvm_info.kvm_memory / 1024).toFixed(2) + " GB");
                                            $('#kvm_cpu_space input').eq(0).val(0).trigger('change');
                                            $('#kvm_cpu_space h4').eq(1).text('0' + " %");
                                        }

                                        $('#kvm_disk_space input').eq(0).val(kvm_diskcpumemory_data["disk_usage"]).trigger('change');
                                        $('#kvm_disk_space h4').eq(1).text(kvm_diskcpumemory_data["disk_used"] + "/" + kvm_diskcpumemory_data["disk_total"] + " GB");
                                    } else {
                                        alert(data.data);
                                        $("#loading2").hide();
                                        $("#form_div").hide();
                                    }
                                },
                                error: function (e) {
                                    alert("页面出现错误，请于管理员联系。");
                                    $("#loading2").hide();
                                    $("#form_div").hide();
                                }
                            });
                        }
                    });
            }
        }
    });

}


$(document).ready(function () {
    $('#loading').show();
    $('#showdata').hide();
    // 加载树
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
    // 完成开机、关机、暂停、运行、断电后重新获取kvm虚拟机的cpu、内存使用信息
    function get_kvm_task_data() {
        $.ajax({
            type: "POST",
            dataType: 'json',
            url: "../get_kvm_task_data/",
            data: {
                kvm_id: $("#kvm_id").val(),
                utils_id: $("#utils_id").val(),
                kvm_name: $("#kvm_name").val(),
                utils_ip: $("#utils_ip").val(),
            },
            success: function (data) {
                if (data.ret == 1) {
                    $("#node").hide();
                    $("#kvm_info").show();
                    $("#loading2").hide();
                    $("#form_div").show();

                    if ($("#kvm_ip").val() == '' && $("#kvm_hostname").val() == '') {
                        $("#kvm_suspend").hide();
                        $("#kvm_resume").hide();
                        $("#kvm_shutdown").hide();
                        $("#kvm_reboot").hide();
                        $("#kvm_clone").hide();
                        $("#kvm_destroy").hide();
                        $("#kvm_start").hide();
                        $("#kvm_undefine").hide();
                        $("#kvm_edit_cpu_mem").hide();
                        $("#kvm_power").show();
                    } else if ($("#kvm_ip").val() != '' && $("#kvm_hostname").val() != '') {
                        $("#kvm_suspend").show();
                        $("#kvm_resume").show();
                        $("#kvm_shutdown").show();
                        $("#kvm_reboot").show();
                        $("#kvm_clone").show();
                        $("#kvm_destroy").show();
                        $("#kvm_start").show();
                        $("#kvm_undefine").show();
                        $("#kvm_edit_cpu_mem").show();
                        $("#kvm_power").hide();
                        if ($("#kvm_state").val() == '运行中') {
                            $("#kvm_start").hide();
                            $("#kvm_resume").hide();
                            $("#kvm_undefine").hide();
                            $("#kvm_clone").hide();
                            $("#kvm_shutdown").show();
                            $("#kvm_destroy").show();
                            $("#kvm_suspend").show();
                            $("#kvm_reboot").show();
                            $("#kvm_edit_cpu_mem").hide();
                        } else if ($("#kvm_state").val() == '关闭') {
                            $("#kvm_start").show();
                            $("#kvm_resume").hide();
                            $("#kvm_suspend").hide();
                            $("#kvm_shutdown").hide();
                            $("#kvm_destroy").hide();
                            $("#kvm_reboot").hide();
                            $("#kvm_clone").show();
                            $("#kvm_undefine").show();
                            $("#kvm_edit_cpu_mem").show();
                        } else if ($("#kvm_state").val() == '暂停') {
                            $("#kvm_start").hide();
                            $("#kvm_shutdown").hide();
                            $("#kvm_resume").show();
                            $("#kvm_suspend").hide();
                            $("#kvm_destroy").show();
                            $("#kvm_clone").show();
                            $("#kvm_reboot").hide();
                            $("#kvm_undefine").hide();
                            $("#kvm_edit_cpu_mem").hide();
                        }
                    }

                    var mem_cpu_data = data.data.kvm_cpu_mem_data;
                    if ($("#kvm_state").val() == '运行中' || $("#kvm_state").val() == '暂停') {
                        $('#kvm_memory_space input').eq(0).val(mem_cpu_data["mem_usage"].toFixed(0)).trigger('change');
                        $('#kvm_memory_space h4').eq(1).text(mem_cpu_data["mem_used"] + "/" + mem_cpu_data["mem_total"] + " GB");
                        if (mem_cpu_data["cpu_usage"] < 0.5) {
                            $('#kvm_cpu_space input').eq(0).val(1).trigger('change');
                        } else if (mem_cpu_data["cpu_usage"] == 0){
                            $('#kvm_cpu_space input').eq(0).val(0).trigger('change');
                        }
                        else {
                            $('#kvm_cpu_space input').eq(0).val(mem_cpu_data["cpu_usage"].toFixed(0)).trigger('change');
                        }
                        $('#kvm_cpu_space h4').eq(1).text(mem_cpu_data["cpu_usage"] + " %")
                    }

                    if ($("#kvm_state").val() == '关闭') {
                        var kvm_memory = $('#kvm_memory').val().replace('MB', '');
                        $('#kvm_memory_space input').eq(0).val(0).trigger('change');
                        $('#kvm_memory_space h4').eq(1).text(0 + "/" + (parseInt(kvm_memory)/1024).toFixed(2) + " GB");
                        $('#kvm_cpu_space input').eq(0).val(0).trigger('change');
                        $('#kvm_cpu_space h4').eq(1).text('0' + " %");
                    }

                } else {
                    alert(data.data);
                    $("#loading2").hide();
                    $("#form_div").show();
                }
            },
            error: function (e) {
                alert("页面出现错误，请于管理员联系。");
                $("#loading2").hide();
                $("#form_div").show();
            }
        });
    };
    // 暂停虚机
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
                    },
                success: function (data) {
                    if (data.ret == 0) {
                        alert(data.data)
                    } else {
                        var myres = data["data"];
                        var kvm_id = data["kvm_id"];
                        if (myres == "暂停成功。") {
                            $('#kvm_state').val('暂停');
                            $('#kvm_id').val(kvm_id);

                            //重新获取kvm虚拟机的cpu、内存使用信息
                            get_kvm_task_data();

                            //设置节点图标：开机、关机状态
                            var curnode = $('#tree_kvm_manage').jstree('get_node', $("#id").val());
                            var newtext = curnode.text.replace("<span class='fa fa-desktop' style='color:green; height:24px;'></span> ", "<span class='fa fa-desktop' style='color:red; height:24px;'></span> ");
                            $('#tree_kvm_manage').jstree('set_text', $("#id").val(), newtext);

                            // 完成开机、关机、暂停、运行、断电后重新设置虚拟机的id和状态
                            //  完成克隆后点击激活虚机，没有刷新页面，点击暂停，data为空，判断data数据，重新加载虚机id和状态
                            if (curnode.data){
                                curnode.data.id = data["kvm_id"];
                                curnode.data.state = '暂停'
                            }else {
                                curnode.original.kvm_id = data["kvm_id"];
                                curnode.original.kvm_state = '暂停'
                            }
                        }
                        alert(myres);
                    }
                },
                error: function (e) {
                    alert("页面出现错误，请于管理员联系。");
                }
            });
        }
    });
    // 唤醒虚机
    $('#kvm_resume').click(function () {
        $.ajax({
            type: "POST",
            dataType: 'json',
            url: "../kvm_resume/",
            data:
                {
                    utils_id: $("#utils_id").val(),
                    kvm_name: $("#kvm_name").val(),
                },
            success: function (data) {
                if (data.ret == 0) {
                        alert(data.data)
                } else {
                    var myres = data["data"];
                    var kvm_id = data["kvm_id"];
                    if (myres == "唤醒成功。") {
                        $('#kvm_state').val('运行中');
                        $('#kvm_id').val(kvm_id);

                        get_kvm_task_data();
                        var curnode = $('#tree_kvm_manage').jstree('get_node', $("#id").val());

                        var newtext = curnode.text.replace("<span class='fa fa-desktop' style='color:red; height:24px;'></span> ", "<span class='fa fa-desktop' style='color:green; height:24px;'></span> ");
                        $('#tree_kvm_manage').jstree('set_text', $("#id").val(), newtext);
                        // 完成开机、关机、暂停、运行、断电后重新设置虚拟机的id和状态
                        //  完成克隆后点击激活虚机，没有刷新页面，点击唤醒，data为空，判断data数据，重新加载虚机id和状态
                        if (curnode.data){
                            curnode.data.id = data["kvm_id"];
                            curnode.data.state = '运行中'
                        }else {
                            curnode.original.kvm_id = data["kvm_id"];
                            curnode.original.kvm_state = '运行中'
                        }
                    }
                    alert(myres);
                }
            },
            error: function (e) {
                alert("页面出现错误，请于管理员联系。");
            }
        });

    });
    // 关闭虚机
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
                    },
                success: function (data) {
                    if (data.ret == 0) {
                        alert(data.data)
                    } else {
                        var myres = data["data"];
                        var kvm_id = data["kvm_id"];
                        if (myres == "关闭成功。") {
                            $('#kvm_state').val('关闭');
                            $('#kvm_id').val(kvm_id);
                            get_kvm_task_data();
                            var curnode = $('#tree_kvm_manage').jstree('get_node', $("#id").val());
                            var newtext = curnode.text.replace("<span class='fa fa-desktop' style='color:green; height:24px;'></span> ", "<span class='fa fa-desktop' style='color:red; height:24px;'></span> ");
                            $('#tree_kvm_manage').jstree('set_text', $("#id").val(), newtext);

                            // 完成开机、关机、暂停、运行、断电后重新设置虚拟机的id和状态
                            //  完成克隆后点击激活虚机，没有刷新页面，点击关闭，data为空，判断data数据，重新加载虚机id和状态
                            if (curnode.data){
                                curnode.data.id = data["kvm_id"];
                                curnode.data.state = '关闭'
                            }else {
                                curnode.original.kvm_id = data["kvm_id"];
                                curnode.original.kvm_state = '关闭'
                            }
                        }
                        alert(myres);
                    }
                },
                error: function (e) {
                    alert("页面出现错误，请于管理员联系。");
                }
            });
        }
    });
    // 重启虚机
    $('#kvm_reboot').click(function () {
        $.ajax({
            type: "POST",
            dataType: 'json',
            url: "../kvm_reboot/",
            data:
                {
                    utils_id: $("#utils_id").val(),
                    kvm_name: $("#kvm_name").val(),
                },
            success: function (data) {
                if (data.ret == 0) {
                    alert(data.data)
                } else {
                    var myres = data["data"];
                    var kvm_id = data["kvm_id"];
                    if (myres == "重启成功。") {
                        $('#kvm_state').val('运行中');
                        $('#kvm_id').val(kvm_id);
                        get_kvm_task_data();
                        var curnode = $('#tree_kvm_manage').jstree('get_node', $("#id").val());

                        // 完成开机、关机、暂停、运行、断电后重新设置虚拟机的id和状态
                        //  完成克隆后点击激活虚机，没有刷新页面，点击重启，data为空，判断data数据，重新加载虚机id和状态
                        if (curnode.data){
                            curnode.data.id = data["kvm_id"];
                            curnode.data.state = '运行中'
                        }else {
                            curnode.original.kvm_id = data["kvm_id"];
                            curnode.original.kvm_state = '运行中'
                        }
                    }
                    alert(myres);
                }
            },
            error: function (e) {
                alert("页面出现错误，请于管理员联系。");
            }
        });

    });
    // 断电虚机
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
                    },
                success: function (data) {
                    if (data.ret == 0) {
                        alert(data.data)
                    } else {
                        var myres = data["data"];
                        var kvm_id = data["kvm_id"];
                        if (myres == "断电成功。") {
                            $('#kvm_state').val('关闭');
                            $('#kvm_id').val(kvm_id);
                            get_kvm_task_data();
                            var curnode = $('#tree_kvm_manage').jstree('get_node', $("#id").val());
                            var newtext = curnode.text.replace("<span class='fa fa-desktop' style='color:green; height:24px;'></span> ", "<span class='fa fa-desktop' style='color:red; height:24px;'></span> ");
                            $('#tree_kvm_manage').jstree('set_text', $("#id").val(), newtext);

                            // 完成开机、关机、暂停、运行、断电后重新设置虚拟机的id和状态
                            // 完成克隆后点击激活虚机，没有刷新页面，点击断电，data为空，判断data数据，重新加载虚机id和状态
                            if (curnode.data){
                                curnode.data.id = data["kvm_id"];
                                curnode.data.state = '关闭'
                            }else {
                                curnode.original.kvm_id = data["kvm_id"];
                                curnode.original.kvm_state = '关闭'
                            }
                        }
                        alert(myres);
                    }
                },
                error: function (e) {
                    alert("页面出现错误，请于管理员联系。");
                }
            });
        }
    });
    // 给电虚机
    $('#kvm_start').click(function () {
        $.ajax({
            type: "POST",
            dataType: 'json',
            url: "../kvm_start/",
            data:
                {
                    utils_id: $("#utils_id").val(),
                    kvm_name: $("#kvm_name").val(),
                },
            success: function (data) {
                if (data.ret == 0) {
                    alert(data.data)
                } else {
                    var myres = data["data"];
                    var kvm_id = data["kvm_id"];
                    if (myres == "给电成功。") {
                        $('#kvm_state').val('运行中');
                        $('#kvm_id').val(kvm_id);

                        //重新获取kvm虚拟机的cpu、内存使用信息
                        get_kvm_task_data();

                        //设置节点图标：开机、关机状态
                        var curnode = $('#tree_kvm_manage').jstree('get_node', $("#id").val());
                        var newtext = curnode.text.replace("<span class='fa fa-desktop' style='color:red; height:24px;'></span> ", "<span class='fa fa-desktop' style='color:green; height:24px;'></span> ");
                        $('#tree_kvm_manage').jstree('set_text', $("#id").val(), newtext);

                        // 完成开机、关机、暂停、运行、断电后重新设置虚拟机的id和状态
                        //  完成克隆后点击激活虚机，没有刷新页面，点击开机，data为空，判断data数据，重新加载虚机id和状态
                        if (curnode.data){
                            curnode.data.id = data["kvm_id"];
                            curnode.data.state = '运行中'
                        }else {
                            curnode.original.kvm_id = data["kvm_id"];
                            curnode.original.kvm_state = '运行中'
                        }
                    }
                    alert(myres);
                }
            },
            error: function (e) {
                alert("页面出现错误，请于管理员联系。");
            }
        });
    });
    // 删除虚机
    $('#kvm_undefine').click(function () {
        if (confirm("确定要删除该虚拟机？")) {
            $.ajax({
                type: "POST",
                url: "../kvm_delete/",
                data:
                    {
                        utils_id: $("#utils_id").val(),
                        kvm_name: $("#kvm_name").val(),
                    },
                success: function (data) {
                    if (data.ret == 0) {
                        alert(data.data)
                    } else {
                        var myres = data["data"];
                        if (myres == "删除成功。") {
                            //树节点移除此虚机
                            var ref = $('#tree_kvm_manage').jstree(true),
                            sel = ref.get_selected();
                            ref.delete_node(sel);
                        }
                        alert(myres);
                    }
                },
                error: function (e) {
                    alert("删除失败，请于管理员联系。");
                }
            });
        }

    });
    // 克隆虚机弹出填写信息
    $('#kvm_clone').click(function () {
        $('#static01').modal('show');
        $('#loading1').hide();
        $('#kvm_clone_div').show();
        $('#kvm_name_old').val($('#kvm_name').val());
        $('#kvm_name_new').val('')
    });
    // 克隆虚机
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
                    kvm_name: $("#kvm_name_old").val(),
                    kvm_clone_name: $("#kvm_name_new").val(),
                },
            success: function (data) {
                if (data.ret == 0) {
                    alert(data.data);
                    $('#loading1').hide();
                    $('#kvm_clone_div').show();
                } else {
                    var myres = data["data"];
                    if (myres == "克隆成功。") {
                        // 克隆成功，树节点新增虚拟机
                        $('#tree_kvm_manage').jstree('create_node', $("#pid").val(), {
                            "utils_id": data["utils_id"],
                            "utils_ip": data["utils_ip"],
                            "kvm_name": $("#kvm_name_new").val(),
                            "kvm_state": '关闭',
                            "kvm_id": '-1',
                            "icon": false,
                            "text": "<span class='fa fa-desktop' style='color:red; height:24px;'></span> " + $("#kvm_name_new").val(),
                        }, "last", false, false);
                        $('#tree_kvm_manage').jstree('deselect_all');
                    }
                    alert(myres);
                    $('#loading1').hide();
                    $('#static01').modal('hide');
                }
            },
            error: function (e) {
                alert("页面出现错误，请于管理员联系。");
                $('#loading1').hide();
                $('#kvm_clone_div').show();
            }
        });
    });
    // 新建虚机弹出填写信息
    $('#create_kvm_div').click(function () {
        $('#static02').modal('show');
        $('#loading3').hide();
        $('#create_kvm_machine').show();
        $('#select_kvm_template').val('');
        $('#select_kvm_storage').val('');
        $('#kvm_template_name').val('');
        $('#alter_kvm_cpu').val('');
        $('#alter_kvm_memory').val('');

    });
    // 新建虚机
    $('#kvm_machine_create').click(function () {
        $('#create_kvm_machine').hide();
        $('#loading3').show();
        $.ajax({
            type: "POST",
            dataType: 'json',
            url: "../kvm_machine_create/",
            data:
                {
                    utils_id: $("#utils_id").val(),
                    kvm_template_name: $("#select_kvm_template").val(),
                    kvm_name: $("#kvm_template_name").val(),
                    kvm_storage: $("#select_kvm_storage").val(),
                    kvm_cpu: $("#alter_kvm_cpu").val(),
                    kvm_memory: $("#alter_kvm_memory").val(),
                },
            success: function (data) {
                if (data.ret == 0) {
                    alert(data.data);
                    $('#loading3').hide();
                    $('#create_kvm_machine').show();
                } else {
                    var myres = data["data"];
                    if (myres == "注册成功。") {
                        // 注册成功，树节点新增虚拟机
                        $('#tree_kvm_manage').jstree('create_node', $("#id").val(), {
                            "utils_id": data["utils_id"],
                            "utils_ip": data["utils_ip"],
                            "kvm_name": $("#kvm_template_name").val(),
                            "kvm_state": '关闭',
                            "kvm_id": '-1',
                            "icon": false,
                            "text": "<span class='fa fa-desktop' style='color:red; height:24px;'></span> " + $("#kvm_template_name").val(),
                        }, "last", false, false);
                        $('#tree_kvm_manage').jstree('deselect_all');
                    }
                    alert(myres);
                    $('#loading3').hide();
                    $('#static02').modal('hide');
                }
            },
            error: function (e) {
                alert("页面出现错误，请于管理员联系。");
                $('#loading3').hide();
                $('#create_kvm_machine').show();
            }
        });
    });
    // 激活虚机弹出填写信息
    $('#kvm_power').click(function () {
        $('#static03').modal('show');
        $('#loading4').hide();
        $('#ip_hostname_div').show();
        $('#alter_ip').val('');
        $('#alter_hostname').val($("#kvm_name").val());
        $('#alter_password').val('');
    });
    // 激活虚机
    $('#kvm_power_save').click(function () {
        $('#loading4').show();
        $('#ip_hostname_div').hide();
        $.ajax({
            type: "POST",
            dataType: 'json',
            url: "../kvm_power/",
            data:
                {
                    utils_id: $("#utils_id").val(),
                    kvm_name: $("#kvm_name").val(),
                    kvm_ip: $("#alter_ip").val(),
                    kvm_hostname: $("#alter_hostname").val(),
                    kvm_password: $("#alter_password").val(),
                },
            success: function (data) {
                if (data.ret == 0) {
                    alert(data.data);
                    $('#loading4').hide();
                    $('#ip_hostname_div').show();
                } else {
                    var myres = data["data"];
                    if (myres == "激活成功。") {
                        $('#kvm_state').val('运行中');
                        $('#kvm_id').val(data["kvm_id"]);
                        $("#kvm_ip").val(data["ip"]);
                        $("#kvm_hostname").val(data["hostname"]);
                        $("#kvm_password").val(data["password"]);

                        //重新获取kvm虚拟机的cpu、内存使用信息
                        get_kvm_task_data();

                        //设置节点图标：开机、关机状态
                        var curnode = $('#tree_kvm_manage').jstree('get_node', $("#id").val());
                        var newtext = curnode.text.replace("<span class='fa fa-desktop' style='color:red; height:24px;'></span> ", "<span class='fa fa-desktop' style='color:green; height:24px;'></span> ");
                        $('#tree_kvm_manage').jstree('set_text', $("#id").val(), newtext);

                        // 完成克隆后点击激活虚机，data为空，判断data数据，重新加载虚机id和状态
                        if (curnode.data){
                            curnode.data.id = data["kvm_id"];
                            curnode.data.state = '运行中'
                        }else {
                            curnode.original.kvm_id = data["kvm_id"];
                            curnode.original.kvm_state = '运行中'
                        }
                    }
                    alert(myres);
                    $('#loading4').hide();
                    $('#static03').modal('hide');
                }
            },
            error: function (e) {
                alert("页面出现错误，请于管理员联系。");
                $('#loading4').hide();
                $('#ip_hostname_div').show();
            }
        });
    });
    // 编辑虚机弹出填写信息：cpu与内存修改
    $('#kvm_edit_cpu_mem').click(function () {
        $('#static04').modal('show');
        $('#loading5').hide();
        $('#alert_cpu_memory_div').show();
        $('#edit_kvm_cpu').val('');
        $('#edit_kvm_memory').val('');
    });
    // 虚机编辑：修改cpu与内存
    $('#kvm_cpu_memory_save').click(function () {
        $('#alert_cpu_memory_div').hide();
        $('#loading5').show();
        $.ajax({
            type: "POST",
            dataType: 'json',
            url: "../kvm_cpu_memory_save/",
            data:
                {
                    utils_id: $("#utils_id").val(),
                    kvm_name: $("#kvm_name").val(),
                    kvm_cpu: $("#edit_kvm_cpu").val(),
                    kvm_memory: $("#edit_kvm_memory").val(),
                },
            success: function (data) {
                if (data.ret == 0) {
                    alert(data.data);
                    $('#loading5').hide();
                    $('#alert_cpu_memory_div').show();
                } else {
                    var myres = data["data"];
                    if (myres == "保存成功。") {
                        //重新获取kvm虚拟机的cpu、内存使用信息
                        $("#kvm_cpu").val($("#edit_kvm_cpu").val() + '个');
                        $("#kvm_memory").val($("#edit_kvm_memory").val() + 'MB');
                        get_kvm_task_data();
                    }
                    alert(myres);
                    $('#loading5').hide();
                    $('#static04').modal('hide');
                }
            },
            error: function (e) {
                alert("页面出现错误，请于管理员联系。");
                $('#loading5').hide();
                $('#alert_cpu_memory_div').show();
            }
        });
    });

});