var inited = false;
var first_name;
var last_name;
var city;
var delivery;
var phone;
var email;
var password;
var notes;
var remember;

var changes = {};

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

function checkWrong() {
    var score = 0;
    if (first_name !== undefined)
        if (!checkName(first_name.val())) {
            first_name.addClass("wrong");
            console.log(score);
            score++;
        } else {
            first_name.removeClass("wrong")
        }
    if (last_name !== undefined)
        if (!checkName(last_name.val())) {
            last_name.addClass("wrong");
            score++;
        } else {
            last_name.removeClass("wrong")
        }
    if (city !== undefined)
        if (!checkName(city.val())) {
            city.addClass("wrong");
            score++;
        } else {
            city.removeClass("wrong")
        }
    if (delivery !== undefined)
        if (!checkName(delivery.val())) {
            delivery.addClass("wrong");
            score++;
        } else {
            delivery.removeClass("wrong")
        }
    if (phone !== undefined)
        if (!checkPhone(phone.val())) {
            phone.addClass("wrong");
            score++;
        } else {
            phone.removeClass("wrong")
        }
    console.log("Before IF");
    if (email !== undefined)
        console.log("INSIDE IF");
    if (!isEmail(email.val())) {
        console.log("WRONG");
        email.addClass("wrong");
        score++;
    } else {
        console.log("NOT WRONG");
        email.removeClass("wrong")
    }
    if (remember[0].checked) {
        if (password !== undefined)
            if (!checkPassword(password.val())) {
                password.addClass("wrong");
                score++;
            } else {
                password.removeClass("wrong");
            }
    } else {
        if (password !== undefined)
            password.removeClass("wrong");

    }
    return score;
}


function checkout() {
    var score;

    score = checkWrong();

    if (!inited) {
        first_name.change(checkWrong());
        last_name.change(checkWrong());
        city.change(checkWrong());
        delivery.change(checkWrong());
        phone.change(checkWrong());
        email.change(checkWrong());
        password.change(checkWrong());
        remember.change(checkWrong());

        inited = true;
    }

    if (score === 0) {
        var dat = {
            "email": email.val(),
            "phone": phone.val(),
            "city": city.val(),
            "delivery": delivery.val(),
            "first-name": first_name.val(),
            "last-name": last_name.val(),
            "changes": JSON.stringify(changes)
        };
        if ($("#remember")[0].checked) {
            dat['password'] = password.val();
        }
        if (notes.val() !== "") {
            dat['additional'] = notes.val();
        }
        $.ajax({
            url: Flask.url_for('cart'),
            data: dat,
            type: "POST",
            success: function (data) {
                window.location.replace(data);
            }
        })
    }
}



function remove_from_big_cart(product_id, total_price) {
    if (product_id in changes)
        delete changes[product_id];

    $('#cart-table-item-' + product_id).fadeOut('fast', function (c) {
        $('#cart-table-item-' + product_id).remove();
    });
    $('#cart-list-item-' + product_id).fadeOut('fast', function (c) {
        $('#cart-table-item-' + product_id).remove();
    });
    update_price($("#big-cart-total"), total_price);
    remove_from_cart(product_id);
    if ($("#big-cart-total").html() === "0 грн.")
        $(".inner-sec-shop").html("<h1 class=\"title1\">Shopping cart is empty</h1><p class=\"cart\">You have no items in your shopping cart.<br>Click <a href=\"/\">here</a> to\n" +
            "            continue\n" +
            "            shopping</p>")
}

function change_item(product_id, change_quantity, change_price) {
    if ($('#quantity-' + product_id).html() === "1" && change_quantity < 0)
        remove_from_big_cart(product_id, change_quantity * change_price);
    else {
        update_number($('#quantity-' + product_id), change_quantity);
        update_price($("#big-cart-total"), change_quantity * change_price);
        update_price($("#cart-list-item-price-" + product_id), change_quantity * change_price);
        update_price($("#price-" + product_id), change_quantity * change_price);

        if (product_id in changes) {
            changes[product_id] += change_quantity;
        } else {
            changes[product_id] = change_quantity;
        }
    }
}


function boxChecked() {
    if (remember[0].checked) {
        password.removeAttr('disabled');

    } else {
        password.attr('disabled', true);
    }
}

$(document).ready(function (c) {
    first_name = $('input[name=first_name]');
    last_name = $("#last-name");
    city = $("#city");
    delivery = $("#delivery");
    phone = $("#phone");
    email = $("#email");
    password = $("#password");
    notes = $("#notes");
    remember = $("#remember");
});
