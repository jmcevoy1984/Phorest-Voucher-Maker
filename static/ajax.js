//Basic Javascript to pull vouchers in JSON using AJAX calls from the API server.
//If there is no client reference attached the name of the client is set to "Walk-In"
//If there is a client reference then we fire that in an AJAX call and we append the client's name to the row.

var ajaxImg = "<img src='/static/three_block.gif'>";
var searchButton = document.getElementById('search-button');
var table = document.getElementById('table');
var text = '';
var clientName = '';
var start = -25;
var max = 25;
var len = table.innerHTML.length - 8;
            
searchButton.onclick = search;

pull('next');//Initial function call to populate table.


//Set button onlcick handler functions.
document.getElementById('next').onclick = function(){
    pull('next');
};

document.getElementById('prev').onclick = function(){
    pull('prev');
};

//Function for adding a row to the table
function writeHtml(string){
        table.innerHTML = table.innerHTML.slice(0, table.innerHTML.length - 8) + string;
    }

//Main 'pull' function for retrieving vouchers from the server in batches of 25 at a time.
function pull(direction){

    if (direction === 'prev'){

        if (start >= max){
            start -= max;
        }
    }
    else if (direction === "next"){
        start += max;
    }

    //Sets the display for the range of vouchers currently listed. eg: 1 - 25
    var title = document.getElementById('results');
    title.innerHTML = "Showing : " + ((start + 1)) + " - " + (start + max);

    var voucherArray = [];
    var ajaxQueue = [];
    var resultsArray = [];
    var xhr = new XMLHttpRequest();
    //Send initial AJAX call to the server with parameters in the query string.
    xhr.open('GET', '/api/vouchers' + '?' + 'start=' + start + '&max=' + max );
    xhr.send();
    xhr.onload = function(){
        var resp = JSON.parse(this.responseText);
        resultsArray = resp.voucher_list;

        //Loop through the results of the AJAX call and creates a HTML string. Stores the string in the voucherArray.
        //This is done so that we can use each indexed string in the writeHtml function and edit them later.
        for (i = 0; i < resultsArray.length; i++){
            //Give the cell holding the client name an id that contains it's index. This means we can easily reference this cell with later AJAX calls to retrieve the name of the client and append this string.
            voucherArray[i] = "<tr><td id=" + "'clientName" + i + "'>" + "Walk-In" + "</td><td>" + resultsArray[i].serial + "</td><td>€" + resultsArray[i].originalBalance + "</td><td>€" + resultsArray[i].remainingBalance + "</td><td>" + resultsArray[i].issueDate.slice(0, 10) + "</td><td>" + resultsArray[i].expiryDate.slice(0, 10) + "</td></tr>";
            if (resultsArray[i].clientCardRef !== ''){
                ajaxQueue.push([resultsArray[i], i]);//Append to a queue of AJAX calls to be executed later. Adds the original index too so it can easily be back referenced to make changes.
            }

        }

        //Sets table back to it's inital state containing only headers each time the function is called.
        //Then when using writeHtml function we loop through the voucherArray and add the contents of each index to a row in the table.
        table.innerHTML = table.innerHTML.slice(0, len);
        //console.log(table.innerHTML);
        for (i = 0; i < voucherArray.length; i++){
            writeHtml(voucherArray[i]);
        }

        //Simply logs how many AJAX calls we have queued for debugging.
        console.log("Ajax Queue: " + ajaxQueue.length);

        //If there are any AJAX calls in the queue we fire them off and retrieve the attached client's name.
        //Then we edit the HTML at the corresponding row in the cell we have given an id to which contains it's index.
        //This is why we stored the strings in voucherArray, gave them each an id containing their index and finally
        //also added the index along with the JSON object itself to the AJAX queue so that we can easily make changes.
        if (ajaxQueue.length > 0){

            for (i = 0; i < ajaxQueue.length; i++){
                document.getElementById('clientName' + ajaxQueue[i][1]).innerHTML = ajaxImg;
                var req = new XMLHttpRequest();
                req.open('GET', '/api/client/' + ajaxQueue[i][0].clientCardRef);
                req.send();
                req.onload = (function(value){
                    return function(){
                    var response = JSON.parse(this.responseText);
                    document.getElementById('clientName'+ ajaxQueue[value][1]).innerHTML = "<a href='/clients/" + response.ref + "'>" + response.firstName + " " +response.lastName + '</a>';
                    }})(i);
                }
            }
    };

}//end 'pull' function

function search(){
    var loadGif = document.getElementById('loading-gif');
    loadGif.innerHTML = ajaxImg;
    var search = document.getElementById('search-box');
    var searchValue = search.value;
    var req = new XMLHttpRequest();
    req.open('GET', '/search');
    req.send();
    req.onload = function(){
    var resp = JSON.parse(req.responseText);
    resp = resp.Vouchers;

    for(i = 0; i < resp.length; i++){
        if (resp[i].serial === searchValue){
            var voucherStr = "<tr><td id='clientName'>" + 
                "Walk-In" + "</td><td>" + resp[i].serial + "</td><td>€" + resp[i].originalBalance + "</td><td>€" + resp[i].remainingBalance + "</td><td>" + resp[i].issueDate.slice(0, 10) + "</td><td>" + resp[i].expiryDate.slice(0, 10) + "</td></tr>";
            table.innerHTML = table.innerHTML.slice(0, len) + voucherStr;
            document.getElementById('header').innerHTML = "<div class='alert alert-success'>Serial <strong>" + resp[i].serial + "</strong> found!</div>";
            console.log(resp[i]);
            break;
        }
        if ( i === resp.length - 1 ){
            table.innerHTML = table.innerHTML.slice(0, len);
            document.getElementById('header').innerHTML = "<div class='alert alert-danger'>Serial <strong>" + searchValue + "</strong> not found.</div>";
        }
    }

    loadGif.innerHTML = '';

    }
}//End 'search' function.
