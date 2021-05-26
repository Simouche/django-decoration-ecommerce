function refreshCart() {
    $.ajax({
        url: "/cart/get-count/",
        type: "GET",
        success: function (data, textStatus, jqXHR) {
            document.getElementById("cart_count").innerHTML = data['count'] ?? 0
        },
        error: function (jqXHR, textStatus, errorThrown) {
            console.log(errorThrown)
        }
    })
}

refreshCart()

function addToCart(productID, quantity, url, csrf, cart, size) {
    const formData = {product: productID, quantity: quantity, csrfmiddlewaretoken: csrf, cart: cart, size}
    console.log(formData)
    $.ajax({
        url: url,
        type: "POST",
        data: formData,
        success: function (data, textStatus, jqXHR) {
            refreshCart()
            $("#successModal").modal()
        },
        error: function (jqXHR, textStatus, errorThrown) {
            console.log(errorThrown)
        }
    })
}

