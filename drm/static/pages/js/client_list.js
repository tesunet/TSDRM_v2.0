$(document).ready(function () {
    $("#loading1").show();
    $("#loading2").show();
    $("#loading3").show();
    $("#loading4").show();
    $("#loading5").show();

    function getClientsInfo(utils_manage_id) {
        $.ajax({
            type: 'POST',
            dataType: 'json',
            url: '../get_client_info/',
            data: {
                'utils_manage_id': utils_manage_id
            },
            success: function (data) {
                if (data.ret == 0) {
                    alert(data.data)
                } else {
                    var backup_status = data.data;
                    for (var i = 0; i < data.data.length; i++) {
                        var result = "";
                        result += "<tr>";
                        result += "<td>" + (i + 1) + "</td>";
                        result += "<td>" + data.data[i]["client_name"] + "</td>";
                        result += "<td>" + data.data[i]["network_interface"] + "</td>";
                        result += "<td>" + data.data[i]["galaxy_release"] + "</td>";
                        result += "<td>" + data.data[i]["os"] + "</td>";
                        result += "<td>" + data.data[i]["install_time"] + "</td>";
                        // if(data.data[i]["net"]=="中断")
                        //     result +="<td style='color: red'>" + data.data[i]["net"] + "</td>";
                        // else
                        //     result +="<td>" + data.data[i]["net"] + "</td>";

                        result += "</tr>";
                        $("#tbody1").append(result);
                    }

                    $("#loading1").hide();
                }
            }
        });
    }

    function getBackupStatus(utils_manage_id) {
        $.ajax({
            type: 'POST',
            dataType: 'json',
            url: '../get_backup_status/',
            data: {
                'utils_manage_id': utils_manage_id
            },
            success: function (data) {
                if (data.ret == 0) {
                    alert(data.data)
                } else {
                    var backup_status = data.data;

                    function get_status_label(job_status) {
                        var status_label = "label label-sm label-danger";
                        if (["运行", "正常", "等待", "QueuedCompleted", "Queued", "PartialSuccess", "成功"].indexOf(job_status) != -1) {
                            status_label = "label label-sm label-success"
                        }
                        if (["阻塞", "已完成，但有一个或多个错误", "已完成，但有一个或多个警告"].indexOf(job_status) != -1) {
                            status_label = "label label-sm label-warning"
                        }
                        if (job_status == "无") {
                            status_label = ""
                        }
                        return status_label;
                    }

                    var pre_clientname = "";
                    var pre_idataagent = "";
                    var pre_type = "";
                    var sort = 0;
                    for (var i = 0; i < backup_status.length; i++) {
                        var clientname_hidden = "";
                        var idataagent_hidden = "";
                        var type_hidden = "";

                        if (pre_clientname == backup_status[i]["clientname"]) {
                            // 非首个客户端
                            clientname_hidden = "display:none";
                        } else {
                            sort += 1;
                        }
                        if (pre_clientname == backup_status[i]["clientname"] && pre_idataagent == backup_status[i]["idataagent"]) {
                            idataagent_hidden = "display:none";
                        }
                        if (pre_clientname == backup_status[i]["clientname"] && pre_idataagent == backup_status[i]["idataagent"] && pre_type == backup_status[i]["type"]) {
                            type_hidden = "display:none";
                        }

                        var bk_status_label = get_status_label(backup_status[i].bk_status);
                        var aux_status_label = get_status_label(backup_status[i].aux_status);

                        $("#tbody2").append(
                            '<tr>' +
                            '<td rowspan="' + backup_status[i].clientname_rowspan + '" style="vertical-align:middle; ' + clientname_hidden + '">' + sort + '</td>' +
                            '<td rowspan="' + backup_status[i].clientname_rowspan + '" style="vertical-align:middle; ' + clientname_hidden + '">' + backup_status[i]["clientname"] + '</td>' +
                            '<td rowspan="' + backup_status[i].idataagent_rowspan + '" style="vertical-align:middle; ' + idataagent_hidden + '">' + backup_status[i]["idataagent"] + '</td>' +
                            '<td rowspan="' + backup_status[i].type_rowspan + '" style="vertical-align:middle; ' + type_hidden + '">' + backup_status[i]["type"] + '</td>' +
                            '<td style="vertical-align:middle">' + backup_status[i]["subclient"] + '</td>' +
                            '<td style="vertical-align:middle">' + backup_status[i]["startdate"] + '</td>' +
                            '<td style="vertical-align:middle"><span class="' + bk_status_label + '">' + backup_status[i]["bk_status"] + '</span></td>' +
                            '<td style="vertical-align:middle"><span class="' + aux_status_label + '">' + backup_status[i]["aux_status"] + '</span></td>' +
                            '</tr>'
                        );

                        pre_clientname = backup_status[i]["clientname"]
                        pre_idataagent = backup_status[i]["idataagent"]
                        pre_type = backup_status[i]["type"]
                    }
                    $("#loading2").hide();
                }
            }
        });
    }

    function getBackupContent(utils_manage_id) {
        $.ajax({
            type: 'POST',
            dataType: 'json',
            url: '../get_backup_content/',
            data: {
                'utils_manage_id': utils_manage_id
            },
            success: function (data) {
                if (data.ret == 0) {
                    alert(data.data)
                } else {
                    var backup_content = data.data;

                    var pre_clientname = "";
                    var pre_idataagent = "";
                    var pre_type = "";
                    var sort = 0;
                    for (var i = 0; i < backup_content.length; i++) {
                        var clientname_hidden = "";
                        var idataagent_hidden = "";
                        var type_hidden = "";

                        if (pre_clientname == backup_content[i]["clientname"]) {
                            // 非首个客户端
                            clientname_hidden = "display:none";
                        } else {
                            sort += 1;
                        }
                        if (pre_clientname == backup_content[i]["clientname"] && pre_idataagent == backup_content[i]["idataagent"]) {
                            idataagent_hidden = "display:none";
                        }
                        if (pre_clientname == backup_content[i]["clientname"] && pre_idataagent == backup_content[i]["idataagent"] && pre_type == backup_content[i]["type"]) {
                            type_hidden = "display:none";
                        }
                        // 备份大小、应用大小
                        var numbytescomp = (backup_content[i]["numbytescomp"] / 1024 / 1024 / 1024).toFixed(2)
                        var numbytesuncomp = (backup_content[i]["numbytesuncomp"] / 1024 / 1024 / 1024).toFixed(2)

                        $("#tbody3").append(
                            '<tr>' +
                            '<td rowspan="' + backup_content[i].clientname_rowspan + '" style="vertical-align:middle; ' + clientname_hidden + '">' + sort + '</td>' +
                            '<td rowspan="' + backup_content[i].clientname_rowspan + '" style="vertical-align:middle; ' + clientname_hidden + '">' + backup_content[i]["clientname"] + '</td>' +
                            '<td rowspan="' + backup_content[i].idataagent_rowspan + '" style="vertical-align:middle; ' + idataagent_hidden + '">' + backup_content[i]["idataagent"] + '</td>' +
                            '<td rowspan="' + backup_content[i].type_rowspan + '" style="vertical-align:middle; ' + type_hidden + '">' + backup_content[i]["type"] + '</td>' +
                            '<td style="vertical-align:middle">' + backup_content[i]["subclient"] + '</td>' +
                            '<td style="vertical-align:middle">' + backup_content[i]["content"] + '</td>' +
                            '<td style="vertical-align:middle">' + numbytesuncomp + ' GB</td>' +
                            '<td style="vertical-align:middle">' + numbytescomp + ' GB</td>' +
                            '</tr>'
                        );

                        pre_clientname = backup_content[i]["clientname"]
                        pre_idataagent = backup_content[i]["idataagent"]
                        pre_type = backup_content[i]["type"]
                    }
                    $("#loading3").hide();
                }
            }
        });
    }

    function getSchedulePolicy(utils_manage_id) {
        $.ajax({
            type: 'POST',
            dataType: 'json',
            url: '../get_schedule_policy/',
            data: {
                'utils_manage_id': utils_manage_id
            },
            success: function (data) {
                if (data.ret == 0) {
                    alert(data.data)
                } else {
                    var schedule_policy = data.data;

                    var pre_clientname = "";
                    var pre_idataagent = "";
                    var pre_type = "";
                    var pre_subclient = "";
                    var pre_scheduePolicy = "";
                    var pre_schedbackuptype = "";
                    var sort = 0;
                    for (var i = 0; i < schedule_policy.length; i++) {
                        var clientname_hidden = "";
                        var idataagent_hidden = "";
                        var type_hidden = "";
                        var subclient_hidden = "";
                        var scheduePolicy_hidden = "";
                        var schedbackuptype_hidden = "";

                        if (pre_clientname == schedule_policy[i]["clientname"]) {
                            // 非首个客户端
                            clientname_hidden = "display:none";
                        } else {
                            sort += 1;
                        }
                        if (pre_clientname == schedule_policy[i]["clientname"] && pre_idataagent == schedule_policy[i]["idataagent"]) {
                            idataagent_hidden = "display:none";
                        }
                        if (pre_clientname == schedule_policy[i]["clientname"] && pre_idataagent == schedule_policy[i]["idataagent"] && pre_type == schedule_policy[i]["type"]) {
                            type_hidden = "display:none";
                        }
                        if (pre_clientname == schedule_policy[i]["clientname"] && pre_idataagent == schedule_policy[i]["idataagent"] && pre_type == schedule_policy[i]["type"] && pre_subclient == schedule_policy[i]["subclient"]) {
                            subclient_hidden = "display:none";
                        }
                        if (pre_clientname == schedule_policy[i]["clientname"] && pre_idataagent == schedule_policy[i]["idataagent"] &&
                            pre_type == schedule_policy[i]["type"] && pre_subclient == schedule_policy[i]["subclient"] && pre_scheduePolicy == schedule_policy[i]["scheduePolicy"]) {
                            scheduePolicy_hidden = "display:none";
                        }
                        if (pre_clientname == schedule_policy[i]["clientname"] && pre_idataagent == schedule_policy[i]["idataagent"] &&
                            pre_type == schedule_policy[i]["type"] && pre_subclient == schedule_policy[i]["subclient"] && pre_scheduePolicy == schedule_policy[i]["scheduePolicy"] &&
                            pre_schedbackuptype == schedule_policy[i]["schedbackuptype"]) {
                            schedbackuptype_hidden = "display:none";
                        }
                        // 是否展示操作按钮
                        var disable_tag = ''
                        if (schedule_policy[i]["scheduePolicy"] == '无') {
                            disable_tag = 'disabled'
                        }

                        var schedbackupdayString = "";
                        if (schedule_policy[i]["option"]["schedbackupday"]) {
                            schedbackupdayString = '(' + schedule_policy[i]["option"]["schedbackupday"] + ')';
                        }

                        $("#tbody4").append(
                            '<tr>' +
                            '<td rowspan="' + schedule_policy[i]["clientname_rowspan"] + '" style="vertical-align:middle; ' + clientname_hidden + '">' + sort + '</td>' +
                            '<td rowspan="' + schedule_policy[i]["clientname_rowspan"] + '" style="vertical-align:middle; ' + clientname_hidden + '">' + schedule_policy[i]["clientname"] + '</td>' +
                            '<td rowspan="' + schedule_policy[i]["idataagent_rowspan"] + '" style="vertical-align:middle; ' + idataagent_hidden + '">' + schedule_policy[i]["idataagent"] + '</td>' +
                            '<td rowspan="' + schedule_policy[i]["type_rowspan"] + '" style="vertical-align:middle; ' + type_hidden + '">' + schedule_policy[i]["type"] + '</td>' +
                            '<td rowspan="' + schedule_policy[i]["subclient_rowspan"] + '" style="vertical-align:middle; ' + subclient_hidden + '">' + schedule_policy[i]["subclient"] + '</td>' +
                            '<td rowspan="' + schedule_policy[i]["scheduePolicy_rowspan"] + '" style="vertical-align:middle; ' + scheduePolicy_hidden + '">' + schedule_policy[i]["scheduePolicy"] + '</td>' +
                            '<td rowspan="' + schedule_policy[i]["schedbackuptype_rowspan"] + '" style="vertical-align:middle; ' + schedbackuptype_hidden + '">' + schedule_policy[i]["schedbackuptype"] + '</td>' +
                            '<td style="vertical-align:middle">' + schedule_policy[i]["schedpattern"] + schedbackupdayString + '</td>' +
                            '<td><button name="schedule_type" title="编辑" data-toggle="modal" data-target="#static" class="btn btn-xs btn-primary" type="button" ' + disable_tag + '><i class="fa fa-cogs"></i></button>' +
                            '<input value="' + schedule_policy[i]["option"]["scheduleName"] + '" hidden>' +
                            '<input value="' + schedule_policy[i]["option"]["schedpattern"] + '" hidden>' +
                            '<input value="' + schedule_policy[i]["option"]["schednextbackuptime"] + '" hidden>' +
                            '<input value="' + schedule_policy[i]["option"]["schedinterval"] + '" hidden>' +
                            '<input value="' + schedule_policy[i]["option"]["schedbackupday"] + '" hidden>' +
                            '<input value="' + schedule_policy[i]["option"]["schedbackuptype"] + '" hidden>' +
                            '</td>' +
                            '</tr>'
                        );

                        pre_clientname = schedule_policy[i]["clientname"]
                        pre_idataagent = schedule_policy[i]["idataagent"]
                        pre_type = schedule_policy[i]["type"]
                        pre_subclient = schedule_policy[i]["subclient"]
                        pre_scheduePolicy = schedule_policy[i]["scheduePolicy"]
                        pre_schedbackuptype = schedule_policy[i]["schedbackuptype"]
                    }
                    $("#loading4").hide();
                }
            }
        });
    }

    function getStoragePolicy(utils_manage_id) {
        $.ajax({
            type: 'POST',
            dataType: 'json',
            url: '../get_storage_policy/',
            data: {
                'utils_manage_id': utils_manage_id
            },
            success: function (data) {
                if (data.ret == 0) {
                    alert(data.data)
                } else {
                    var storage_policy = data.data;

                    var pre_clientname = "";
                    var pre_idataagent = "";
                    var pre_type = "";
                    var sort = 0;
                    for (var i = 0; i < storage_policy.length; i++) {
                        var clientname_hidden = "";
                        var idataagent_hidden = "";
                        var type_hidden = "";

                        if (pre_clientname == storage_policy[i]["clientname"]) {
                            // 非首个客户端
                            clientname_hidden = "display:none";
                        } else {
                            sort += 1;
                        }
                        if (pre_clientname == storage_policy[i]["clientname"] && pre_idataagent == storage_policy[i]["idataagent"]) {
                            idataagent_hidden = "display:none";
                        }
                        if (pre_clientname == storage_policy[i]["clientname"] && pre_idataagent == storage_policy[i]["idataagent"] && pre_type == storage_policy[i]["type"]) {
                            type_hidden = "display:none";
                        }

                        $("#tbody5").append(
                            '<tr>' +
                            '<td rowspan="' + storage_policy[i].clientname_rowspan + '" style="vertical-align:middle; ' + clientname_hidden + '">' + sort + '</td>' +
                            '<td rowspan="' + storage_policy[i].clientname_rowspan + '" style="vertical-align:middle; ' + clientname_hidden + '">' + storage_policy[i]["clientname"] + '</td>' +
                            '<td rowspan="' + storage_policy[i].idataagent_rowspan + '" style="vertical-align:middle; ' + idataagent_hidden + '">' + storage_policy[i]["idataagent"] + '</td>' +
                            '<td rowspan="' + storage_policy[i].type_rowspan + '" style="vertical-align:middle; ' + type_hidden + '">' + storage_policy[i]["type"] + '</td>' +
                            '<td style="vertical-align:middle">' + storage_policy[i]["subclient"] + '</td>' +
                            '<td style="vertical-align:middle">' + storage_policy[i]["storage_policy"] + '</td>' +
                            '</tr>'
                        );

                        pre_clientname = storage_policy[i]["clientname"]
                        pre_idataagent = storage_policy[i]["idataagent"]
                        pre_type = storage_policy[i]["type"]
                    }
                    $("#loading5").hide();
                }
            }
        });
    }

    function getMADiskSpace(utils_manage_id) {
        $.ajax({
            type: "POST",
            url: "../get_ma_disk_space/",
            data: {
                utils_id: utils_manage_id,
            },
            success: function (data) {
                var capacity_available_percent = 0,
                    space_reserved_percent = 0,
                    used_space_percent = 0;

                if (data.status == 1) {
                    capacity_available_percent = data.data.capacity_available_percent,
                        space_reserved_percent = data.data.space_reserved_percent,
                        used_space_percent = data.data.used_space_percent;
                }
                AmCharts.makeChart("disk_space_container", {
                    "type": "pie",
                    "theme": "light",
                    "fontSize": 15,
                    "fontFamily": 'Open Sans',

                    "color": '#000',
                    "colors": ["#228B22", "#FF6600", "#FF0F00"],

                    "dataProvider": [{
                        "name": "可用空间",
                        "value": capacity_available_percent
                    }, {
                        "name": "保留空间",
                        "value": space_reserved_percent
                    }, {
                        "name": "已用空间",
                        "value": used_space_percent
                    }],
                    "valueField": "value",
                    "titleField": "name",
                    "outlineAlpha": 0.4,
                    "depth3D": 15,
                    "balloonText": "[[title]]<br><span style='font-size:15px'><b>[[value]]</b> ([[percents]]%)</span>",
                    "angle": 30,
                });
            }
        });
    }

    function getDiskSpace(utils_manage_id) {
        $.ajax({
            type: 'POST',
            dataType: 'json',
            url: '../get_disk_space/',
            data: {
                'utils_manage_id': utils_manage_id
            },
            success: function (data) {
                if (data.status == 1) {
                    // 磁盘容量表
                    var disk_space = data.data;

                    var pre_display_name = "";
                    var pre_library_name = "";
                    var sort = 0;
                    for (var i = 0; i < disk_space.length; i++) {
                        var display_name_hidden = "";
                        var library_name_hidden = "";

                        if (pre_display_name == disk_space[i]["DisplayName"]) {
                            display_name_hidden = "display:none";
                        } else {
                            sort += 1;
                        }
                        if (pre_display_name == disk_space[i]["DisplayName"] && pre_library_name == disk_space[i]["LibraryName"]) {
                            library_name_hidden = "display:none";
                        }

                        // GB
                        var CapacityAvailable = (disk_space[i]["CapacityAvailable"] / 1024).toFixed(0)
                        var SpaceReserved = (disk_space[i]["SpaceReserved"] / 1024).toFixed(0)
                        var TotalSpaceMB = (disk_space[i]["TotalSpaceMB"] / 1024).toFixed(0)

                        $("tbody").append(
                            '<tr>' +
                            '<td rowspan="' + disk_space[i].display_name_rowspan + '" style="vertical-align:middle; ' + display_name_hidden + '">' + sort + '</td>' +
                            '<td rowspan="' + disk_space[i].display_name_rowspan + '" style="vertical-align:middle; ' + display_name_hidden + '">' + disk_space[i]["DisplayName"] + '</td>' +
                            '<td rowspan="' + disk_space[i].library_name_rowspan + '" style="vertical-align:middle; ' + library_name_hidden + '">' + disk_space[i]["LibraryName"] + '</td>' +
                            '<td style="vertical-align:middle">' + disk_space[i]["MountPathName"] + '</td>' +
                            '<td style="vertical-align:middle">' + CapacityAvailable + ' GB</td>' +
                            '<td style="vertical-align:middle">' + SpaceReserved + ' GB</td>' +
                            '<td style="vertical-align:middle">' + TotalSpaceMB + ' GB</td>' +
                            '<td style="vertical-align:middle">' + disk_space[i]["LastBackupTime"] + '</td>' +
                            '<td style="vertical-align:middle">' + disk_space[i]["Offline"] + '</td>' +
                            '<td style="vertical-align:middle"><button id="edit" title="图表" data-toggle="modal" data-target="#static01" class="btn btn-xs btn-primary" type="button"><input value="' + disk_space[i]["MediaID"] + '" hidden><i class="fa fa-bar-chart"></i></button></td>' +
                            '</tr>'
                        );

                        pre_display_name = disk_space[i]["DisplayName"]
                        pre_library_name = disk_space[i]["LibraryName"]
                    }
                    $("#loading").hide();
                } else {
                    alert(data.info);
                }
            }
        });
    }

    getClientsInfo($('#utils_manage').val());
    getBackupStatus($('#utils_manage').val());
    getBackupContent($('#utils_manage').val());
    getSchedulePolicy($('#utils_manage').val());
    getStoragePolicy($('#utils_manage').val());
    getMADiskSpace($('#utils_manage').val());
    getDiskSpace($('#utils_manage').val());

    // 点击事件
    $('#schedule tbody').on('click', 'button[name="schedule_type"]', function () {
        var siblingInput = $(this).siblings();
        $("#scheduleName").val(siblingInput[0].value);
        $("#schedpattern").val(siblingInput[1].value);
        $("#schednextbackuptime").val(siblingInput[2].value);
        $("#schedinterval").val(siblingInput[3].value);
        $("#schedbackupday").val(siblingInput[4].value);
        $("#schedbackuptype").val(siblingInput[5].value);
    });

    $('#utils_manage').change(function () {
        $("#tbody1").empty();
        $("#tbody2").empty();
        $("#tbody3").empty();
        $("#tbody4").empty();
        $("#tbody5").empty();

        $("#loading1").show();
        $("#loading2").show();
        $("#loading3").show();
        $("#loading4").show();
        $("#loading5").show();

        getClientsInfo($(this).val());
        getBackupStatus($(this).val());
        getBackupContent($(this).val());
        getSchedulePolicy($(this).val());
        getStoragePolicy($(this).val());
        getMADiskSpace($(this).val());
        getDiskSpace($(this).val());
    });

    var weeklyChart = new Highcharts.Chart({
        chart: {
            renderTo: 'disk_space_hc',
            style: {
                fontFamily: 'Open Sans'
            }
        },
        title: {
            text: '每周磁盘数据',
            x: -20 //center
        },

        xAxis: {
            title: {
                text: '周'
            },
            reversed: true,
        },
        colors: [
            '#3598dc',
            '#e7505a',
            '#32c5d2',
            '#8e44ad',
        ],
        yAxis: {
            title: {
                text: '容量 (GB)'
            },
            plotLines: [{
                value: 0,
                width: 1,
                color: '#808080'
            }]
        },
        tooltip: {
            valueSuffix: 'GB'
        },
        legend: {
            layout: 'vertical',
            align: 'right',
            verticalAlign: 'middle',
            borderWidth: 0
        },
        series: [{}]
    })

    $('#disk_space tbody').on('click', 'button#edit', function () {
        var media_id = $(this).find('input').val();
        var utils_id = $("#utils_manage").val();
        $.ajax({
            type: "POST",
            url: "../get_disk_space_daily/",
            data: {
                media_id: media_id,
                utils_id: utils_id
            },
            success: function (data) {
                while (weeklyChart.series.length > 0) {
                    weeklyChart.series[0].remove(true);
                }
                for (var i = 0; i < data.data.length; i++) {
                    weeklyChart.addSeries({
                        "name": data.data[i].name,
                        "data": data.data[i].capacity_list,
                        "color": data.data[i].color,
                    });
                }
                // 动态生成横坐标
                // 从1开始
                var category_list = [];
                for (var j = 1; j <= 20; j++) {
                    category_list.push(j)
                }
                weeklyChart.xAxis[0].setCategories(category_list);
            }
        });
    });
});