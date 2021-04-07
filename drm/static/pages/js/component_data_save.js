// $(document).ready(function () {
//     //返回db的输入参数信息到页面
//     $("#tabcheck1_2").click(function () {
//         $("#component_input").empty()
//         var guid = {guid: $("#guid").val()}
//         $.ajax({
//             url: "../component_return_input/",
//             data: JSON.stringify(guid),
//             type: "POST",
//             data_type: "JSON",
//             contentType: "application/json",
//             headers: {"X-CSRFToken": $('[name="csrfmiddlewaretoken"]').val()},
//             success: function (data) {
//                 if (data.status == 0) {
//                     $("#component_input").append('<option value="">' + data.input + '</option>')
//                 } else if (data.status == 1) {
//                     $("#component_input").empty();
//                     for (var i = 0; i < data.input.length; i++) {
//                         $("#component_input").append('<option value="' + data.input[i]["code"] + '">' + data.input[i]["name"] + '</option>')
//                     }
//                     $("#component_input").click(function () {
//                         var selectval = $("#component_input option:selected").val();
//                         for (var i = 0; i < data.input.length; i++) {
//                             if (data.input[i]["code"] == selectval) {
//                                 $("#component_input_code").prop("readonly", true);
//                                 $("#component_input_name").prop("readonly", false);
//                                 $("#component_input_type").prop("disabled", false);
//                                 $("#component_input_source").prop("disabled", false);
//                                 $("#component_input_sort").prop("readonly", false);
//                                 $("#component_input_remark").prop("readonly", false);
//                                 $("#component_input_value").prop("readonly", false);
//
//                                 $('#component_input_code').val(data.input[i]["code"]);
//                                 $('#component_input_name').val(data.input[i]["name"]);
//                                 $('#component_input_type').val(data.input[i]["type"]);
//                                 $('#component_input_source').val(data.input[i]["source"]);
//                                 $('#component_input_sort').val(data.input[i]["sort"]);
//                                 $('#component_input_remark').val(data.input[i]["remark"]);
//                                 $('#component_input_value').val(data.input[i]["value"]);
//                                 break;
//                             }
//                         }
//                     })
//                 }
//
//             },
//             error: function () {
//
//             }
//         })
//     })
//     //返回db的临时变量信息到页面
//     $("#tabcheck1_3").click(function () {
//         $("#component_variable").empty()
//         var guid = {guid: $("#guid").val()}
//         $.ajax({
//             url: "../component_return_variable/",
//             data: JSON.stringify(guid),
//             type: "POST",
//             data_type: "JSON",
//             contentType: "application/json",
//             headers: {"X-CSRFToken": $('[name="csrfmiddlewaretoken"]').val()},
//             success: function (data) {
//                 if (data.status == 0) {
//                     $("#component_variable").append('<option value="">' + data.variable + '</option>')
//                 } else if (data.status == 1) {
//                     $("#component_variable").empty();
//                     for (var i = 0; i < data.variable.length; i++) {
//                         $("#component_variable").append('<option value="' + data.variable[i]["code"] + '">' + data.variable[i]["name"] + '</option>')
//                     }
//                     $("#component_variable").click(function () {
//                         var selectval = $("#component_variable option:selected").val();
//                         for (var i = 0; i < data.variable.length; i++) {
//                             if (data.variable[i]["code"] == selectval) {
//                                 $("#component_variable_code").prop("readonly", true);
//                                 $("#component_variable_name").prop("readonly", false);
//                                 $("#component_variable_type").prop("disabled", false);
//                                 $("#component_variable_source").prop("disabled", false);
//                                 $("#component_variable_sort").prop("readonly", false);
//                                 $("#component_variable_remark").prop("readonly", false);
//                                 $("#component_variable_value").prop("readonly", false);
//
//                                 $('#component_variable_code').val(data.variable[i]["code"]);
//                                 $('#component_variable_name').val(data.variable[i]["name"]);
//                                 $('#component_variable_type').val(data.variable[i]["type"]);
//                                 $('#component_variable_source').val(data.variable[i]["source"]);
//                                 $('#component_variable_sort').val(data.variable[i]["sort"]);
//                                 $('#component_variable_remark').val(data.variable[i]["remark"]);
//                                 $('#component_variable_value').val(data.variable[i]["value"]);
//                                 break;
//                             }
//                         }
//                     })
//                 }
//
//             },
//             error: function () {
//
//             }
//         })
//     })
//     //返回db的输出参数信息到页面
//     $("#tabcheck1_4").click(function () {
//         $("#component_output").empty()
//         var guid = {guid: $("#guid").val()}
//         $.ajax({
//             url: "../component_return_output/",
//             data: JSON.stringify(guid),
//             type: "POST",
//             data_type: "JSON",
//             contentType: "application/json",
//             headers: {"X-CSRFToken": $('[name="csrfmiddlewaretoken"]').val()},
//             success: function (data) {
//                 if (data.status == 0) {
//                     $("#component_output").append('<option value="">' + data.output + '</option>')
//                 } else if (data.status == 1) {
//                     $("#component_output").empty();
//                     for (var i = 0; i < data.output.length; i++) {
//                         $("#component_output").append('<option value="' + data.output[i]["code"] + '">' + data.output[i]["name"] + '</option>')
//                     }
//                     $("#component_output").click(function () {
//                         var selectval = $("#component_output option:selected").val();
//                         for (var i = 0; i < data.output.length; i++) {
//                             if (data.output[i]["code"] == selectval) {
//                                 $("#component_output_code").prop("readonly", true);
//                                 $("#component_output_name").prop("readonly", false);
//                                 $("#component_output_type").prop("disabled", false);
//                                 $("#component_output_source").prop("disabled", false);
//                                 $("#component_output_sort").prop("readonly", false);
//                                 $("#component_output_remark").prop("readonly", false);
//                                 $("#component_output_value").prop("readonly", false);
//
//                                 $('#component_output_code').val(data.output[i]["code"]);
//                                 $('#component_output_name').val(data.output[i]["name"]);
//                                 $('#component_output_type').val(data.output[i]["type"]);
//                                 $('#component_output_source').val(data.output[i]["source"]);
//                                 $('#component_output_sort').val(data.output[i]["sort"]);
//                                 $('#component_output_remark').val(data.output[i]["remark"]);
//                                 $('#component_output_value').val(data.output[i]["value"]);
//                                 break;
//                             }
//                         }
//                     })
//                 }
//
//             },
//             error: function () {
//
//             }
//         })
//     })
// })
//
// //点新增后在点保存
// $(document).ready(function () {
//     $('#component_input_save').click(function () {
//         //页面获取组件输入参数
//         if ($('#component_input_code').val() == "") {
//             alert("参数编码不能为空。")
//             return
//         }
//         if ($('#component_input_name').val() == "") {
//             alert("参数名称不能为空。")
//             return
//         }
//         if ($('#component_input_type').val() == "") {
//             alert("数据类型不能为空。")
//             return
//         }
//         if ($('#component_input_source').val() == "") {
//             alert("数据来源不能为空。")
//             return
//         }
//         if ($("#component_input_isnew").val() == "1") {
//             $("#component_input").empty();
//             var inputparams = {
//                 guid: $("#guid").val(),
//                 isnew: $("#component_input_isnew").val(),
//                 code: $("#component_input_code").val(),
//                 name: $("#component_input_name").val(),
//                 type: $("#component_input_type").val(),
//                 value: $("#component_input_value").val(),
//                 source: $("#component_input_source").val(),
//                 remark: $("#component_input_remark").val(),
//                 sort: $("#component_input_sort").val(),
//             }
//             $.ajax({
//                 url: "../component_form_input/",
//                 data: JSON.stringify(inputparams),
//                 type: "POST",
//                 data_type: "JSON",
//                 contentType: "application/json",
//                 headers: {"X-CSRFToken": $('[name="csrfmiddlewaretoken"]').val()},
//                 success: function (data) {
//                     console.log(inputparams)
//                     if (data.status == 1) {
//                         alert(data.input)
//                         // location.reload()
//                         $("#tab_1_2").load(location.href+" tab_1_2")
//                     } else if (data.status == 3) {
//                         alert(data.input)
//                         // location.reload()
//                     } else {
//                         alert(data.input)
//                         // location.reload()
//                     }
//                 },
//                 error: function (data) {
//                     alert("请求错误")
//                     location.reload()
//                 }
//             })
//         } else if ($("#component_input_isnew").val() == "0") {
//             var inputparams = {
//                 guid: $("#guid").val(),
//                 isnew: $("#component_input_isnew").val(),
//                 code: $("#component_input_code").val(),
//                 name: $("#component_input_name").val(),
//                 type: $("#component_input_type").val(),
//                 value: $("#component_input_value").val(),
//                 source: $("#component_input_source").val(),
//                 remark: $("#component_input_remark").val(),
//                 sort: $("#component_input_sort").val(),
//             }
//             $.ajax({
//                 url: "../component_form_input/",
//                 data: JSON.stringify(inputparams),
//                 type: "POST",
//                 data_type: "JSON",
//                 contentType: "application/json",
//                 headers: {"X-CSRFToken": $('[name="csrfmiddlewaretoken"]').val()},
//                 success: function (data) {
//                     if (data.status == 2) {
//                         alert(data.input)
//                         location.reload()
//                     } else {
//                         alert(data.input)
//                         // location.reload()
//                     }
//
//                 },
//                 error: function (data) {
//                     alert("请求失败")
//                 }
//             })
//
//         }
//
//     })
// })
//
// //点新增后在点保存
// $(document).ready(function () {
//     $('#component_variable_save').click(function () {
//         //页面获取组件输入参数
//         if ($('#component_variable_code').val() == "") {
//             alert("参数编码不能为空。")
//             return
//         }
//         if ($('#component_variable_name').val() == "") {
//             alert("参数名称不能为空。")
//             return
//         }
//         if ($('#component_variable_type').val() == "") {
//             alert("数据类型不能为空。")
//             return
//         }
//         if ($('#component_variable_source').val() == "") {
//             alert("数据来源不能为空。")
//             return
//         }
//         if ($("#component_variable_isnew").val() == "1") {
//             $("#component_variable").empty();
//             var variableparams = {
//                 guid: $("#guid").val(),
//                 isnew: $("#component_variable_isnew").val(),
//                 code: $("#component_variable_code").val(),
//                 name: $("#component_variable_name").val(),
//                 type: $("#component_variable_type").val(),
//                 value: $("#component_variable_value").val(),
//                 remark: $("#component_variable_remark").val(),
//                 sort: $("#component_variable_sort").val(),
//             }
//             $.ajax({
//                 url: "../component_form_variable/",
//                 data: JSON.stringify(variableparams),
//                 type: "POST",
//                 data_type: "JSON",
//                 contentType: "application/json",
//                 headers: {"X-CSRFToken": $('[name="csrfmiddlewaretoken"]').val()},
//                 success: function (data) {
//                     console.log(variableparams)
//                     if (data.status == 1) {
//                         alert(data.variable)
//                     } else if (data.status == 3) {
//                         alert(data.variable)
//                     } else {
//                         alert(data.variable)
//                     }
//                 },
//                 error: function (data) {
//                     alert("请求错误")
//                 }
//             })
//         } else if ($("#component_variable_isnew").val() == "0") {
//             var variableparams = {
//                 guid: $("#guid").val(),
//                 isnew: $("#component_variable_isnew").val(),
//                 code: $("#component_variable_code").val(),
//                 name: $("#component_variable_name").val(),
//                 type: $("#component_variable_type").val(),
//                 value: $("#component_variable_value").val(),
//                 remark: $("#component_variable_remark").val(),
//                 sort: $("#component_variable_sort").val(),
//             }
//             $.ajax({
//                 url: "../component_form_variable/",
//                 data: JSON.stringify(variableparams),
//                 type: "POST",
//                 data_type: "JSON",
//                 contentType: "application/json",
//                 headers: {"X-CSRFToken": $('[name="csrfmiddlewaretoken"]').val()},
//                 success: function (data) {
//                     if (data.status == 2) {
//                         alert(data.variable)
//                     } else {
//                         alert(data.variable)
//                     }
//
//                 },
//                 error: function (data) {
//                     alert("请求失败")
//                 }
//             })
//
//         }
//
//     })
// })
//
//
// //点新增后在点保存
// $(document).ready(function () {
//     $('#component_output_save').click(function () {
//         //页面获取组件输入参数
//         if ($('#component_output_code').val() == "") {
//             alert("参数编码不能为空。")
//             return
//         }
//         if ($('#component_output_name').val() == "") {
//             alert("参数名称不能为空。")
//             return
//         }
//         if ($('#component_output_type').val() == "") {
//             alert("数据类型不能为空。")
//             return
//         }
//         if ($('#component_output_source').val() == "") {
//             alert("数据来源不能为空。")
//             return
//         }
//         if ($("#component_output_isnew").val() == "1") {
//             $("#component_output").empty();
//             var outputparams = {
//                 guid: $("#guid").val(),
//                 isnew: $("#component_output_isnew").val(),
//                 code: $("#component_output_code").val(),
//                 name: $("#component_output_name").val(),
//                 type: $("#component_output_type").val(),
//                 value: $("#component_output_value").val(),
//                 source: $("#component_output_source").val(),
//                 remark: $("#component_output_remark").val(),
//                 sort: $("#component_output_sort").val(),
//             }
//             $.ajax({
//                 url: "../component_form_output/",
//                 data: JSON.stringify(outputparams),
//                 type: "POST",
//                 data_type: "JSON",
//                 contentType: "application/json",
//                 headers: {"X-CSRFToken": $('[name="csrfmiddlewaretoken"]').val()},
//                 success: function (data) {
//                     console.log(outputparams)
//                     if (data.status == 1) {
//                         alert(data.output)
//                     } else if (data.status == 3) {
//                         alert(data.output)
//                     } else {
//                         alert(data.output)
//                     }
//                 },
//                 error: function (data) {
//                     alert("请求错误")
//                 }
//             })
//         } else if ($("#component_output_isnew").val() == "0") {
//             var outputparams = {
//                 guid: $("#guid").val(),
//                 isnew: $("#component_output_isnew").val(),
//                 code: $("#component_output_code").val(),
//                 name: $("#component_output_name").val(),
//                 type: $("#component_output_type").val(),
//                 value: $("#component_output_value").val(),
//                 source: $("#component_output_source").val(),
//                 remark: $("#component_output_remark").val(),
//                 sort: $("#component_output_sort").val(),
//             }
//             $.ajax({
//                 url: "../component_form_output/",
//                 data: JSON.stringify(outputparams),
//                 type: "POST",
//                 data_type: "JSON",
//                 contentType: "application/json",
//                 headers: {"X-CSRFToken": $('[name="csrfmiddlewaretoken"]').val()},
//                 success: function (data) {
//                     if (data.status == 2) {
//                         alert(data.output)
//                     } else {
//                         alert(data.output)
//                     }
//
//                 },
//                 error: function (data) {
//                     alert("请求失败")
//                 }
//             })
//
//         }
//
//     })
// })
//
// $(document).ready(function () {
//     $("#component_input_add").click(function () {
//             $("#component_input").empty()
//             $("#component_input_isnew").val("1")
//             $("#component_input").unbind("click")
//             $("#component_input_code").val('');
//             $("#component_input_name").val('');
//             $("#component_input_type").val('');
//             $("#component_input_source").val('');
//             $("#component_input_value").val('');
//             $("#component_input_sort").val('');
//             $("#component_input_remark").val('');
//
//             $("#component_input_code").prop("readonly", false);
//             $("#component_input_name").prop("readonly", false);
//             $("#component_input_type").prop("disabled", false);
//             $("#component_input_source").prop("disabled", false);
//             $("#component_input_value").prop("readonly", false);
//             $("#component_input_sort").prop("readonly", false);
//             $("#component_input_remark").prop("readonly", false);
//         }
//     )
// })
//
// $(document).ready(function () {
//     $("#component_variable_add").click(function () {
//             $("#component_variable").empty()
//             $("#component_variable_isnew").val("1")
//             $("#component_variable").unbind("click")
//             $("#component_variable_code").val('');
//             $("#component_variable_name").val('');
//             $("#component_variable_type").val('');
//             $("#component_variable_source").val('');
//             $("#component_variable_value").val('');
//             $("#component_variable_sort").val('');
//             $("#component_variable_remark").val('');
//
//             $("#component_variable_code").prop("readonly", false);
//             $("#component_variable_name").prop("readonly", false);
//             $("#component_variable_type").prop("disabled", false);
//             $("#component_variable_source").prop("disabled", false);
//             $("#component_variable_value").prop("readonly", false);
//             $("#component_variable_sort").prop("readonly", false);
//             $("#component_variable_remark").prop("readonly", false);
//         }
//     )
// })
//
// $(document).ready(function () {
//     $("#component_output_add").click(function () {
//             $("#component_output").empty()
//             $("#component_output_isnew").val("1")
//             $("#component_output").unbind("click")
//             $("#component_output_code").val('');
//             $("#component_output_name").val('');
//             $("#component_output_type").val('');
//             $("#component_output_source").val('');
//             $("#component_output_value").val('');
//             $("#component_output_sort").val('');
//             $("#component_output_remark").val('');
//
//             $("#component_output_code").prop("readonly", false);
//             $("#component_output_name").prop("readonly", false);
//             $("#component_output_type").prop("disabled", false);
//             $("#component_output_source").prop("disabled", false);
//             $("#component_output_value").prop("readonly", false);
//             $("#component_output_sort").prop("readonly", false);
//             $("#component_output_remark").prop("readonly", false);
//         }
//     )
// })
