icons = {'success': 'ti-check', 'danger': 'ti-na'};

function notify(msg, mood) {
    $.notify({
        icon: icons[mood],
        message: msg

    }, {
        type: mood,
        delay: 1200,
        animate: {
            enter: 'animated fadeInRight',
            exit: 'animated fadeOutRight'
        }
    });
}

function buy(product_id, quantity) {
    $.ajax({
        url: Flask.url_for('buy'),
        data: {"product_id": product_id, "add": quantity},
        type: "POST",
        success: function (data) {
            if (data['success']) {
                if ('notify' in data)
                    notify(data['notify'], 'success');
                if ('new_mini_cart' in data)
                    $("#mini-cart-container").html(data['new_mini_cart'])
            } else {
                if ('notify' in data)
                    notify(data['notify'], 'danger');
            }
        }
    })
}

function remove_from_cart(product_id) {
    buy(product_id, 0)
}

function update_price(element, price_change) {
    element.html(String(parseFloat(element.html().substring(0, element.html().length - 5)) + price_change) + " грн.");

}

function update_number(element, change) {
        element.html(parseInt(element.html()) + change);

}

function remove_from_mini_cart(product_id, total_price) {
    $('#cart-item-' + product_id).fadeOut('fast', function (c) {
        $('#cart-item-' + product_id).remove();
    });
    update_price($("#mini-cart-total"), total_price);
    update_number($(".rate"), -1);
    remove_from_cart(product_id)
}

$(document).ready(function (c) { // TODO: fix all to onclicks
    $("#buy-button").click(function (event) {
        event.preventDefault();
    });
});
