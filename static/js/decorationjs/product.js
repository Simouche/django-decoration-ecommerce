function createProduct() {

}

function deleteProduct(url, dataId, csrf) {
    $.ajax({
        type: "POST",
        url: url,
        dataType: "json",
        headers: {'csrfmiddlewaretoken': csrf},
        data:{'csrfmiddlewaretoken': csrf},
        success: function (response) {
            // Update page
            $(dataId).html(response["products"]);
        },
        error: function (jqXHR, textStatus, errorThrown) {
            console.log(errorThrown)
        }
    });
}