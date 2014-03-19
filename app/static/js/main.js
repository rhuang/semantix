// on enter while on search
$("#search").keyup(function(event){
    var enterKey = 13
    if(event.keyCode == enterKey ){
        $("#search-button").click();
    }
});

var categoryData;


$('#search-button').on('click', function(evt){
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
        spinner.removeClass('hide');

     
        $.get('classify_business', {business_name: JSON.stringify(inputURL)}, function(data){
            data = JSON.parse(data);
            if (data){
                $('.search-heading').fadeOut('fast');
                $('.top-search-spacing').fadeOut('slow');
                $('.business-name').html(data.name);
                $('.business-type-heading').html("Business Type: ")

                var businessType = data.type.label;
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
                if (key === "hours" || key === "location") {
                    categoryData += "<span class='label-default category-item'>" + data[key][i] + "</span>" + "</br>"
                }
                else {
                    categoryData += "<span class='label-default category-item'>" + data[key][i] + "</span>" + " "
                }
            }
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

$('.input-group').on('focus', '.form-control', function () {
    $(this).closest('.form-group, .navbar-search').addClass('focus');
});

$('.input-group').on('blur', '.form-control', function () {
    $(this).closest('.form-group, .navbar-search').removeClass('focus');
});


