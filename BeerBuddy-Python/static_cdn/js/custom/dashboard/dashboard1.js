$(function () {
    "use strict";
    var data = [],
        totalPoints = 100


    //Polar Chart
    new Chart(document.getElementById("polar-chart"), {
        type: 'polarArea',
        data: {
            datasets: [
                {
                    label: "Population (millions)",
                    backgroundColor: ["#36a2eb", "#ff6384", "#4bc0c0", "#ffcd56", "#07b107"],
                    data: [2478, 5267, 5734, 3784]
				}
			  ]
        }
    });


    // Pie chart
    new Chart(document.getElementById("pie-chart"), {
        type: 'pie',
        data: {
            datasets: [{
                label: "Population (millions)",
                backgroundColor: ["#2ddb62", "#bcccdc", "#3ca7f9", "#ff484a", "#a78bd5"],
                data: [2478, 5267, 3734, 2784]
			  }]
        }
    });

});

function labelFormatter(label, series) {
    return '<div style="font-size:13px; text-align:center; padding:2px; color: #fff; font-weight: 600;">' +
        label +
        '<br>' +
        Math.round(series.percent) + '%</div>'
}
