function globalSearch(text) {
    if (text.length == 0) {
        // ToDo update the document and set its text to ""
        return
    }
    const xhttp = new XMLHttpRequest()
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            //ToDo update the document with the new List
        }
    }
    xhttp.open('GET', 'url of search', true)
    xhttp.send()
}