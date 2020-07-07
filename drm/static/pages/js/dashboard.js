function getframeworkstate(){
    $("#url_util").click(function () {
        window.open("/framework?util="+$("#util").val());
    });
    $.ajax({
        type: 'POST',
        dataType: 'json',
        url: '../get_frameworkstate/',
        data: {
            "util":$('#util').val(),
        },
        success: function (data) {
                if (data.data == 0) {
                    $('#frameworkstate').text("正常")
                    $("#frameworkstate").css("color", "white");
                } else if (data.data == 1){
                    $('#frameworkstate').text("警告")
                    $("#frameworkstate").css("color", "yellow");

                }else if (data.data == 2){
                    $('#frameworkstate').text("错误")
                    $("#frameworkstate").css("color", "red");
            }
        }
    });
}

function getclientnum(){
    $("#url_allclient").click(function () {
        window.open("/client_list?util="+$("#util").val());
    });
    $("#url_wnclient").click(function () {
        window.open("/client_list?util="+$("#util").val());
    });
    $.ajax({
        type: 'POST',
        dataType: 'json',
        url: '../get_backup_status/',
        data: {

            'utils_manage_id': $("#util").val(),
        },
        success: function (data) {
            if (data.ret == 0) {
                alert(data.data)
            } else {
                // 报警客户端
                var all_client_num = 0;
                var warning_client_num = 0;
                var allclientlist = []
                var warningclientlist = []
                var whole_list = data.data;

                // 加载数据
                var content_el = ''
                for (var i = 0; i < whole_list.length; i++) {
                    if( allclientlist.indexOf(whole_list[i]["clientname"]) == -1){
                        allclientlist.push(whole_list[i]["clientname"]);
                    }
                    if(whole_list[i]["bk_status"].indexOf("失败") != -1 && warningclientlist.indexOf(whole_list[i]["clientname"]) == -1){
                        warningclientlist.push(whole_list[i]["clientname"]);
                    }
                }
                var all_client_num = allclientlist.length;
                var warning_client_num = warningclientlist.length;

                $("#all_client_num").text(all_client_num)
                $("#warning_client_num").text(warning_client_num)
                if (warning_client_num > 0) {
                    $("#warning_client_num").css("color", "red");
                }

                //$("tbody").append(content_el);
                $("#loading").hide();
            }
        }
    });
}

