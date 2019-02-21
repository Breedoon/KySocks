function close_dialog() {
    $('.cd-popup').removeClass('is-visible');

}

function open_dialog() {
    $('.cd-popup').addClass('is-visible');
}

jQuery(document).ready(function ($) {

    //close popup
    $('.cd-popup').on('click', function (event) {
        if ($(event.target).is('.cd-popup-close') || $(event.target).is('.cd-popup')) {
            event.preventDefault();
            $(this).removeClass('is-visible');
        }
    });
    document.querySelector('body').onkeyup = function (event) {
        if (event.keyCode === 27) {
            $('.cd-popup').removeClass('is-visible');
        }
    };
});