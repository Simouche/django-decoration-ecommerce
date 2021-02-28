function loadByType({selectId, callBack, url, dataTableId, responseObjectName = "complaints"}) {
    $(selectId).on('change', function (object) {
        const selectedVal = $(this).val()
        const queries = {type: selectedVal}
        $.ajax({
            type: "GET",
            url: url,
            data: queries,
            dataType: "json",
            success: (response) => $(dataTableId).html(response[responseObjectName]),
            error: (jqXHR, textStatus, errorThrown) => console.log(errorThrown)
        })

    })
}