function checkName(name) {
    var re = /^[_a-zA-Z0-9а-яА-ЯёЁіІїЇ#№ ]+$/;
    return re.test(name)
}

function checkPhone(phone) {
    var re = /^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$/im;
    return re.test(phone)
}

function isEmail(email) {
    var re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(String(email).toLowerCase());
}

function checkPassword(password) {
    var re = /(?=.*[a-z]).{6,}/;
    return re.test(password);
}

function checkout() {
    var score = 0;
    if (!checkName($("#firstname")[0].value)) {
        $("#firstname").addClass("wrong");
        console.log(score);
        score++;
    } else {
        $("#firstname").removeClass("wrong")
    }
    if (!checkName($("#lastname")[0].value)) {
        $("#lastname").addClass("wrong");
        score++;
    } else {
        $("#lastname").removeClass("wrong")
    }
    if (!checkName($("#city")[0].value)) {
        $("#city").addClass("wrong");
        score++;
    } else {
        $("#city").removeClass("wrong")
    }
    if (!checkName($("#delivery")[0].value)) {
        $("#delivery").addClass("wrong");
        score++;
    } else {
        $("#delivery").removeClass("wrong")
    }
    if (!checkPhone($("#phone")[0].value)) {
        $("#phone").addClass("wrong");
        score++;
    } else {
        $("#phone").removeClass("wrong")
    }
    if (!isEmail($("#email")[0].value)) {
        $("#email").addClass("wrong");
        score++;
    } else {
        $("#email").removeClass("wrong")
    }
    if ($("#remember")[0].checked) {
        if (!checkPassword($('#password').val())) {
            $('#password').addClass("wrong");
            score++;
        } else {
            $('#password').removeClass("wrong");
        }
    }
    if (score === 0) {
        var dat = {
            "email": $("#email")[0].value,
            "phone": $("#phone")[0].value,
            "city": $("#city")[0].value,
            "delivery": $("#delivery")[0].value,
            "firstname": $("#firstname")[0].value,
            "lastname": $("#lastname")[0].value
        };
        if ($("#remember")[0].checked) {
            dat['password'] = $('#password').val();
        }
        if ($("#notes").val() !== "") {
            dat['additional'] = $("#notes").val();
        }
        $.ajax({
            url: Flask.url_for('checkout'),
            data: dat,
            type: "POST",
            success: function (data) {
                window.location.replace(data);
            }
        })
    }
}


function boxChecked() {
    if ($("#remember")[0].checked) {
        $('#password').removeAttr('disabled');

    } else {
        $('#password').attr('disabled', true);
    }
}