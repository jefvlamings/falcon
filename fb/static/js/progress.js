$(document).ready(function() {
    var updateProgress = function() {
        $.ajax({
            type: "GET",
            url: "/progress/" + $('#progress').attr('data-id'),
            dataType: "json"
        }).success(function(json) {
            if(json == 100) {
                clearInterval(interval);
            }
            $('#progress').html(json + '%');
            $('#progress-bar').width(json + '%');
        });
    }
    var interval = window.setInterval(updateProgress, 500);
});