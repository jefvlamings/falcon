$(document).ready(function() {

    var title = document.title;

    var updateProgress = function() {
        $.ajax({
            type: "GET",
            url: "/ajax/progress/" + $('#progress').attr('data-id') + '/',
            dataType: "json"
        }).success(function(json) {
            if(json == 100) {
                clearInterval(interval);
            }
            $('#progress').html(json.percentage + '%');
            $('#progress-bar').width(json.percentage + '%');
            $('#progress-description').html(json.description);
            document.title = title + ' (' +json.percentage + '%)';
        });
    }
    var interval = window.setInterval(updateProgress, 500);
});