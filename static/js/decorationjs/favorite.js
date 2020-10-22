function addToFavorite(productID, profileID, url, csrf) {
    const formData = {profile: profileID, product: productID, csrfmiddlewaretoken: csrf}
    $.ajax({
        url: url,
        type: "POST",
        data: formData,
        success: function (data, textStatus, jqXHR) {
            alert("added!")
        },
        error: function (jqXHR, textStatus, errorThrown) {
            console.log(errorThrown)
        }
    })
}