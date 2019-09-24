import Response from '/static/js/tools/response.js';
import getRequest from '/static/js/tools/request.js';

const requestFuncs = (function() {
  const downloadResp = new Response({
    msgYes: 'Журнал успешно скачан.',
    msgNo: 'USB-устройство не обнаружено. Проверьте подключение.',
    msgError: 'Возникла ошибка системы. Перезагрузите гроукомпьютер.',
    preloader: true,
  });

  const extractResp = new Response({
    msgYes: 'USB-устройство может быть извлечено.',
    msgNo: 'USB-устройство не обнаружено. Проверьте подключение.',
    msgError: 'Возникла ошибка системы. Перезагрузите гроукомпьютер.',
  });

  let arrOfResp = [downloadResp, extractResp];

  arrOfResp.forEach(obj => {
    if (typeof obj.msgYes !== 'undefined') {
      obj.success = function() {
        addMsgToDiv('#msg-box', this.msgYes);
      };
    }
    if (typeof obj.msgNo !== 'undefined') {
      obj.fail = function() {
        addMsgToDiv('#msg-box', this.msgNo);
      };
    }
    if (typeof obj.msgError !== 'undefined') {
      obj.error = function() {
        Alert('Ошибка!', this.msgError);
      };
    }
    if (typeof obj.msgNotFound !== 'undefined') {
      obj.notFound = function() {
        addMsgToDiv('#msg-box', this.msgNotFound);
      };
    }
  });

  return {
    downloadLogs: () => getRequest('/download/log', downloadResp, true),
    extractUsb: () => getRequest('/extract_usb', extractResp, true),
  };
})();

$(function() {
  $('#download-button').click(function() {
    Confirm(
      'Скачать журнал',
      'Вы действительно хотите скачать журнал?',
      'Да',
      'Нет',
      requestFuncs.downloadLogs
    );
  });

  $('#extract').click(function() {
    Confirm(
      'Извлечь накопитель',
      'Вы действительно хотите извлечь накопитель?',
      'Да',
      'Нет',
      requestFuncs.extractUsb
    );
  });
});
