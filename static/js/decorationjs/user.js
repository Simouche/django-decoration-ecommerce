function deleteUser(url, dataId, csrf) {
    $.ajax({
        type: "POST",
        url: url,
        dataType: "json",
        headers: {'csrfmiddlewaretoken': csrf},
        data: {'csrfmiddlewaretoken': csrf},
        success: function (response) {
            // Update page
            $(dataId).html(response["users"]);
        },
        error: function (jqXHR, textStatus, errorThrown) {
            console.log(errorThrown)
        }
    })
}

function filterUserByGroup({groupId, url, dataTableId}) {
    const queries = {group: groupId}
    $.ajax({
        type: "GET",
        url: url,
        data: queries,
        dataType: "json",
        success: (response) => $(dataTableId).html(response['users']),
        error: (jqXHR, textStatus, errorThrown) => console.log(errorThrown)
    })
}