/**
 * Map
 */
var ReportMap = function() {
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
    self.create = function() {
        self.new();
    };
    self.new = function() {
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
            icon: "https://graph.facebook.com/" + data.person.fbid + "/picture?width=20&height=20",
            title: data.location + " (" + data.person.name + ")"
        });
        self.markers.push(marker);
    };
    self.update = function(url) {
        $.ajax({
            url: "/ajax/" + url + "/" + self.id
        }).done(function(json) {
            self.toggleButton(url);
            self.createMarkers(json);
            self.zoom()
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
    self.zoom = function() {
        var latlngbounds = new google.maps.LatLngBounds();
        for (var i = 0; i < self.markers.length; i++) {
            latlngbounds.extend(self.markers[i].position);
        }
        self.map.fitBounds(latlngbounds);
    };
    self.init = function() {
        self.create();
        self.update('top-travels');
        $("#report-locations-buttons button").on("click", function() {
            var dataUrl = $(this).attr('data-url');
            self.update(dataUrl);
        });

    };
    self.init();
}

/**
 * Demographics
 */
var ReportDemographics = function() {
    var self = this;
    self.chart;
    self.yMin = 0;
    self.yMax = 0;
    self.xCategories = function() {
        var xCategories = []
        for(var i = self.yMin; i<self.yMax; i++) {
            xCategories.push(i);
        }
        return xCategories;
    };
    self.calculateYMin = function() {
        var maleLowestAge = Math.min.apply(Math, reportMaleAges);
        var femaleLowestAge = Math.min.apply(Math, reportFemaleAges);
        self.yMin = Math.min(maleLowestAge, femaleLowestAge);
    };
    self.calculateYMax = function() {
        var maleHighestAge = Math.max.apply(Math, reportMaleAges);
        var femaleHighestAge = Math.max.apply(Math, reportFemaleAges);
        self.yMax = Math.min(maleHighestAge, femaleHighestAge);
    };
    self.processAges = function(ages, negative, percentages) {
        var counts = [];
        for(var i = self.yMin; i<self.yMax; i++) {
            var count = 0
            for(var j = 0; j<ages.length; j++) {
                if(i == ages[j]) {
                    count++
                }
            }
            if(percentages == true) {
                count = (count / ages.length * 100);
            }
            if(negative === true) {
                counts.push(-count);
            }
            else {
                counts.push(count);
            }
        }
        return counts;
    };
    self.newChart = function() {
        $('#demographics-chart').highcharts({
            chart: {
                type: 'column'
            },
            colors: [
                '#2f7ed8',
                '#ff5f51'
            ],
            title: {
                text: null
            },
            xAxis: [
                {
                    categories: self.xCategories(),
                    reversed: false
                },
                {
                    // mirror axis on right side
                    opposite: true,
                    reversed: false
                }
            ],
            yAxis: {
                title: {
                    text: null
                }
            },
            plotOptions: {
                series: {
                    stacking: 'normal'
                }
            },
            tooltip: {
                formatter: function(){
                    return '<b>'+ this.series.name +', age '+ this.point.category +'</b><br/>'+
                        'Population: '+ Highcharts.numberFormat(Math.abs(this.point.y), 0);
                }
            },
            series: [{
                name: 'Male',
                data: self.processAges(reportMaleAges, false, true)
            }, {
                name: 'Female',
                data: self.processAges(reportFemaleAges, true, true)
            }]
        });
        self.chart = $('#demographics-chart').highcharts();
    };
    self.toggleButton = function(url) {
        var buttons = $("#report-demographics-buttons button");
        buttons.each(function() {
            if($(this).attr('data-url') == url) {
                $(this).addClass('active');
            }
            else {
                $(this).removeClass('active');
            }
        })
    };
    self.updateChart = function(dataUrl) {
        self.toggleButton(dataUrl)
        if(dataUrl == 'totals') {
            self.chart.series[0].setData(self.processAges(reportMaleAges, false, false));
            self.chart.series[1].setData(self.processAges(reportFemaleAges, true, false));
        }
        else {
            self.chart.series[0].setData(self.processAges(reportMaleAges, false, true));
            self.chart.series[1].setData(self.processAges(reportFemaleAges, true, true));
        }
    };
    self.init = function() {
        self.calculateYMin();
        self.calculateYMax();
        self.newChart();
        $("#report-demographics-buttons button").on("click", function() {
            var dataUrl = $(this).attr('data-url');
            self.updateChart(dataUrl);
        });
    };
    self.init();
}

/**
 * Relationships
 */
var ReportRelationships = function() {
    var self = this;
    self.chart;
    self.xLabels = [
        "Single", "In a relationship", "Engaged", "Married", "It's complicated", "In an open relationship", "Widowed",
        "Separated", "Divorced", "In a civil union", "in a domestic partnership", "Unknow"
    ];
    self.xCategories = [
        "S", "R", "E", "M", "C", "O", "W",
        "Q", "D", "U", "P", "X"
    ];
    self.processRelationships = function(relationships, percentages) {
        var counts = [];
        for(var i = 0; i<self.xCategories.length; i++) {
            var count = 0
            for(var j = 0; j<relationships.length; j++) {
                if(self.xCategories[i] == relationships[j]) {
                    count++
                }
            }
            if(percentages === true) {
                count = (count / relationships.length * 100);
            }
            counts.push(count);
        }
        return counts;
    };
    self.newChart = function() {
        $('#relationships-chart').highcharts({
            chart: {
                type: 'column'
            },
            colors: [
                '#2f7ed8',
                '#ff5f51'
            ],
            title: {
                text: null
            },
            xAxis: [
                {
                    categories: self.xLabels
                }
            ],
            yAxis: {
                title: {
                    text: null
                }
            },
            tooltip: {
                formatter: function(){
                    return '<b>'+ this.series.name +', age '+ this.point.category +'</b><br/>'+
                        'Population: '+ Highcharts.numberFormat(Math.abs(this.point.y), 0);
                }
            },
            series: [{
                name: 'Male',
                data: self.processRelationships(reportMaleRelationships, true)
            }, {
                name: 'Female',
                data: self.processRelationships(reportFemaleRelationships, true)
            }]
        });
        self.chart = $('#relationships-chart').highcharts();
    };
    self.updateChart = function(dataUrl) {
        self.toggleButton(dataUrl)
        if(dataUrl == 'totals') {
            self.chart.series[0].setData(self.processRelationships(reportMaleRelationships, false));
            self.chart.series[1].setData(self.processRelationships(reportFemaleRelationships, false));
        }
        else {
            self.chart.series[0].setData(self.processRelationships(reportMaleRelationships, true));
            self.chart.series[1].setData(self.processRelationships(reportFemaleRelationships, true));
        }
    };
    self.toggleButton = function(url) {
        var buttons = $("#report-relationship-buttons button");
        buttons.each(function() {
            if($(this).attr('data-url') == url) {
                $(this).addClass('active');
            }
            else {
                $(this).removeClass('active');
            }
        })
    };
    self.init = function() {
        self.newChart();
        $("#report-relationship-buttons button").on("click", function() {
            var dataUrl = $(this).attr('data-url');
            self.updateChart(dataUrl);
        });
    };
    self.init();
}

/**
 * Wait for the DOM to rock 'n roll!
 */
$(document).ready(function() {

    // Instantiate map
    var reportMap = new ReportMap();

    // Instantiate Demographics chart
    var demoChart = new ReportDemographics();

    // Instantiate Relationshop chart
    var relationshipChart = new ReportRelationships();

});