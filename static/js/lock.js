function sendPasswd() {
  let passwd = $('#pincode').val();
  console.log(passwd);
  $.ajax({
    url: '/teacher_settings',
    type: 'POST',
    data: JSON.stringify({ passwd: passwd }),
    contentType: 'application/json; charset=utf8',
    dataType: 'json',
  })
    .fail(function() {
      $('#wrong-passwd').fadeIn();
      setTimeout(function() {
        $('#wrong-passwd').fadeOut();
      }, 3000);
    })
    .done(function() {
      window.location.href = '/index';
    });
}

numKeyboardModule.createKeyboard('#pincode', 'light');

$('#pincode').click(function() {
  numKeyboardModule.openKeyboard();
});

$('#send-btn').click(function() {
  sendPasswd();
});
