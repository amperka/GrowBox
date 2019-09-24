function createChart(label) {
  Chart.defaults.global.responsive = false;
  let Canv = document.getElementById('month_chart').getContext('2d');
  let Data = {
    labels: [],
    datasets: [
      {
        label: label,
        fill: true,
        backgroundColor: 'rgba(75,192,192,0.4)',
        borderColor: 'rgba(75,192,192,1)',
        borderCapStyle: 'butt',
        borderDash: [],
        borderDashOffset: 0.0,
        borderJoinStyle: 'miter',
        pointBorderColor: 'rgba(75,192,192,1)',
        pointBackgroundColor: '#fff',
        pointBorderWidth: 1,
        pointHoverRadius: 5,
        pointHoverBackgroundColor: 'rgba(75,192,192,1)',
        pointHoverBorderColor: 'rgba(220,220,220,1)',
        pointHoverBorderWidth: 2,
        pointRadius: 1,
        pointHitRadius: 10,
        data: [],
        spanGaps: false,
      },
    ],
  };

  let Options = {
    scales: {
      xAxes: [
        {
          ticks: {
            autoSkip: true,
            maxTicksLimit: 14,
          },
        },
      ],
    },
  };

  let mainChart = new Chart(Canv, {
    type: 'line',
    data: Data,
    options: Options,
  });

  return mainChart;
}

function addData(chart, labels, data) {
  labels.forEach(element => {
    chart.data.labels.push(element);
  });

  data.forEach(element => {
    chart.data.datasets[0].data.push(element);
  });
  chart.update();
}

function removeData(chart) {
  chart.data.labels = [];
  chart.data.datasets[0].data = [];
  chart.update();
}

function initChart(label, parameter) {
  let mainChart = createChart(label);

  function setChanges(parameter) {
    let hour = document.querySelector('#period-hour');
    let day = document.querySelector('#period-day');
    let week = document.querySelector('#period-week');
    let month = document.querySelector('#period-month');

    let request = { param: parameter };
    if (hour.checked) {
      request.period = 'hour';
    }
    if (day.checked) {
      request.period = 'day';
    }
    if (week.checked) {
      request.period = 'week';
    }
    if (month.checked) {
      request.period = 'month';
    }

    $.ajax({
      url: '/charts/draw_chart',
      type: 'POST',
      data: JSON.stringify(request),
      contentType: 'application/json; charset=utf8',
      dataType: 'json',
      success: function(data) {
        removeData(mainChart);
        addData(mainChart, data.labels, data.data);
        mainChart.render({
          duration: 800,
        });
      },
    });
  }

  $('.custom-control-input').change(function() {
    setChanges(parameter);
  });

  $('#period-hour').prop('checked', true);

  let request = { param: parameter, period: 'hour' };

  $.ajax({
    url: '/charts/draw_chart',
    type: 'POST',
    data: JSON.stringify(request),
    contentType: 'application/json; charset=utf8',
    dataType: 'json',
    success: function(data) {
      addData(mainChart, data.labels, data.data);
      mainChart.render({
        duration: 800,
      });
    },
  });
}
