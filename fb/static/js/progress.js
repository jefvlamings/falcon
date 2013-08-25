$(document).ready(function() {

    var title = document.title;

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
            document.title = title + ' (' +json + '%)';
        });
    }
    var interval = window.setInterval(updateProgress, 500);
});