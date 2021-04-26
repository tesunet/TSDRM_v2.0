$(document).ready(function () {
    $('#testnetwork').click(function () {
        $.ajax({
            type: "POST",
            dataType: "json",
            url: "../check_master_network/",
            data: {
                user: $("#user").val(),
                mip: $("#mip").val(),
                password: $("#password").val(),

            },
            success: function (data) {
                if (data.code == 0) {
                    alert(data.info)
                } else {
                    alert(data.info);
                }
            }
        })
    })
    $('#testdbstate').click(function () {
        $.ajax({
            type: "POST",
            dataType: "json",
            url: "../check_master_dbstate/",
            data: {
                user: $("#user").val(),
                mip: $("#mip").val(),
                password: $("#password").val(),
                dbuser:$("#dbuser").val(),
                dbpassword:$("#dbpassword").val(),

            },
            success: function (data) {
                if (data.code == 0) {
                    alert(data.info)
                } else {
                    alert(data.info);
                }
            }
        })
    })
})