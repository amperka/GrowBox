var keyboardModule = (function($, window, document) {
    let Keyboard = window.SimpleKeyboard.default;
    let keyboard = new Keyboard({
        onChange: input => onChange(input),
        onKeyPress: button => onKeyPress(button),
        layout: {
            'default': [
                "1 2 3 4 5 6 7 8 9 0",
                "q w e r t y u i o p",
                " a s d f g h j k l ",
                "{lock} z x c v b n m {bksp}",
                "{shift} {space} . {esc}"
            ],
            'shift': [
                "1 2 3 4 5 6 7 8 9 0",
                "+ ` ~ = / _ { } [ ]",
                "! @ # $ % ^ & * ( )",
                "{lock} - ' \" : ; , ? {bksp}",
                "{shift} {space} . {esc}"
            ],
            'lock': [
                "1 2 3 4 5 6 7 8 9 0",
                "Q W E R T Y U I O P",
                " A S D F G H J K L ",
                "{lock} Z X C V B N M {bksp}",
                "{shift} {space} . {esc}"
            ],
        },
        theme: "hg-theme-default hg-layout-default",
        mergeDisplay: true,
        display: {
            "{bksp}": "⌫",
            "{lock}": "⇪",
            "{shift}": "⌘",
        },
        buttonTheme: [
            {
                class: "keyboard-btn dark textsize",
                buttons: "1 2 3 4 5 6 7 8 9 0 \
                          q w e r t y u i o p \
                          a s d f g h j k l \
                          z x c v b n m \
                          Q W E R T Y U I O P \
                          A S D F G H J K L \
                          Z X C V B N M \
                          {space} . \
                          + ` ~ = / _ { } [ ] \
                          ! @ # $ % ^ & * ( ) \
                          - ' \" : ; , ? ",
            },
            {
                class: "space-btn",
                buttons: "{space}",
            },
            {
                class: "keyboard-btn control-btn textsize",
                buttons: "{shift} {esc} {bksp} {lock}",
            },
            {
                class: "dot-btn",
                buttons: ".",
            },
            {
                class: "empty-btn",
                buttons: " ",
            }
        ]
    });

    document.querySelectorAll(".input").forEach(input => {
        input.addEventListener("focus", onInputFocus);
    });

    function onInputFocus(event) {
        selectedInput = `#${event.target.id}`;
        keyboard.setOptions({
            inputName: event.target.id
        });
    }

    function onChange(input) {
        console.log("Input changed", input); //testing
        document.querySelector(selectedInput || ".input").value = input;
    }

    function closeKeyboard() {
        $("#keyboard").fadeOut();
    }

    function onKeyPress(button) {
        console.log("Button pressed", button); //testing
        switch(button) {
            case "{shift}":
                handleShift();
                break;
            case "{lock}":
                handleLock();
                break;
            case "{esc}":
                closeKeyboard();
            default:
                break;
        }
    }

    function handleShift() {
        let currentLayout = keyboard.options.layoutName;
        let shiftToggle = currentLayout === "default" ? "shift" : "default";

        keyboard.setOptions({
            layoutName: shiftToggle
        });
    }

    function handleLock () {
        let currentLayout = keyboard.options.layoutName;
        let lockToggle = currentLayout === "default" ? "lock" : "default";
        keyboard.setOptions({
            layoutName: lockToggle
        });
    }

    return {
        openKeyboard: function () {
            $("#keyboard").fadeIn();
        },
    };

})(jQuery, window, document);
