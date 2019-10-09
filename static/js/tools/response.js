export default class Response {
  constructor(obj) {
    this.msgYes = obj.msgYes;
    this.msgNo = obj.msgNo;
    this.msgError = obj.msgError;
    this.msgNotFound = obj.msgNotFound;
    this.preloader = obj.preloader || false;
    this._success = undefined;
    this._fail = undefined;
    this._notFound = undefined;
    this._error = undefined;
  }
  callback(status) {
    let callMethod;
    switch (status) {
      case 200:
        callMethod = '_success';
        break;
      case 403:
        callMethod = '_fail';
        break;
      case 404:
        callMethod = '_notFound';
        break;
      case 500:
        callMethod = '_error';
        break;
      default:
        callMethod = '_error';
        break;
    }
    if (typeof this[callMethod] === 'function') {
      this[callMethod]();
    } else {
      throw new TypeError(callMethod + ' is not a function');
    }
  }
  set success(func) {
    this._success = func;
  }
  set fail(func) {
    this._fail = func;
  }
  set error(func) {
    this._error = func;
  }
  set notFound(func) {
    this._notFound = func;
  }
}
