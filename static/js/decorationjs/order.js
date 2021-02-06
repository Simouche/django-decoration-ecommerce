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
        const selectedVal = $(this).val()
        const queries = {status: selectedVal}
        $.ajax({
            type: "GET",
            url: url,
            data: queries,
            dataType: "json",
            success: (response) => $(dataTableId).html(response['orders']),
            error: (jqXHR, textStatus, errorThrown) => console.log(errorThrown)
        })

    })
}

function loadByState({selectId, callBack, url, dataTableId, responseObjectName = "orders"}) {
    $(selectId).on('change', function (object) {
        const selectedVal = $(this).val()
        const queries = {state: selectedVal}
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

function loadByCity({selectId, callBack, url, dataTableId, responseObjectName = "orders"}) {
    $(selectId).on('change', function (object) {
        const selectedVal = $(this).val()
        const queries = {city: selectedVal}
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


function loadByStatusSales({selectId, callBack, url, dataTableId}) {
    $(selectId).on('change', function (object) {
        const selectedVal = $(this).val()
        const queries = {status: selectedVal}
        $.ajax({
            type: "GET",
            url: url,
            data: queries,
            dataType: "json",
            success: (response) => $(dataTableId).html(response['sales']),
            error: (jqXHR, textStatus, errorThrown) => console.log(errorThrown)
        })

    })
}