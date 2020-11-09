function showOrderDetails(url) {
    $.ajax({
        type: "GET",
        url: url,
        dataType: "json",
        success: (response) => {
            const mModal = $("#order-details-modal")
            mModal.find(".modal-content").html(response['order'])
            mModal.modal()
        },
        error: (jqXHR, textStatus, errorThrown) => console.log(errorThrown)
    })
}

function loadByStatus({selectId, callBack, url, dataTableId}) {
    $(selectId).on('change', function (object) {
        const selectedVal = parseInt($(this).val())
        const queries = {status: selectedVal}
        if (isNaN(selectedVal)) {
            $.ajax({
                type: "GET",
                url: url,
                dataType: "json",
                success: (response) => $(dataTableId).html(response['orders']),
                error: (jqXHR, textStatus, errorThrown) => console.log(errorThrown)
            })
            return
        }
        $.ajax({
                type: "GET",
                url: url,
                data: queries,
                dataType: "json",
                success: (response) => $(dataTableId).html(response['products']),
                error: (jqXHR, textStatus, errorThrown) => console.log(errorThrown)
            })
    })
}