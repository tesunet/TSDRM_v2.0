$(document).ready(function () {
    function get_kvm_template() {
        $.ajax({
            type: "POST",
            dataType: 'json',
            url: "../get_kvm_template/",
            data: {
                utils_id: $('#util').val()
            },
            success: function (data) {
                if (data.ret == 1) {
                    $("#template_data").val(JSON.stringify(data.data));
                    var os_image = data.data.os_image;
                    var disk_image = data.data.disk_image;
                    var base_image = data.data.base_image;
                    var windb_image = data.data.windb_image;
                    var linuxdb_image = data.data.linuxdb_image;

                    $('#select_kvm_template').empty();

                    var all_image_pre = '<optgroup label="' + '/home/images/disk-image' + '" class="dropdown-header">';
                    for (i = 0; i < disk_image.length; i++) {
                        all_image_pre += '<option value="' + disk_image[i] + '">' + disk_image[i] + '</option>'
                    }
                    all_image_pre += '</optgroup>';

                    all_image_pre += '<optgroup label="' + '/home/images/os-image' + '" class="dropdown-header">';
                    for (i = 0; i < os_image.length; i++) {
                        all_image_pre += '<option value="' + os_image[i] + '">' + os_image[i] + '</option>'
                    }
                    all_image_pre += '</optgroup>';


                    all_image_pre += '<optgroup label="' + '/home/images/windb-image' + '" class="dropdown-header">';
                    for (i = 0; i < windb_image.length; i++) {
                        all_image_pre += '<option value="' + windb_image[i] + '">' + windb_image[i] + '</option>'
                    }
                    all_image_pre += '</optgroup>';


                    all_image_pre += '<optgroup label="' + '/home/images/linuxdb-image' + '" class="dropdown-header">';
                    for (i = 0; i < linuxdb_image.length; i++) {
                        all_image_pre += '<option value="' + linuxdb_image[i] + '">' + linuxdb_image[i] + '</option>'
                    }
                    all_image_pre += '</optgroup>';

                    all_image_pre += '<optgroup label="' + '/home/images/base-image' + '" class="dropdown-header">';
                    for (i = 0; i < base_image.length; i++) {
                        all_image_pre += '<option value="' + base_image[i] + '">' + base_image[i] + '</option>'
                    }
                    all_image_pre += '</optgroup>';

                    $('#remote_template_file').append(all_image_pre)

                } else {
                    alert(data.data);
                }
            },
            error: function (e) {
                alert("页面出现错误，请于管理员联系。");
            }
        });
    }
    get_kvm_template();

    $('#util').change(function(){
        get_kvm_template()
    });

    $('#kvm_template_dt').dataTable({
        "bAutoWidth": true,
        "bSort": false,
        "bProcessing": true,
        "ajax": "../kvm_template_data/",
        "columns": [
            {"data": "id"},
            {"data": "name"},
            {"data": "path"},
            {"data": "file_name"},
            {"data": "type"},
            {"data": "utils_name"},
            {"data": null}
        ],
        "columnDefs": [{
            "targets": -1,
            "data": null,
            "width": "100px",
            "defaultContent": "<button  id='edit' title='编辑' data-toggle='modal'  data-target='#static'  class='btn btn-xs btn-primary' type='button'><i class='fa fa-edit'></i></button>" +
                "<button title='删除'  id='delrow' class='btn btn-xs btn-primary' type='button'><i class='fa fa-trash-o'></i></button>"
        }],
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

        }
    });

    $('#kvm_template_dt tbody').on('click', 'button#delrow', function () {
        if (confirm("确定要删除该条数据？")) {
            var table = $('#kvm_template_dt').DataTable();
            var data = table.row($(this).parents('tr')).data();
            $.ajax({
                type: "POST",
                url: "../kvm_template_del/",
                data: {
                    id: data.id,
                    path: data.path,
                    utils_id: data.utils_id,
                },
                success: function (data) {
                    if (data.status == 1) {
                        table.ajax.reload();
                    }
                    alert(data.data);
                },
                error: function (e) {
                    alert("删除失败，请于管理员联系。");
                }
            });
        }
    });

    $('#kvm_template_dt tbody').on('click', 'button#edit', function () {
        $('#upload_template_div').show();
        $('#loading1').hide();

        $('input:radio[name=radio2]')[0].checked = false;
        $('input:radio[name=radio2]')[1].checked = true;
        $("#local_file_div").hide();
        $("#remote_file_div").show();

        var table = $('#kvm_template_dt').DataTable();
        var data = table.row($(this).parents('tr')).data();
        $("#id").val(data.id);
        $("#name").val(data.name);
        $("#type").val(data.type_val);
        $("#path").val(data.path);
        $("#utils_id").val(data.utils_id);
        $("#remote_template_file").val(data.file_name);
    });

    $("#upload").click(function () {
        $('#upload_template_div').show();
        $('#loading1').hide();
        $('input:radio[name=radio2]')[0].checked = true;
        $('input:radio[name=radio2]')[1].checked = false;
        $("#local_file_div").show();
        $("#remote_file_div").hide();
        $("span.fileinput-filename").empty();
        $("#file_status").attr("class", "fileinput fileinput-new");
        $("#id").val(0);
        $("#name").val("");
        $("#local_template_file").val("");
        $("#remote_template_file").val("");
        $("#type").val("");
        $("#path").val("");
    });

    $("#type").change(function () {
        if ($("#type").val() == 'os_image'){
            $("#path").val("/home/images/os-image");
        }
        if ($("#type").val() == 'disk_image'){
            $("#path").val("/home/images/disk-image");
        }
    });

    $("#save").click(function () {
        var remote_template_file = $("#remote_template_file").val();
        var local_template_file = $("#local_template_file")[0].files[0];
        if (local_template_file){
            $('#upload_template_div').hide();
            $('#loading1').show();
            var table = $('#kvm_template_dt').DataTable();
            var form = new FormData();
            form.append("template_file", $("#local_template_file")[0].files[0]);
            form.append("id", $("#id").val());
            form.append("name", $("#name").val());
            form.append("utils_id", $("#util").val());
            form.append("type", $("#type").val());
            form.append("path", $("#path").val());
            form.append("csrfmiddlewaretoken", $('input[name="csrfmiddlewaretoken"]').val());
            $.ajax({
                type: "POST",
                url: "../kvm_template_save/",
                data:form,
                processData: false,
                contentType: false,
                success: function (data) {
                    var myres = data["res"];
                    if (myres == "保存成功。") {
                        $("#id").val(data["data"]);
                        $('#loading1').hide();
                        $('#static').modal('hide');
                        table.ajax.reload();
                    }
                    alert(myres);
                    $('#upload_template_div').show();
                    $('#loading1').hide();
                },
                error: function (e) {
                    alert("页面出现错误，请于管理员联系。");
                    $('#upload_template_div').show();
                    $('#loading1').hide();
                }
            });
        }

        if (remote_template_file && local_template_file == undefined){
            $('#loading1').hide();
            var table = $('#kvm_template_dt').DataTable();
            $.ajax({
                type: "POST",
                dataType: 'json',
                url: "../kvm_template_save/",
                data:
                    {
                        id: $("#id").val(),
                        name: $("#name").val(),
                        remote_template_file: $("#remote_template_file").val(),
                        utils_id: $("#util").val(),
                        type: $("#type").val(),
                        path: $("#path").val(),
                    },
                success: function (data) {
                        var myres = data["res"];
                        if (myres == "保存成功。") {
                            $("#id").val(data["data"]);
                            $('#loading1').hide();
                            $('#static').modal('hide');
                            table.ajax.reload();
                        }
                        alert(myres);
                        $('#upload_template_div').show();
                        $('#loading1').hide();
                    },
                error: function (e) {
                    alert("页面出现错误，请于管理员联系。");
                    $('#upload_template_div').show();
                    $('#loading1').hide();
                }
            });
        }
    });

    if ($("#local_file:checked").val() == "1") {
        $("#local_file_div").show();
        $("#remote_file_div").hide();
    }else{
         $("#local_file_div").hide();
         $("#remote_file_div").show();
    }

    $('input:radio[name="radio2"]').click(function() {
        if ($("#local_file:checked").val() == "1") {
            $("#name").val("");
            $("#type").val("");
            $("#path").val("");
            $("#remote_template_file").val("");
            $("#local_file_div").show();
            $("#remote_file_div").hide();
            $('input:radio[name=radio2]')[0].checked = true;
        }
        if (($("#remote_file:checked").val() == "0")){
            $("#name").val("");
            $("#remote_template_file").val("");
            $("#local_template_file").val("");
            $("#local_file_div").hide();
            $("#remote_file_div").show();
            $('input:radio[name=radio2]')[1].checked = true;

        }
    });

    $('#remote_template_file').change(function(){
        var data = JSON.parse($("#template_data").val());
        var os_image = data.os_image;
        var disk_image = data.disk_image;
        var base_image = data.base_image;
        var windb_image = data.windb_image;
        var linuxdb_image = data.linuxdb_image;
        var value = $("#remote_template_file").val();
        if (os_image.indexOf(value) != -1){
            $("#type").val("os_image");
            $("#path").val("/home/images/os-image" + '/' + value);
        }else if (disk_image.indexOf(value) != -1){
            $("#type").val("disk_image");
            $("#path").val("/home/images/disk-image" + '/' + value);
        }else if (base_image.indexOf(value) != -1){
            $("#type").val("disk_image");
            $("#path").val("/home/images/base-image" + '/' + value);
        }else if (linuxdb_image.indexOf(value) != -1){
            $("#type").val("disk_image");
            $("#path").val("/home/images/windb-image" + '/' + value);
        }else if (windb_image.indexOf(value) != -1){
            $("#type").val("disk_image");
            $("#path").val("/home/images/linuxdb-image" + '/' + value);
        }
    });

});