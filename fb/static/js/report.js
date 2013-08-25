/**
 * Report
 */
var Report = function() {
    var self = this;
    self.id = $("#person").attr("data-id");
    self.map;
    self.markers = [];
    self.mapOptions = {
        zoom: 2,
        center: new google.maps.LatLng(50, 4),
        mapTypeId: google.maps.MapTypeId.ROADMAP,
        scrollwheel: false
    };
    self.createMap = function() {
        self.newMap();
    };
    self.newMap = function() {
        self.map = new google.maps.Map(document.getElementById("map-canvas"),self.mapOptions)
    };
    self.clearMarkers = function() {
        for (var i = 0; i < self.markers.length; i++ ) {
            self.markers[i].setMap(null);
        }
        self.markers = [];
    }
    self.createMarkers = function(json) {
        self.clearMarkers()
        for(i=0; i<json.length; i++) {
            self.addMarker(json[i]);
        }
    };
    self.addMarker = function(data) {
        var marker = new google.maps.Marker({
            position: new google.maps.LatLng(data.latitude,data.longitude),
            map: self.map,
            icon: "https://graph.facebook.com/" + data.person.fbid + "/picture?width=30&height=30",
            title: data.location
        });
        self.markers.push(marker);
    };
    self.updateMap = function(url) {
        $.ajax({
            url: "/ajax/" + url + "/" + self.id
        }).done(function(json) {
            self.toggleButton(url);
            self.createMarkers(json);
            self.zoomMap()
        });
    };
    self.toggleButton = function(url) {
        var buttons = $("#report-locations-buttons button");
        buttons.each(function() {
            if($(this).attr('data-url') == url) {
                $(this).addClass('active');
            }
            else {
                $(this).removeClass('active');
            }
        })
    };
    self.zoomMap = function() {
        var latlngbounds = new google.maps.LatLngBounds();
        for (var i = 0; i < self.markers.length; i++) {
            latlngbounds.extend(self.markers[i].position);
        }
        self.map.fitBounds(latlngbounds);
    }
}

/**
 * Wait for the DOM to rock 'n roll!
 */
$(document).ready(function() {

    var report = new Report()
    report.createMap();
    report.updateMap('top-travel-friends');

    $("#report-locations-buttons button").on("click", function() {
        var dataUrl = $(this).attr('data-url');
        report.updateMap(dataUrl);
    });

})