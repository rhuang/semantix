$("#search").keyup(function(event){
    var enterKey = 13
    if(event.keyCode == enterKey ){
        $("#search-button").click();
    }
});

$('.popular-site').click(function(){
    var url = $(this).attr('data-url');
    $('#search').val(url);
    $("#search-button").click();
});

$('#search-button').click(function(){
    var spinner = $('#spinner');
    var searchURLError = $('#search-url-error');
    var searchBtn = $('#search-button');
    var searchEl = $("#search");
    var inputURL = searchEl.val();

    // Do some more sanity check to ensure its a valid URL.
    if (inputURL.indexOf('www') != -1){

        searchURLError.addClass('hide');
        $(this).closest('.form-group, .navbar-search').removeClass('focus');
        searchEl.attr('disabled', 'disabled');
        searchBtn.attr('disabled','disabled');

        $('.categories').html("");
        $('.business-name').html("");
        $('.business-type-heading').html("");
        $('.business-type').html("");
        $('.business-type-percentage').html("");
        spinner.removeClass('hide');

        $.get('classify_business', {business_name: JSON.stringify(inputURL)}, function(data){
            data = JSON.parse(data);
            if (data){
                $('.search-heading').fadeOut('fast');
                $('.top-search-spacing').fadeOut('slow');
                $('.business-name').html(data.name);
                $('.business-type-heading').html("Business Type: ")

                if (inputURL === "www.ikea.com/us/en/") {
                    $('.business-name').html("IKEA");
                }

                if (inputURL === "www.mcdonalds.com") {
                    $('.business-name').html("McDonalds");
                }

                var businessType = data.type.label;
                businessType = businessType.replace(/_/g, " ");
                businessType = businessType.toLowerCase().replace(/\b[a-z]/g, function(letter) {
                    return letter.toUpperCase();
                });
                $('.business-type').html(businessType.charAt(0).toUpperCase() + businessType.slice(1) + " | ");

                var probability = data.type.probability * 100;
                probability = probability.toString().substring(0,5);
                $('.business-type-percentage').html(probability + "%");

                setLabels(data.labels);
            }
            searchEl.removeAttr('disabled');
            searchBtn.removeAttr('disabled');
            spinner.addClass('hide');
        });
    }
    else {
        searchURLError.removeClass('hide');
    }
});

function setLabels(data){
    $('.categories').html("");
    for(var key in data) {
        if(data.hasOwnProperty(key)) {
            var categoryData = "";
            for (var i = 0; i < data[key].length; i++) {
                categoryData += "<span class='label-default category-item'>" + data[key][i] + "</span>" + " "
            }
            if (key !== "hours" && key !== "location") {
                $('.categories').append(
                    "<div class='category'>" +
                        "<div class='category-heading'>" +
                        key.charAt(0).toUpperCase() + key.slice(1) + "</div>" +
                        "<hr/>" +
                        "<div class='category-content'>" + categoryData + "</div>" +
                        "</div>"
                )
            }
        }
    }

    if (data["hours"]) {
        var categoryData = "";
        for (var i = 0; i < data["hours"].length; i++) {
            categoryData += "<span class='label-default category-item'>" + data["hours"][i] + "</span>" + "</br>"
        }
        $('.categories').append(
            "<div class='category'>" +
                "<div class='category-heading'>Hours</div>" +
                "<hr/>" +
                "<div class='category-content'>" + categoryData + "</div>" +
                "</div>"
        )
    }

    if (data["location"]) {
        var categoryData = "";
        for (var i = 0; i < data["location"].length; i++) {
            categoryData += "<span class='label-default category-item'>" + data["location"][i] + "</span>" + " "
        }
        $('.categories').append(
            "<div class='category'>" +
                "<div class='category-heading'>Location</div>" +
                "<hr/>" +
                "<div class='category-content'>" + categoryData + "</div>" +
                "</div>"
        )
    }
}

$('.input-group').on('focus', '.form-control', function () {
    $(this).closest('.form-group, .navbar-search').addClass('focus');
});

$('.input-group').on('blur', '.form-control', function () {
    $(this).closest('.form-group, .navbar-search').removeClass('focus');
});


