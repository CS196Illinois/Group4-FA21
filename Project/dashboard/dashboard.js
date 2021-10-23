let stockChart;

function initializeGraph() {
    var data = [];
    var dataSeries = {
        type: "spline",
        dataPoints: getGraphDataPoints()
    };
    data.push(dataSeries);

    stockChart = new CanvasJS.StockChart("chartContainer", {
        animationEnabled: true,
        exportEnabled: false,
        charts: [{
            axisX: {
                crosshair: {
                    enabled: true,
                    snapToDataPoint: true
                }
            },
            axisY: {
                crosshair: {
                    enabled: true,
                }
            },
            data: data
        }],
        rangeSelector: {
            inputFields: {
                startValue: "2021-09-29",
                endValue: "2022-01-01",
                valueFormatString: "YYYY-MM-DD"
            },

            buttons: [{
                label: "1 day",
                range: 1,
                rangeType: "day"
            }, {
                label: "5 days",
                range: 5,
                rangeType: "day"
            }, {
                label: "3 months",
                range: 3,
                rangeType: "month"
            }, {
                label: "1 year",
                range: 1,
                rangeType: "year"
            }, {
                label: "All",
                rangeType: "all"
            }]
        }
    });

    stockChart.render();
}

function refreshGraph() {
    var data = [];
    var dataSeries = {
        type: "spline",
        dataPoints: getGraphDataPoints()
    };
    data.push(dataSeries);
    stockChart.charts[0].set("data", data);
}

// TEMP - initial filler data //
let dataPoints = [];
let time = 1633053788;
for (var i = 0; i < 15; i++) {
    dataPoints.push({
        "x": new Date(time * 1000),
        "y": Math.floor(Math.random() * 8000 + 92000)
    });
    time += 33000;
}
// *** //
function getGraphDataPoints() {
    // TODO: fetch & parse data from API and fill dataPoints
    //let dataPoints = [];
    // TEMP - periodic filler data //
    dataPoints.push({
        "x": new Date(time * 1000),
        "y": Math.floor(Math.random() * 8000 + 92000)
    });
    time += 33000;
    // *** //
    return dataPoints;
}
