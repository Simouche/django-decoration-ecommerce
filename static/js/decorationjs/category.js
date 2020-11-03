function loadCategoriesSelect({categories, parentSelect, childSelect, callBack, url, dataTableId}) {
    const parsedCategories = JSON.parse(categories)
    $(parentSelect).on('change', function (object) {
        const selectedVal = parseInt($(this).val())
        if (isNaN(selectedVal)) {
            callBack({url: url, dataTableId: dataTableId})
            return
        }
        $(childSelect).empty()
        $(childSelect).append(new Option('Sub-Categories', ''))
        parsedCategories.some(function (category) {
            if (category.id === selectedVal) {
                category.subs.forEach(function (sub) {
                    $(childSelect).append(new Option(sub.name, sub.id))
                })
                callBack({categoryId: selectedVal, url: url, dataTableId: dataTableId})
                return true;
            }
        })
    })
}

function loadSubCategorySelect({selectId, callBack, url, dataTableId}) {
    $(selectId).on('change', function (object) {
        const selectedVal = parseInt($(this).val())
        if (isNaN(selectedVal)) {
            callBack({url: url, dataTableId: dataTableId})
            return
        }
        callBack({subCategoryId: selectedVal, url: url, dataTableId: dataTableId})
    })
}