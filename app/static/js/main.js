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

function makeOptGroup(key) {
    selectOptionsHTML += '<optgroup label="' + key + '">';
}

function makeOption(key) {
    selectOptionsHTML += '<option>' + key + '</option>';
}

var wordsList
function searchForKey(key, obj) {
    $.each(obj, function(term, val){
        if(key == term) {
            wordsList = val;
        } else if(!$.isArray(val)) {
            searchForKey(key, val);
        }
    });
}

function setDraggable() {
    $('.draggable').draggable({
        revert: "invalid",
        stack: ".draggable",
        helper: "clone",
        cursor: "move",
        appendTo: "parent"
    });
}

$(function() {
    $("#catATags_tagsinput").droppable({
      accept: "#catBTags_tagsinput > span",
      drop: function( event, ui ) {
        deleteSpan( ui.draggable, "#catBTags_tagsinput", "#catATags_tagsinput");
      }
    });

    $("#catBTags_tagsinput").droppable({
      accept: "#catATags_tagsinput > span",
      drop: function( event, ui ) {
        deleteSpan(ui.draggable, "#catATags_tagsinput", "#catBTags_tagsinput");
      }
    });
});

function deleteSpan($item, removeFrom, moveTo) {
    var $list = $(moveTo);
    $item.find(removeFrom).remove();
    $item.appendTo($list);
}

$("#categoryA_select").change(function() {
    key = $(this).val();
    searchForKey(key, data);
    var catA_HTML = '';
    for (var i in wordsList) {
        var word = wordsList[i].trim()
        catA_HTML += '<span class="tag draggable"><span>' + word + 
        '<a class="tagsinput-remove-link"></a></span></span>';
    }
    $('#catATags_tagsinput').html(catA_HTML);
    setDraggable();
    setTagRemoval();
});

$("#categoryB_select").change(function() {
    key = $(this).val();
    searchForKey(key, data);
    var catB_HTML = '';
    for (var i in wordsList) {
        var word = wordsList[i].trim()
        catB_HTML += '<span class="tag draggable"><span>' + word + 
        '<a class="tagsinput-remove-link"></a></span></span>';
    }
    $('#catBTags_tagsinput').html(catB_HTML);
    setDraggable();
    setTagRemoval();
});

function setTagRemoval() {
    $('.tagsinput-remove-link').click(function(event) {
        $(event.target).closest('span[class^="tag"]').remove();
    });
}

$('#add_categoryA_label').click(function(event) {
    var $input = $(event.target).siblings('input');
    var label = $input.val();
    $input.val('');
    var html = '<span class="tag draggable"><span>' + label + 
        '<a class="tagsinput-remove-link"></a></span></span>';
    $("#catATags_tagsinput").append(html);
    setTagRemoval();
});

$('#add_categoryB_label').click(function(event) {
    var $input = $(event.target).siblings('input');
    var label = $input.val();
    $input.val('');
    var html = '<span class="tag draggable"><span>' + label + 
        '<a class="tagsinput-remove-link"></a></span></span>';
    $("#catBTags_tagsinput").append(html);
    setTagRemoval();
});

