let stockChart;
let portfolioInfo;

function renderGraphAndTable(firstTimeRun) {
    var url = new URL("http://localhost:1337/api/v1/portfolioInfo");
    fetch(url).then(response => response.json()).then(data => {
        portfolioInfo = data;
        if (firstTimeRun) {
            initializeGraph();
        } else {
            refreshGraph();
        }
        renderTable();
        setTimeout(renderGraphAndTable, 5000);
    });
}

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

function getGraphDataPoints() {
    let dataPoints = [];
    for (var i = 0; i < portfolioInfo.equity.length; i++) {
        let date = new Date(0);
        date.setUTCSeconds(portfolioInfo.timestamp[i]);
        dataPoints.push({
            "x": date,
            "y": portfolioInfo.equity[i]
        });
    }
    return dataPoints;
}

const tableBody = document.querySelector("#tableBody");

function renderTable() {
    // TODO: populate table with real data instead of filler data (loop through portfolioInfo and add to HTML as needed)

    // *** TEMP - periodic filler data
    var pps = Math.round((Math.random() * 129 + 50) * 100) / 100;
    var shares = Math.floor(Math.random() * 22 + 3);
    var dt = new Date();

    var newEntryHTML = `<tr>
        <th>${ (dt.getMonth()+1).toString().padStart(2, '0')}-${
            dt.getDate().toString().padStart(2, '0')}-${
            dt.getFullYear().toString().padStart(4, '0')}, ${
            dt.getHours().toString().padStart(2, '0')}:${
            dt.getMinutes().toString().padStart(2, '0')}:${
            dt.getSeconds().toString().padStart(2, '0') }
        </th>
        <td>${ (dt.getMonth()+1).toString().padStart(2, '0')}-${
            dt.getDate().toString().padStart(2, '0')}-${
            dt.getFullYear().toString().padStart(4, '0')}, ${
            dt.getHours().toString().padStart(2, '0')}:${
            dt.getMinutes().toString().padStart(2, '0')}:${
            dt.getSeconds().toString().padStart(2, '0') }
        </td>
        <td><abbr title="Apple Inc.">AAPL</abbr></td>
        <td>Market</td>
        <td>$${pps}</td>
        <td>${shares}</td>
        <td class="has-text-success">+ $xx,xxx</td>
    <tr>`;
    tableBody.innerHTML = newEntryHTML + tableBody.innerHTML;
    // *** //
}
