var request = new XMLHttpRequest();

request.open('GET', 'http://localhost:8888/init', true);
request.onload = function () {

    // Begin accessing JSON data here
    var data = JSON.parse(this.response);
    if (request.status >= 200 && request.status < 400) {
        var cell_hash = data.cell_hash;
        var grid = data.grid;
    } else {
        console.log('error');
    }
}

request.send();
