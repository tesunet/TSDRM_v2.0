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
                        text: '最近恢复RTO',
                        x: -20 //center
                    },

                    xAxis: {
                        title: {
                            text: '次数 (次)'
                        },
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
                        }],
                        tickInterval: 5,
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
                    series: [{}],
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
                timeFormat: 'H:mm',
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
            this.initHighChart();
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

// 演练概况
$.ajax({
    type: 'POST',
    dataType: 'json',
    url: '../get_process_run_facts/',
    data: {
        "csrfmiddlewaretoken": $("[name='csrfmiddlewaretoken']").val(),
    },
    success: function (data) {
        var whole_list = data.data;
        $("tbody#process_run_facts").empty();
        // 加载数据
        for (var i = 0; i < whole_list.length; i++) {
            var labelStatus = "";
            if (whole_list[i].process_run_today == 0) {
                labelStatus = '<span title="演练成功"><i class="fa fa-check" style="color:#26C281;"></i></span>';
            } else if (whole_list[i].process_run_today == 1) {
                labelStatus = '<span title="演练失败"><i class="fa fa-times" style="color:#c51b26;"></i></span>';
            } else {
                labelStatus = '<span title="未演练"><i class="fa fa-circle-o" style="color:#F1C40F;"></i></span>';
            }

            $("tbody#process_run_facts").append('<tr>\n' +
                '    <td style="vertical-align:middle">' + (i + 1) + '</td>\n' +
                '    <td style="vertical-align:middle"><a href="/oracle_restore/' + whole_list[i].process_id + '">' + whole_list[i].process_name + '</a></td>\n' +
                '    <td style="vertical-align:middle">\n' + labelStatus +
                '    </td>\n' +
                '    <td style="vertical-align:middle">' + whole_list[i].average_rto + '</td>\n' +
                '    <td style="vertical-align:middle">' + whole_list[i].cur_client_process_times + '</td>\n' +
                '    <td style="vertical-align:middle">' + whole_list[i].process_run_rate + ' %</td>\n' +
                '</tr>');
        }
    }
});

