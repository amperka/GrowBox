document.addEventListener('DOMContentLoaded', function() {
  let currentDate = new Date();
  let month = appendLeadZero(currentDate.getMonth() + 1);
  let year = currentDate.getFullYear();
  let day = appendLeadZero(currentDate.getDate());
  let hours = appendLeadZero(currentDate.getHours());
  let minutes = appendLeadZero(currentDate.getMinutes());

  document.getElementsByName('set-time')[0].value = hours + ':' + minutes;
  document.getElementsByName('set-date')[0].value =
    day + '-' + month + '-' + year;
});

function setTime() {
  let newTime = document.getElementsByName('set-time')[0].value;
  let newDate = document.getElementsByName('set-date')[0].value;

  if (newTime === '' || newDate === '') {
    return Alert('Предупреждение!', 'Введите корректное значение.');
  }

  $.ajax({
    url: '/apply_time',
    type: 'POST',
    data: JSON.stringify({ 'set-time': newTime, 'set-date': newDate }),
    contentType: 'application/json; charset=utf8',
    dataType: 'json',
    success: function() {
      $('#time-saved').fadeIn();
      setTimeout(function() {
        $('#time-saved').fadeOut(1000);
      }, 3000);
    },
  });
}

$('#dtBox').DateTimePicker({
  dateFormat: 'dd-MM-yyyy',
  shortDayNames: ['Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб'],
  fullDayNames: [
    'Воскресенье',
    'Понедельник',
    'Вторник',
    'Среда',
    'Четверг',
    'Пятница',
    'Суббота',
  ],
  shortMonthNames: [
    '01',
    '02',
    '03',
    '04',
    '05',
    '06',
    '07',
    '08',
    '09',
    '10',
    '11',
    '12',
  ],
  fullMonthNames: [
    'Январь',
    'Февраль',
    'Март',
    'Апрель',
    'Май',
    'Июнь',
    'Июль',
    'Август',
    'Сентябрь',
    'Отктябрь',
    'Ноябрь',
    'Декабрь',
  ],
  titleContentDate: 'Установка даты',
  titleContentTime: 'Установка времени',
  setButtonContent: 'Установить',
  clearButtonContent: 'Очистить',
  incrementButtonContent: '▲',
  decrementButtonContent: '▼',
  buttonsToDisplay: ['SetButton', 'ClearButton'],
  animationDuration: 200,
});

function appendLeadZero(n) {
  if (n <= 9) {
    return '0' + n;
  }
  return n;
}
