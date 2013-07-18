$('.search-button').on('click', function(evt){
    $('.data-header small').html('California Pizza Kitchen');
    $('#locationTags_tagsinput').html('Loading...');
    $('.data-name').html('California Pizza Kitchen');
    $('.data-business').html('Restaurant');
    $('.data-hours').html('Unknown');
    $.ajax({
        url: '/locations',
    }).done(function(addresses){
    	var locationsHTML = '';
    	JSON.parse(addresses).forEach(function(address){
            locationsHTML += '<span class="tag"><span>' + address.trim() + '</span></span>';
    	});
    	locationsHTML += 
    		'<input id="locationTags_tag" value="" data-default="" ' +
    		'style="color: rgb(102, 102, 102); width: 12px;"></div></div>';
    	$('#locationTags_tagsinput').html(locationsHTML);
    });
    $.ajax({
        url: '/menu',
    }).done(function(menu){
        var menuHTML = '';
        JSON.parse(menu).forEach(function(menuItem){
            menuHTML += '<span class="tag"><span>' + menuItem.trim() + '</span></span>';
        });
        menuHTML +=
    		'<input id="menuTags_tag" value="" data-default="" ' +
    		'style="color: rgb(102, 102, 102); width: 12px;"></div></div>';
    	$('#menuTags_tagsinput').html(menuHTML);
    });
    $('.data-wrap').removeClass('hide');
});

//this is the data that is obtained by making a call to 
//businesscategories.getCategories()
var data;
var selectOptionsHTML='';
$(function() {
    $.ajax({
        url: '/business_categories',
    }).done(function(get_request){
        selectOptionsHTML += '<option>Select Category</option>';
        data = JSON.parse(get_request);
        $.each(data, function(key, val){
            recursiveFunction(key, val);
        });
        $('#categoryA_select').html(selectOptionsHTML);
        $('#categoryB_select').html(selectOptionsHTML);
        $("select").selectpicker({
            style: 'btn-inverse',
            menuStyle: 'dropdown-inverse'
        });
    });
});

//used to set up the categories in the drop down select menu
function recursiveFunction(key, val) {
    if (val instanceof Array) {
        makeOption(key);
    } else if (val instanceof Object) {
        makeOptGroup(key);
        $.each(val, function(key, value) {
            recursiveFunction(key, value);
        });
    }
}

//helper for recursiveFunction
//simply makes html that will be put into the select element
function makeOptGroup(key) {
    selectOptionsHTML += '<optgroup label="' + key + '">';
}

//helper for recursiveFunction
//simply makes html that will be put into the select element
function makeOption(key) {
    selectOptionsHTML += '<option>' + key + '</option>';
}

//This makes the two main boxes with the draggable items droppable
//which means it allows elements with draggable class to be put into
//these boxes
$(function() {
    $("#catATags_tagsinput").droppable({
      accept: "#catBTags_tagsinput > span",
      drop: function( event, ui ) {
        var select_option = $("#categoryA_select").val();
        if(select_option != "Select Category") {
            deleteSpan( ui.draggable, "#catBTags_tagsinput", "#catATags_tagsinput");
        }
      }
    });

    $("#catBTags_tagsinput").droppable({
      accept: "#catATags_tagsinput > span",
      drop: function( event, ui ) {
        var select_option = $("#categoryB_select").val();
        if(select_option != "Select Category") {
            deleteSpan(ui.draggable, "#catATags_tagsinput", "#catBTags_tagsinput");
        }
      }
    });
});

//helper for when an element is dropped in the opposite box, need to remove it
//from its original box and add it to its new box
function deleteSpan($item, removeFrom, moveTo) {
    var $list = $(moveTo);
    $item.find(removeFrom).remove();
    $item.appendTo($list);
}

//This function helps to find the words that will be made into
//draggable tags when something from the dropdown menu is selected
var wordsList
function searchForKey(key, obj) {
    $.each(obj, function(term, val){
        if(key == term && $.isArray(val)) {
            wordsList = val;
        } else if(!$.isArray(val)) {
            searchForKey(key, val);
        }
    });
}

//this functions finds all elements with draggable class
// and makes them draggable using the JQuery API
function setDraggable() {
    $('.draggable').draggable({
        revert: "invalid",
        stack: ".draggable",
        helper: "clone",
        appendTo: "#draggable_container"
    });
}

//This following 2 onChange functions do the following
//when the select option changes we need to fill in the box below
//with the words for that category which will be draggable items
$("#categoryA_select").change(function() {
    key = $(this).val();
    if(key != "Select Category") {
        searchForKey(key, data);
        var catA_HTML = '';
        for (var i in wordsList) {
            var word = wordsList[i]
            catA_HTML += '<span class="tag draggable"><span>' + word + 
            '<a class="tagsinput-remove-link"></a></span></span>';
        }
        $('#catATags_tagsinput').html(catA_HTML);
        setDraggable();
        setTagRemoval();
    } else {
        $('#catATags_tagsinput').html('');
    }
});

$("#categoryB_select").change(function() {
    key = $(this).val();
    if(key != "Select Category") {
        searchForKey(key, data);
        var catB_HTML = '';
        for (var i in wordsList) {
            var word = wordsList[i]
            catB_HTML += '<span class="tag draggable"><span>' + word + 
            '<a class="tagsinput-remove-link"></a></span></span>';
        }
        $('#catBTags_tagsinput').html(catB_HTML);
        setDraggable();
        setTagRemoval();
    } else {
        $('#catBTags_tagsinput').html('');
    }
});

//When you click on the X on a draggable item this funtion helps to
//remove that draggable item
function setTagRemoval() {
    $('.tagsinput-remove-link').click(function(event) {
        $(event.target).closest('span[class^="tag"]').remove();
    });
}

//for the two following onClick handlers (for the plus icon) when clicked 
//take the text in the input element and make that into a draggable 
//tag which is added into the box below
$('#add_categoryA_label').click(function(event) {
    var $input = $(event.target).siblings('input');
    var label = $input.val();
    if (label.length != 0) {
        $input.val('');
        var html = '<span class="tag draggable"><span>' + label + 
            '<a class="tagsinput-remove-link"></a></span></span>';
        $("#catATags_tagsinput").append(html);
        setDraggable();
        setTagRemoval();
    }
});

$('#add_categoryB_label').click(function(event) {
    var $input = $(event.target).siblings('input');
    var label = $input.val();
    if (label.length != 0) {
        $input.val('');
        var html = '<span class="tag draggable"><span>' + label + 
            '<a class="tagsinput-remove-link"></a></span></span>';
        $("#catBTags_tagsinput").append(html);
        setDraggable();
        setTagRemoval();
    }
});

