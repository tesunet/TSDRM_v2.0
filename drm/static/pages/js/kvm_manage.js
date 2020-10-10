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
                        var kvm_id = data.node.data.id;
                        var utils_id = data.node.data.utils_id;
                        var kvm_name = data.node.data.name;
                        $("#form_div").show();
                        var type = data.node.original.type;
                        $("#type").val(type);
                        $("#id").val(data.node.id);
                        $("#pid").val(data.node.parent);
                        $("#utils_id").val(utils_id);
                        $("#kvm_id").val(kvm_id);
                        $("#my_type").val(type);
                        $("#title").text(data.node.data.name);
                        $('#pname').val(data.node.data.pname);

                        // 根节点
                        if (data.node.parent == "#") {
                            $("#loading2").show();
                            $("#form_div").hide();
                            var utils_ip = data.node.original.kvm_credit.KvmHost;
                            $("#host_ip").val(utils_ip);

                            $.ajax({
                                type: "POST",
                                dataType: 'json',
                                url: "../get_kvm_detail/",
                                data: {
                                    utils_id: utils_id,
                                    utils_ip: utils_ip
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
                             $('#select_kvm_storage').append(disk_image_pre)
                        }
                        // 虚拟机
                        else {
                            $("#loading2").show();
                            $("#form_div").hide();
                            var kvm_info = data.node.data;
                            $("#kvm_name").val(kvm_info.name);
                            $("#kvm_state").val(kvm_info.state);
                            var utils_ip = data.node.original.ip;
                            $("#utils_ip").val(utils_ip);

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
                                        var kvm_info = data.data.kvm_info_data;
                                        $("#kvm_cpu").val(kvm_info.kvm_cpu + '个');
                                        $("#kvm_memory").val(kvm_info.kvm_memory + 'MB');
                                        $("#kvm_disk").val(kvm_info.kvm_disk);
                                        $("#kvm_os").val(kvm_info.kvm_os);
                                        $("#kvm_ip").val(data.data.ip);
                                        $("#kvm_hostname").val(data.data.hostname);
                                        $("#kvm_password").val(data.data.password);
                                        if (type == 'KVM') {
                                            $("#kvm_undefine").hide();
                                            $("#kvm_clone").hide();
                                            if ($("#kvm_ip").val() == '' && $("#kvm_hostname").val() == '') {
                                            $("#kvm_power_div").show();
                                            $("#kvm_task_div").hide();

                                            } else if ($("#kvm_ip").val() != '' && $("#kvm_hostname").val() != '') {
                                                $("#kvm_power_div").hide();
                                                $("#kvm_task_div").show();
                                                if ($("#kvm_state").val() == '运行中') {
                                                    $("#kvm_start").hide();
                                                    $("#kvm_resume").hide();
                                                    $("#kvm_shutdown").show();
                                                    $("#kvm_destroy").show();
                                                    $("#kvm_suspend").show();
                                                    $("#kvm_reboot").show();
                                                } else if ($("#kvm_state").val() == '关闭') {
                                                    $("#kvm_start").show();
                                                    $("#kvm_resume").hide();
                                                    $("#kvm_suspend").hide();
                                                    $("#kvm_shutdown").hide();
                                                    $("#kvm_destroy").hide();
                                                    $("#kvm_reboot").hide();
                                                } else if ($("#kvm_state").val() == '暂停') {
                                                    $("#kvm_start").hide();
                                                    $("#kvm_shutdown").hide();
                                                    $("#kvm_resume").show();
                                                    $("#kvm_suspend").hide();
                                                    $("#kvm_destroy").show();
                                                    $("#kvm_reboot").hide();
                                                    $("#kvm_undefine").hide();
                                                }
                                            }
                                        }
                                        if (type == 'COPY') {
                                            $("#kvm_undefine").hide();
                                            $("#kvm_clone").hide();
                                            if ($("#kvm_ip").val() == '' && $("#kvm_hostname").val() == '') {
                                                $("#kvm_power_div").show();
                                                $("#kvm_task_div").hide();

                                            } else if ($("#kvm_ip").val() != '' && $("#kvm_hostname").val() != '') {
                                                $("#kvm_power_div").hide();
                                                $("#kvm_task_div").show();
                                                if ($("#kvm_state").val() == '运行中') {
                                                    $("#kvm_start").hide();
                                                    $("#kvm_resume").hide();
                                                    $("#kvm_shutdown").show();
                                                    $("#kvm_destroy").show();
                                                    $("#kvm_suspend").show();
                                                    $("#kvm_reboot").show();
                                                } else if ($("#kvm_state").val() == '关闭') {
                                                    $("#kvm_start").show();
                                                    $("#kvm_resume").hide();
                                                    $("#kvm_suspend").hide();
                                                    $("#kvm_shutdown").hide();
                                                    $("#kvm_destroy").hide();
                                                    $("#kvm_reboot").hide();
                                                    $("#kvm_undefine").show();
                                                } else if ($("#kvm_state").val() == '暂停') {
                                                    $("#kvm_start").hide();
                                                    $("#kvm_shutdown").hide();
                                                    $("#kvm_resume").show();
                                                    $("#kvm_suspend").hide();
                                                    $("#kvm_destroy").show();
                                                    $("#kvm_reboot").hide();
                                                }
                                            }
                                        }

                                        var mem_cpu_data = data.data.kvm_cpu_mem_data;
                                        var disk_data = data.data.kvm_disk_data;
                                        if ($("#kvm_state").val() == '运行中' || $("#kvm_state").val() == '暂停') {
                                            $('#kvm_memory_space input').eq(0).val(mem_cpu_data["mem_usage"].toFixed(0)).trigger('change');
                                            $('#kvm_memory_space h4').eq(1).text(mem_cpu_data["mem_used"] + "/" + mem_cpu_data["mem_total"] + " GB");
                                            if (mem_cpu_data["cpu_usage"] < 0.5) {
                                                $('#kvm_cpu_space input').eq(0).val(1).trigger('change');
                                            } else {
                                                $('#kvm_cpu_space input').eq(0).val(mem_cpu_data["cpu_usage"].toFixed(0)).trigger('change');
                                            }
                                            $('#kvm_cpu_space h4').eq(1).text(mem_cpu_data["cpu_usage"] + " %")
                                        }

                                        if ($("#kvm_state").val() == '关闭') {
                                            $('#kvm_memory_space input').eq(0).val(0).trigger('change');
                                            $('#kvm_memory_space h4').eq(1).text(0 + "/" + kvm_info.kvm_memory / 1024 + " GB");
                                            $('#kvm_cpu_space input').eq(0).val(0).trigger('change');
                                            $('#kvm_cpu_space h4').eq(1).text('0' + " %");
                                        }

                                        $('#kvm_disk_space input').eq(0).val(disk_data["disk_usage"]).trigger('change');
                                        $('#kvm_disk_space h4').eq(1).text(disk_data["disk_used"] + "/" + disk_data["disk_total"] + " GB");
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

    function get_kvm_task_data() {
        //完成开机、关机、暂停、运行、断电后重新获取kvm虚拟机的cpu、内存使用信息
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
                    var type = $("#type").val();
                    $("#node").hide();
                    $("#kvm_info").show();
                    $("#loading2").hide();
                    $("#form_div").show();

                    if (type == 'KVM') {
                        $("#kvm_undefine").hide();
                        if ($("#kvm_ip").val() == '' && $("#kvm_hostname").val() == '') {
                        $("#kvm_power_div").show();
                        $("#kvm_task_div").hide();

                        } else if ($("#kvm_ip").val() != '' && $("#kvm_hostname").val() != '') {
                            $("#kvm_power_div").hide();
                            $("#kvm_task_div").show();
                            if ($("#kvm_state").val() == '运行中') {
                                $("#kvm_start").hide();
                                $("#kvm_resume").hide();
                                $("#kvm_shutdown").show();
                                $("#kvm_destroy").show();
                                $("#kvm_suspend").show();
                                $("#kvm_reboot").show();
                            } else if ($("#kvm_state").val() == '关闭') {
                                $("#kvm_start").show();
                                $("#kvm_resume").hide();
                                $("#kvm_suspend").hide();
                                $("#kvm_shutdown").hide();
                                $("#kvm_destroy").hide();
                                $("#kvm_reboot").hide();
                            } else if ($("#kvm_state").val() == '暂停') {
                                $("#kvm_start").hide();
                                $("#kvm_shutdown").hide();
                                $("#kvm_resume").show();
                                $("#kvm_suspend").hide();
                                $("#kvm_destroy").show();
                                $("#kvm_reboot").hide();
                                $("#kvm_undefine").hide();
                            }
                        }
                    }
                    if (type == 'COPY') {
                        $("#kvm_undefine").hide();
                        $("#kvm_clone").hide();
                        if ($("#kvm_ip").val() == '' && $("#kvm_hostname").val() == '') {
                            $("#kvm_power_div").show();
                            $("#kvm_task_div").hide();

                        } else if ($("#kvm_ip").val() != '' && $("#kvm_hostname").val() != '') {
                            $("#kvm_power_div").hide();
                            $("#kvm_task_div").show();
                            if ($("#kvm_state").val() == '运行中') {
                                $("#kvm_start").hide();
                                $("#kvm_resume").hide();
                                $("#kvm_shutdown").show();
                                $("#kvm_destroy").show();
                                $("#kvm_suspend").show();
                                $("#kvm_reboot").show();
                            } else if ($("#kvm_state").val() == '关闭') {
                                $("#kvm_start").show();
                                $("#kvm_resume").hide();
                                $("#kvm_suspend").hide();
                                $("#kvm_shutdown").hide();
                                $("#kvm_destroy").hide();
                                $("#kvm_reboot").hide();
                                $("#kvm_undefine").show();
                            } else if ($("#kvm_state").val() == '暂停') {
                                $("#kvm_start").hide();
                                $("#kvm_shutdown").hide();
                                $("#kvm_resume").show();
                                $("#kvm_suspend").hide();
                                $("#kvm_destroy").show();
                                $("#kvm_reboot").hide();
                            }
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
                        $('#kvm_memory_space h4').eq(1).text(0 + "/" + parseInt(kvm_memory)/1024 + " GB");
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
                        curnode.data.id = kvm_id;
                        curnode.data.state = '暂停';

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
                var kvm_id = data["kvm_id"];
                if (myres == "运行成功。") {
                    $('#kvm_state').val('运行中');
                    $('#kvm_id').val(kvm_id);

                    get_kvm_task_data();
                    var curnode = $('#tree_kvm_manage').jstree('get_node', $("#id").val());

                    var newtext = curnode.text.replace("<span class='fa fa-desktop' style='color:red; height:24px;'></span> ", "<span class='fa fa-desktop' style='color:green; height:24px;'></span> ");
                    $('#tree_kvm_manage').jstree('set_text', $("#id").val(), newtext);
                    curnode.data.id = kvm_id;
                    curnode.data.state = '运行中'
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
                    var kvm_id = data["kvm_id"];
                    if (myres == "关闭成功。") {
                        $('#kvm_state').val('关闭');
                        $('#kvm_id').val(kvm_id);
                        get_kvm_task_data();
                        var curnode = $('#tree_kvm_manage').jstree('get_node', $("#id").val());
                        var newtext = curnode.text.replace("<span class='fa fa-desktop' style='color:green; height:24px;'></span> ", "<span class='fa fa-desktop' style='color:red; height:24px;'></span> ");
                        $('#tree_kvm_manage').jstree('set_text', $("#id").val(), newtext);
                        curnode.data.id = kvm_id;
                        curnode.data.state = '关闭'

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
                var kvm_id = data["kvm_id"];
                if (myres == "重启成功。") {
                    $('#kvm_state').val('运行中');
                    $('#kvm_id').val(kvm_id);
                    get_kvm_task_data();
                    var curnode = $('#tree_kvm_manage').jstree('get_node', $("#id").val());
                    curnode.data.id = kvm_id;
                    curnode.data.state = '运行中'

                }
                alert(myres);
            },
            error: function (e) {
                alert("页面出现错误，请于管理员联系。");
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
                    var kvm_id = data["kvm_id"];
                    if (myres == "断电成功。") {
                        $('#kvm_state').val('关闭');
                        $('#kvm_id').val(kvm_id);
                        get_kvm_task_data();
                        var curnode = $('#tree_kvm_manage').jstree('get_node', $("#id").val());
                        var newtext = curnode.text.replace("<span class='fa fa-desktop' style='color:green; height:24px;'></span> ", "<span class='fa fa-desktop' style='color:red; height:24px;'></span> ");
                        $('#tree_kvm_manage').jstree('set_text', $("#id").val(), newtext);
                        curnode.data.id = kvm_id;
                        curnode.data.state = '关闭'

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
                var kvm_id = data["kvm_id"];
                if (myres == "开机成功。") {
                    $('#kvm_state').val('运行中');
                    $('#kvm_id').val(kvm_id);

                    //重新获取kvm虚拟机的cpu、内存使用信息
                    get_kvm_task_data();

                    //设置节点图标：开机、关机状态
                    var curnode = $('#tree_kvm_manage').jstree('get_node', $("#id").val());
                    var newtext = curnode.text.replace("<span class='fa fa-desktop' style='color:red; height:24px;'></span> ", "<span class='fa fa-desktop' style='color:green; height:24px;'></span> ");
                    $('#tree_kvm_manage').jstree('set_text', $("#id").val(), newtext);

                    // 完成开机、关机、暂停、运行、断电后重新设置虚拟机的id和状态
                    curnode.data.id = kvm_id;
                    curnode.data.state = '运行中'

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
                        location.reload()
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
                    location.reload()
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
    $('#kvm_machine_create').click(function () {
        $('#create_kvm_machine').hide();
        $('#loading3').show();

        var kvm_memory = $("#alter_kvm_memory").val();
        if (kvm_memory != ''){
            if (kvm_memory % 4 != 0){
                alter('内存大小必须为4MB的倍数。');
                $('#create_kvm_machine').show();
                $('#loading3').hide();
            }else{
                $.ajax({
                    type: "POST",
                    dataType: 'json',
                    url: "../kvm_machine_create/",
                    data:
                        {
                            utils_id: $("#utils_id").val(),
                            kvm_template: $("#select_kvm_template").val(),
                            kvm_template_name: $("#kvm_template_name").val(),
                            kvm_storage: $("#select_kvm_storage").val(),
                            kvm_cpu: $("#alter_kvm_cpu").val(),
                            kvm_memory: $("#alter_kvm_memory").val(),
                        },
                    success: function (data) {
                        var myres = data["res"];
                        if (myres == "新建成功。") {
                            $('#loading3').hide();
                            $('#create_kvm_machine').hide();
                            $('#static02').modal('hide');
                            location.reload()

                        }
                        alert(myres);
                        $('#loading3').hide();
                        $('#create_kvm_machine').show();
                    },
                    error: function (e) {
                        alert("页面出现错误，请于管理员联系。");
                        $('#loading3').hide();
                        $('#create_kvm_machine').show();
                    }
                });
            }
        }
        else{
            $.ajax({
                type: "POST",
                dataType: 'json',
                url: "../kvm_machine_create/",
                data:
                    {
                        utils_id: $("#utils_id").val(),
                        kvm_template: $("#select_kvm_template").val(),
                        kvm_template_name: $("#kvm_template_name").val(),
                        kvm_storage: $("#select_kvm_storage").val(),
                        kvm_cpu: $("#alter_kvm_cpu").val(),
                        kvm_memory: $("#alter_kvm_memory").val(),
                    },
                success: function (data) {
                    var myres = data["res"];
                    if (myres == "新建成功。") {
                        $('#loading3').hide();
                        $('#create_kvm_machine').hide();
                        $('#static02').modal('hide');
                        location.reload()

                    }
                    alert(myres);
                    $('#loading3').hide();
                    $('#create_kvm_machine').show();
                },
                error: function (e) {
                    alert("页面出现错误，请于管理员联系。");
                    $('#loading3').hide();
                    $('#create_kvm_machine').show();
                }
            });
        }

    });
    $('#kvm_power').click(function () {
        $('#static03').modal('show');
        $('#loading4').hide();
        $('#ip_hostname_div').show();
    });
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
                    kvm_state: $("#kvm_state").val(),
                    kvm_ip: $("#alter_ip").val(),
                    kvm_hostname: $("#alter_hostname").val(),
                    kvm_password: $("#alter_password").val(),

                },
            success: function (data) {
                var myres = data["res"];
                if (myres == "给电成功。") {
                    $('#loading4').hide();
                    $('#static03').hide();
                    $('#ip_hostname_div').hide();
                    var kvm_id = data["kvm_id"];
                    var kvm_ip = data["ip"];
                    var kvm_hostname = data["hostname"];
                    var kvm_password = data["password"];

                    $('#kvm_state').val('运行中');
                    $('#kvm_id').val(kvm_id);
                    $("#kvm_ip").val(kvm_ip);
                    $("#kvm_hostname").val(kvm_hostname);
                    $("#kvm_password").val(kvm_password);

                    //重新获取kvm虚拟机的cpu、内存使用信息
                    get_kvm_task_data();

                    //设置节点图标：开机、关机状态
                    var curnode = $('#tree_kvm_manage').jstree('get_node', $("#id").val());
                    var newtext = curnode.text.replace("<span class='fa fa-desktop' style='color:red; height:24px;'></span> ", "<span class='fa fa-desktop' style='color:green; height:24px;'></span> ");
                    $('#tree_kvm_manage').jstree('set_text', $("#id").val(), newtext);

                    // 完成给电后重新设置虚拟机的id和状态
                    curnode.data.id = kvm_id;
                    curnode.data.state = '运行中';

                }
                alert(myres);
                $('#loading4').hide();
                $('#ip_hostname_div').show();
            },
            error: function (e) {
                alert("页面出现错误，请于管理员联系。");
                $('#loading4').hide();
                $('#ip_hostname_div').show();
            }
        });
    });


});