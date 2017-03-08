function getParameterByName(name, url) {
    if (!url) url = window.location.href;
    name = name.replace(/[\[\]]/g, "\\$&");
    var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
        results = regex.exec(url);
    if (!results) return null;
    if (!results[2]) return '';
    return decodeURIComponent(results[2].replace(/\+/g, " "));
}

function getIdFromURL(){
    var parts = window.location.pathname.split('/');
    var thesis_id = parts.pop();
    if (thesis_id == '') {
        thesis_id = parts.pop();
    }
    return thesis_id
}
