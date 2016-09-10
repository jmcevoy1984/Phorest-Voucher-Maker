var clientTable = document.getElementById('client-table');
var len = clientTable.innerHTML.length;
var voucherTable = document.getElementById('voucher-table');
var vlen = voucherTable.innerHTML.length;

var voucherArray = [];

function load() {
    var drawString = '';
    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/api/client/' + ref);
    xhr.send();
    xhr.onload = function() {
        var resp = JSON.parse(xhr.responseText);
        console.log(resp);
        clientTable.innerHTML = clientTable.innerHTML.slice(0, len - 8) + 
        "<tr>" +
            '<td>' + resp.firstName + '</td>' +
            '<td>' + resp.lastName + '</td>' +
            '<td>' + resp.mobile + '</td>' +
            '<td>' + resp.email + '</td>' +
        "</tr>";
        var req = new XMLHttpRequest();
        req.open('GET', '/client/vouchers' + '?' + 'link=' + resp.vouchers);
        req.send();
        req.onload = function(){
            var response = JSON.parse(req.responseText);
            voucherArray = response.vouchers
            console.log(response);
            for (i = 0; i < voucherArray.length; i++) {
                drawString += '<tr><td>' +       voucherArray[i].serial + "</td><td>€" + voucherArray[i].originalBalance + "</td><td>€" + voucherArray[i].remainingBalance + "</td><td>" + voucherArray[i].issueDate.slice(0, 10) + "</td><td>" + voucherArray[i].expiryDate.slice(0, 10) + "</td></tr>";
            }
            vlen = voucherTable.innerHTML.length;
            voucherTable.innerHTML = voucherTable.innerHTML.slice(0, vlen - 8) + drawString; 
        };
    };
}

load();