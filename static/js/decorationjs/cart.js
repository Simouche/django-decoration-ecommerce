function refreshCart() {
    const xhttp = new XMLHttpRequest()
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            document.getElementById("cart_count").innerHTML = this.responseText
        }
    }
    xhttp.open("GET", "/get-cart-count/", true)
    xhttp.send()
}