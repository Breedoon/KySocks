function isEmail(email) {
    var re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(String(email).toLowerCase());
}

function checkPassword(password) {
    var re = /(?=.*[a-z]).{6,}/;
    return re.test(password);
}


$(document).ready(function () {
    $("#submit-form").click(function (event) {
        event.preventDefault();
    });

});

function clicked(isLogin) {
    var email;
    var password;
    var score = 0;
    if (isLogin) {
        email = $("#login-email");
        password = $("#login-pass");
        if (!isEmail(email.val())) {
            email.addClass("wrong");
            score++;
        } else {
            email.removeClass("wrong");
        }
        if (!checkPassword(password.val())) {
            password.addClass("wrong");
            score++;
        } else {
            password.removeClass("wrong");
        }
        if (score === 0) {
            $.ajax({
                url: Flask.url_for("login"),
                data: {"username": email.val(), "password": password.val()},
                type: "POST",
                success: function (data) {
                    window.location = data;
                }
            })
        }
    } else {
        email = $("#signup-email");
        password = $("#signup-pass");
        var confirmation = $("#signup-conf");
        score = 0;
        if (!isEmail(email.val())) {
            email.addClass("wrong");
            score++;
        } else {
            email.removeClass("wrong");
        }
        if (!checkPassword(password.val())) {
            password.addClass("wrong");
            score++;
        } else {
            password.removeClass("wrong");
        }
        if (password.val() !== confirmation.val()) {
            confirmation.addClass("wrong");
            score++;
        } else {
            confirmation.removeClass("wrong");
        }
        if (score === 0) {
            $.ajax({
                url: Flask.url_for('register'),
                data: {"username": email.val(), "password": password.val(), "confirmation": confirmation.val()},
                type: "POST",
                success: function (data) {
                    window.location = data;
                }
            })
        }
    }
}
