let numKeyboardModule = (function($, window, document) {
    function createKeyboard(selector, theme) {
        let btnClass = "num-btn";
        if (theme === "dark") {
            btnClass = "num-btn dark"
        }
        let Keyboard = window.SimpleKeyboard.default;
        let textsize = new Keyboard({
              onChange: input => onChange(input, selector),
              onKeyPress: button => onKeyPress(button),
              layout: {
                'default': [
                            "1 2 3",
                            "4 5 6",
                            "7 8 9",
                            "* 0 #",
                            "{bksp} x"
                ],
              },
              display: {
                        "{bksp}": "⌫",
              },
              theme: "textsize hg-theme-default hg-layout-dafault",
              buttonTheme: [
              {
                  class: btnClass,
                  buttons: "1 2 3 4 5 6 7 8 9 0 * # {bksp} x"
              },
              ],
              inputPattern: /^[\d,*,#]+$/,
        });
    }

    function onChange(input, selector) {
        document.querySelector(selector).value = input;
    }

    function onKeyPress(button) {
        if (button === "x") {
            closeKeyboard();
        }
    }

    function openKeyboard() {
        $("#keyboard").fadeIn();
    }

    function closeKeyboard() {
        $("#keyboard").fadeOut();
    }

    return {
        createKeyboard: createKeyboard,
        openKeyboard: openKeyboard,
    };

})(jQuery, window, document);
