function loadCategoriesSelect(categories, parentSelect, childSelect) {
    categories = JSON.parse(categories)
    console.log(categories)
    $(parentSelect).on('change', function (object) {
        console.log($(this).val())
        const selectedVal = $(this).val()
        $(childSelect).html()
        $(childSelect).append(new Option('Sub-Categories', ''))
        categories.forEach(function (category) {
            if (category.id === selectedVal) {
                category.subs.forEach(function (sub) {
                    $(childSelect).append(new Option(sub.name, sub.id))
                })
            }
        })
    })
}