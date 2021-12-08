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
    for (let i = 0; i < portfolioInfo.equity.length; i++) {
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
    let tableBodyHTML = "";
    for (let i = 0; i < portfolioInfo.orders.length; i++) {
        let order = portfolioInfo.orders[i];
        let datePlaced = new Date(order.placed_at);
        tableBodyHTML += `<tr><th>${ (datePlaced.getMonth()+1).toString().padStart(2, '0')}-${
            datePlaced.getDate().toString().padStart(2, '0')}-${
            datePlaced.getFullYear().toString().padStart(4, '0')}, ${
            datePlaced.getHours().toString().padStart(2, '0')}:${
            datePlaced.getMinutes().toString().padStart(2, '0')}:${
            datePlaced.getSeconds().toString().padStart(2, '0') }
        </th>`
        if (order.filled_at !== "None") {
            let dateExecuted = new Date(order.filled_at);
            tableBodyHTML += `<td>${ (dateExecuted.getMonth()+1).toString().padStart(2, '0')}-${
                dateExecuted.getDate().toString().padStart(2, '0')}-${
                dateExecuted.getFullYear().toString().padStart(4, '0')}, ${
                dateExecuted.getHours().toString().padStart(2, '0')}:${
                dateExecuted.getMinutes().toString().padStart(2, '0')}:${
                dateExecuted.getSeconds().toString().padStart(2, '0') }
            </td>`;
        } else {
            tableBodyHTML += "<td>Unfilled</td>"
        }
        tableBodyHTML += `<td><abbr title="">${order.ticker}</abbr></td>`;
        tableBodyHTML += `<td>${order.type.charAt(0).toUpperCase() + order.type.slice(1)}</td>`;
        tableBodyHTML += `<td>${order.pps ? "$" + order.pps : "Unfilled"}</td>`;
        if (order.filled_quantity === order.quantity || order.filled_quantity === "0") {
            tableBodyHTML += `<td>${order.quantity}</td>`;
        } else {
            tableBodyHTML += `<td>${order.filled_quantity + " of " + order.quantity}</td>`;
        }
        if (order.filled_quantity === "0") {
            tableBodyHTML += `<td class="has-text-link">Unfilled</td>`;
        } else if (order.buy_or_sell === "buy") {
            tableBodyHTML += `<td class="has-text-danger">- $${order.filled_quantity * order.filled_avg_price}</td>`;
        } else {
            tableBodyHTML += `<td class="has-text-success">+ $${order.filled_quantity * order.filled_avg_price}</td>`;
        }
        tableBodyHTML += "<tr>";
    }
    tableBody.innerHTML = tableBodyHTML;
}