$(document).ready(function () {
    getframeworkstate();
    getclientnum();
    $("#util").change(function () {
        getframeworkstate();
        getclientnum();
    });



    var Dashboard = function () {

        return {

            initHighChart: function () {
                var chart;
                $(document).ready(function () {
                    chart = new Highcharts.Chart({
                        chart: {
                            renderTo: 'highchart_1',
                            style: {
                                fontFamily: 'Open Sans'
                            }
                        },
                        title: {
                            text: ' ',
                            x: -20 //center
                        },

                        xAxis: {
                            categories: ['1', '2', '3', '4', '5', '6',
                                '7', '8', '9', '10', '11', '12']
                        },
                        colors: [
                            '#3598dc',
                            '#e7505a',
                            '#32c5d2',
                            '#8e44ad',
                        ],
                        yAxis: {
                            title: {
                                text: 'RTO (分钟)'
                            },
                            plotLines: [{
                                value: 0,
                                width: 1,
                                color: '#808080'
                            }]
                        },
                        tooltip: {
                            valueSuffix: '分钟'
                        },
                        legend: {
                            layout: 'vertical',
                            align: 'right',
                            verticalAlign: 'middle',
                            borderWidth: 0
                        },
                        series: [{}]
                    })
                });
                $.ajax({
                    type: "GET",
                    url: "../get_process_rto/",
                    success: function (data) {
                        while (chart.series.length > 0) {
                            chart.series[0].remove(true);
                        }
                        for (var i = 0; i < data.data.length; i++) {
                            chart.addSeries({
                                "name": data.data[i].process_name,
                                "data": data.data[i].current_rto_list,
                                "color": data.data[i].color,
                            });
                        }
                    }

                });
            },

            initCalendar: function () {
                if (!jQuery().fullCalendar) {
                    return;
                }

                var date = new Date();
                var d = date.getDate();
                var m = date.getMonth();
                var y = date.getFullYear();

                var h = {};


                $('#calendar').removeClass("mobile");
                if (App.isRTL()) {
                    h = {
                        right: 'title',
                        center: '',
                        left: 'prev,next,today,month,agendaWeek,agendaDay'
                    };
                } else {
                    h = {
                        left: 'title',
                        center: '',
                        right: 'prev,next,today,month,agendaWeek,agendaDay'
                    };
                }


                $('#calendar').fullCalendar('destroy'); // destroy the calendar
                $('#calendar').fullCalendar({ //re-initialize the calendar
                    disableDragging: false,
                    header: h,
                    editable: true,
                    monthNames: ['一月', '二月', '三月', '四月', '五月', '六月', '七月',
                        '八月', '九月', '十月', '十一月', '十二月'],
                    dayNames: ['星期天', '星期一', '星期二', '星期三', '星期四',
                        '星期五', '星期六'],
                    dayNamesShort: ['星期天', '星期一', '星期二', '星期三', '星期四',
                        '星期五', '星期六'],
                    buttonText: {
                        today: '回到当日',
                        month: '月',
                        week: '周',
                        day: '日',
                        list: 'list'
                    },
                    events: function (start, end, timezone, callback) {
                        $.ajax({
                            url: '../get_daily_processrun/',
                            type: 'post',
                            data: {},
                            dataType: 'json',
                            success: function (data) {
                                var events = [];
                                for (var i = 0; i < data.data.length; i++) {
                                    var title = data.data[i].process_name;
                                    var id = data.data[i].process_run_id;
                                    var start = data.data[i].start_time;
                                    var end = data.data[i].end_time;
                                    var backgroundColor = data.data[i].process_color;
                                    var url = data.data[i].url;
                                    var invite = data.data[i].invite;
                                    if (invite == "1") {
                                        events.push({
                                            id: id,
                                            title: title,
                                            start: start,
                                            end: end,
                                            backgroundColor: backgroundColor,
                                            url: url,
                                            className: "invite"
                                        });
                                    } else {
                                        events.push({
                                            id: id,
                                            title: title,
                                            start: start,
                                            end: end,
                                            backgroundColor: backgroundColor,
                                            url: url,
                                        });
                                    }
                                }

                                try {
                                    callback(events);
                                } catch (e) {
                                    console.info(e);
                                }
                            }
                        });
                    },
                    eventAfterAllRender: function (view) {
                        $(".fc-day-grid-event.fc-h-event.fc-event.fc-start.fc-end.invite.fc-draggable").each(function () {
                            var processName = $(this).find('.fc-title').text();
                            $(this).find('.fc-title').html("<font color='red'>*</font> " + processName);
                        });
                        $(".fc-day-grid-event.fc-h-event.fc-event.fc-start.fc-end.fc-draggable").each(function () {
                            $(this).prop("target", "_blank");
                        })
                    }
                });
            },
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
                this.initCalendar();
                //this.initHighChart();
                this.componentsKnobDials();
            }
        };

    }();

    if (App.isAngularJsApp() === false) {
        jQuery(document).ready(function () {
            Dashboard.init(); // init metronic core componets
        });
    }

    $("ul#locate_task").on("click", " li", function () {
        var task_id = $(this).attr("id");
        $("#mytask").val($("#a".replace("a", task_id)).find("input#task_id").val());
        $("#processname").val($("#a".replace("a", task_id)).find("input#process_name").val());
        $("#sendtime").val($("#a".replace("a", task_id)).find("input#send_time").val());
        $("#signrole").val($("#a".replace("a", task_id)).find("input#sign_role").val());
        $("#processrunreason").val($("#a".replace("a", task_id)).find("input#process_run_reason").val());
    });

});








