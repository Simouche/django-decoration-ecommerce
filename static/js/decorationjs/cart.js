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

function addToCart(productID, quantity, cart, url, csrf) {
    const formData = {product: productID, quantity: quantity, cart: cart, csrfmiddlewaretoken: csrf}
    $.ajax({
        url: url,
        type: "POST",
        data: formData,
        success: function (data, textStatus, jqXHR) {
            refreshCart()
            alert("added to cart!")
        },
        error: function (jqXHR, textStatus, errorThrown) {
            console.log(errorThrown)
        }
    })
}