Chart.defaults.global.responsive = false;
    var Data = {
        labels : [],
        datasets : [{
        label : thislabel,
        fill : true,
        backgroundColor: "rgba(75,192,192,0.4)",
        borderColor: "rgba(75,192,192,1)",
        borderCapStyle: 'butt',
        borderDash: [],
        borderDashOffset: 0.0,
        borderJoinStyle: 'miter',
        pointBorderColor: "rgba(75,192,192,1)",
        pointBackgroundColor: "#fff",
        pointBorderWidth: 1,
        pointHoverRadius: 5,
        pointHoverBackgroundColor: "rgba(75,192,192,1)",
        pointHoverBorderColor: "rgba(220,220,220,1)",
        pointHoverBorderWidth: 2,
        pointRadius: 1,
        pointHitRadius: 10,
        data : [],
        spanGaps: false
        }]
    };

    var Canv = document.getElementById('chartCanv').getContext('2d');
    var chart = new Chart(Canv, {
            type: 'line',
            data: Data
    });
