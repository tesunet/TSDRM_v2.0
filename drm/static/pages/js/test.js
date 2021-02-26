$(document).ready(function () {
    $('#save').click(function () {
        document.getElementById("mySavedModel").value = myDiagram.model.toJson();
	    myDiagram.isModified = false;
    });

    $('#start1').click(function () {
        $.ajax({
            type: "POST",
            url: "../tsdrmstart1/",
        });
    });
    $('#start2').click(function () {
        $.ajax({
            type: "POST",
            url: "../tsdrmstart2/",
        });
    });
    $('#stop').click(function () {
        $.ajax({
            type: "POST",
            url: "../tsdrmstop/",
        });
    });
    $('#pause').click(function () {
        $.ajax({
            type: "POST",
            url: "../tsdrmpause/",
        });
    });
    $('#retry1').click(function () {
        $.ajax({
            type: "POST",
            url: "../tsdrmretry1/",
        });
    });
    $('#retry2').click(function () {
        $.ajax({
            type: "POST",
            url: "../tsdrmretry2/",
        });
    });
});