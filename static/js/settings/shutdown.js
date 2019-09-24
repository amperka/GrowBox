function reboot() {
  $.get('/shutdown/reboot', function() {
    addMsgToDiv(
      '#shutdown-msg',
      'Гроукомпьютер перезагрузится через 10 секунд.'
    );
  }).fail(function() {
    Alert(
      'Ошибка!',
      'Перезагрузите гроукомпьютер принудительно, нажав кнопку питания на задней крышке.'
    );
  });
}

function shutdown() {
  $.get('/shutdown/shutdown', function() {
    addMsgToDiv('#shutdown-msg', 'Гроукомпьютер выключится через 10 секунд.');
  }).fail(function() {
    Alert(
      'Ошибка!',
      'Выключите гроукомпьютер принудительно, нажав кнопку питания на задней крышке.'
    );
  });
}

$('#reboot-btn').click(function() {
  Confirm(
    'Перезагрузить гроукомпьютер',
    'Вы действительно хотите перезагрузить гроукомпьютер?',
    'Да',
    'Нет',
    reboot
  );
});

$('#shutdown-btn').click(function() {
  Confirm(
    'Выключение гроукомпьютера',
    'Вы действительно хотите выключить гроукомпьютер?',
    'Да',
    'Нет',
    shutdown
  );
});
