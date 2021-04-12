$('#se_1').contextmenu({
    target: '#context-menu2',
    onItem: function (context, e) {
        if ($(e.target).text() == "新增") {
            $("#dict_id_display_div").hide();

            $("#dictname").val("");
            $("#dictsort").val("");
            $("#dictremark").val("");
            $("#dictid").val("0");
            document.getElementById("edit").click();
        }
        if ($(e.target).text() == "修改") {
            if ($("#se_1").find('option:selected').length == 0)
                alert("请选择要修改的字典。");
            else {
                if ($("#se_1").find('option:selected').length > 1)
                    alert("修改时请不要选择多条记录。");
                else {
                    $("#dict_id_display_div").show();
                    $("#dict_id_display").val($("#se_1").find('option:selected').attr('id'));

                    $("#dictname").val($("#se_1").find('option:selected').text());
                    $("#dictsort").val($("#se_1").find('option:selected').attr('sort'));
                    $("#dictid").val($("#se_1").find('option:selected').attr('id'));
                    $("#dictremark").val($("#se_1").find('option:selected').attr('remark'));

                    document.getElementById("edit").click();
                }
            }
        }

        if ($(e.target).text() == "删除") {
            if ($("#se_1").find('option:selected').length == 0)
                alert("请选择要删除的字典。");
            else {
                if (confirm("错误删除字典可能引起系统瘫痪，确定要删除该字典吗？")) {
                    $.ajax({
                        type: "POST",
                        url: "../dictdel/",
                        data:
                            {
                                dictid: $("#se_1").find('option:selected').attr("id"),
                            },
                        success: function (data) {
                            if (data == "删除成功。") {
                                $("#se_1").find('option:selected').remove();
                                $("#se_2").empty();
                            }
                            alert(data);
                        },
                        error: function (e) {
                            alert("页面出现错误，请于管理员联系。");
                        }
                    });
                }
            }
        }

    }
});
$('#se_2').contextmenu({
    target: '#context-menu3',
    onItem: function (context, e) {
        if ($(e.target).text() == "新增") {

            if ($("#se_1").find('option:selected').length == 0)
                alert("请选择字典。");
            else {
                $("#list_id_display_div").hide();

                $("#listname").val("");
                $("#listsort").val("");
                $("#listremark").val("");
                $("#listcontent").val("");
                $("#listid").val("0");
                document.getElementById("edit2").click();
            }
        }
        if ($(e.target).text() == "修改") {
            if ($("#se_2").find('option:selected').length == 0)
                alert("请选择要修改的条目。");
            else {
                if ($("#se_2").find('option:selected').length > 1)
                    alert("修改时请不要选择多条记录。");
                else {
                    $("#list_id_display_div").show();
                    $("#list_id_display").val($("#se_2").find('option:selected').attr('id'));

                    $("#listname").val($("#se_2").find('option:selected').text());
                    $("#listsort").val($("#se_2").find('option:selected').attr('sort'));
                    $("#listid").val($("#se_2").find('option:selected').attr('id'));
                    $("#listremark").val($("#se_2").find('option:selected').attr('remark'));
                    $("#listcontent").val($("#se_2").find('option:selected').attr('content'));

                    document.getElementById("edit").click();
                }
            }
        }

        if ($(e.target).text() == "删除") {
            if ($("#se_2").find('option:selected').length == 0)
                alert("请选择要删除的条目。");
            else {
                if (confirm("错误删除条目可能引起系统瘫痪，确定要删除该字典吗？")) {
                    $.ajax({
                        type: "POST",
                        url: "../dictlistdel/",
                        data:
                            {
                                listid: $("#se_2").find('option:selected').attr("id"),
                            },
                        success: function (data) {
                            if (data == "删除成功。") {
                                $("#se_2").find('option:selected').remove();
                            }
                            alert(data);
                        },
                        error: function (e) {
                            alert("页面出现错误，请于管理员联系。");
                        }
                    });
                }
            }
        }

    }
});
$('#se_1').change(function () {
    $.ajax({
        type: "GET",
        dataType: 'json',
        url: "../dictselect/",
        data:
            {
                dictid: $("#se_1").find('option:selected').attr('id'),
            },
        success: function (data) {
            $("#se_2").empty();
            for (var i = 0; i < data.length; i++) {
                $("#se_2").append("<option id='" + "list_" + data[i].id + "' sort='" + data[i].sort + "' remark='" + data[i].remark + "' content='" + data[i].content + "'>" + data[i].name + "</option>");
            }
        },
        error: function (e) {
            alert("系统出错")

        }
    });
});

$('#save').click(function () {
    $.ajax({
        type: "POST",
        dataType: 'json',
        url: "../dictsave/",
        data:
            {
                dictid: $("#dictid").val(),
                dictname: $("#dictname").val(),
                dictsort: $("#dictsort").val(),
                dictremark: $("#dictremark").val(),
            },
        success: function (data) {
            var myres = data["res"];
            var mydata = data["data"];
            if (myres == "新增成功。") {
                $("#se_1").append("<option id='" + "dict_" + mydata + "' sort='" + $("#dictsort").val() + "' remark='" + $("#dictremark").val() + "'>" + $("#dictname").val() + "</option>");
                $('#static').modal('hide');
            }
            if (myres == "修改成功。") {
                $("#" + $("#dictid").val()).text($("#dictname").val());
                $("#" + $("#dictid").val()).attr('sort', $("#dictsort").val());
                $("#" + $("#dictid").val()).attr('remark', $("#dictremark").val());

                $('#static').modal('hide');
            }
            alert(myres);
        },
        error: function (e) {
            alert("页面出现错误，请于管理员联系。");
        }
    });
});

$('#listsave').click(function () {

    $.ajax({
        type: "POST",
        dataType: 'json',
        url: "../dictlistsave/",
        data:
            {
                dictid: $("#se_1").find('option:selected').attr('id'),
                listid: $("#listid").val(),
                listname: $("#listname").val(),
                listsort: $("#listsort").val(),
                listremark: $("#listremark").val(),
                listcontent: $("#listcontent").val(),
            },
        success: function (data) {
            var myres = data["res"];
            var mydata = data["data"];
            if (myres == "新增成功。") {
                $("#se_2").append("<option id='" + "list_" + mydata + "' sort='" + $("#listsort").val() + "' remark='" + $("#listremark").val() + "' content='" + $("#listcontent").val() + "'>" + $("#listname").val() + "</option>");
                $('#static1').modal('hide');
            }
            if (myres == "修改成功。") {
                $("#" + $("#listid").val()).text($("#listname").val());
                $("#" + $("#listid").val()).attr('sort', $("#listsort").val());
                $("#" + $("#listid").val()).attr('remark', $("#listremark").val());
                $("#" + $("#listid").val()).attr('content', $("#listcontent").val());
                $('#static1').modal('hide');
            }
            alert(myres);
        },
        error: function (e) {
            alert("页面出现错误，请于管理员联系。");
        }
    });

});



