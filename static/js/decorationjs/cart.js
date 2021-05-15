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

function addToCart(productID, quantity, cart, url, csrf, size) {
    const formData = {product: productID, quantity: quantity, cart: cart, csrfmiddlewaretoken: csrf, size}
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

