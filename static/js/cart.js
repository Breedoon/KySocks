function buy(product_id, quantity) {
    $.ajax({
        url: Flask.url_for('cart'),
        data: {"product_id": product_id, "add": quantity},
        type: "POST",
        success: function (data) {
            if (data !== "Nice!") {
                window.location = data;
            }
        }
    })
}

function buy_func(product_id, quantity, func) {
    $.ajax({
        url: Flask.url_for('cart'),
        data: {"product_id": product_id, "add": quantity},
        type: "POST",
        success: func
    })
}

function update_cart(cart) {
    var value;
    for (value in cart) {
        var diff = $('#' + value + '-quantity')['0'].value - cart[value]['quantity'];
        if (diff != 0) {
            buy(value, diff, function () {
                window.location.reload(false);
            })
        }
    }

}