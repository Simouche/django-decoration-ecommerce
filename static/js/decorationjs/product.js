function createProduct() {

}

function filterProductByCategoryId({categoryId, subCategoryId, url, dataTableId}) {
    const queries = {category: categoryId, sub_category: subCategoryId}
    $.ajax({
        type: "GET",
        url: url,
        data: queries,
        dataType: "json",
        success: (response) => $(dataTableId).html(response['products']),
        error: (jqXHR, textStatus, errorThrown) => console.log(errorThrown)
    })
}

function deleteProduct(url, dataId, csrf) {
    $.ajax({
        type: "POST",
        url: url,
        dataType: "json",
        headers: {'csrfmiddlewaretoken': csrf},
        data: {'csrfmiddlewaretoken': csrf},
        success: function (response) {
            // Update page
            $(dataId).html(response["products"]);
        },
        error: function (jqXHR, textStatus, errorThrown) {
            console.log(errorThrown)
        }
    })
}