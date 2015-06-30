var mu = '';
$(function()  {
    $('#save_changes').click(function() {
        if ($("#show_mu").is(":checked")) {
            mu = 'checked';
        }
        else {
            mu = 'unchecked';
        }
        $('#myModal2').modal('hide');
    });
});
$(function()  {
    $('#reset_changes').click(function() {
        $("#show_mu").prop('checked', false);
    });
});
$(function()  {
    $('#sign_in_button').click(function() {
        if ($('#inputLogin').val() == 'admin' && $('#inputPassword').val() == '123')
        {
            $('#myModal1').modal('hide');
            $('#myModal2').modal('show');
        }
        else {alert('Неверный логин или пароль!');}
    });
});
$(function()  {
    $('#reset_button').click(function() {
        $('input[id="dict_search"]').val('');
    });
});

function get_transliteration() {
    if (trans == undefined) {
        return 'ural'
    }
    $('#transliteration').click(function () {
        trans = $('#transliteration').val();
    });
    return trans
}

$(function()  {
    $('#button').click(function() {
        $.ajax({
            type: "GET",
            url: "/handler/",
            data: { word: ".*" },
            dataType: "json",
            success: function(data) {
                $("#button").html('');
                $("#lemmas").html(data.entries);
                showEntry();
            }
        });
    });
});


function showEntry() {
    $('a#lemma').click(function() {
        $.getJSON('/_get_entry', {
            lemma: $( this ).text(),
            trans: $('#transliteration').val()
        }, function(data) {
            $('html, body').css('position', 'relative');
            $("#entry").html(data.entryHtml);
            if (mu == 'unchecked') {
                $('#mu').hide();
            }
        });
        return false;
    });
}

$(document).ready(function () {
    if (window.location.href.indexOf("/hidden") > -1) {
        $('#corpus_trans').show();
        $('#transliteration').val('corpus')
    }
});

var lang;

$(document).ready(function () {
$("#lang").click(function () {
    if ($('#lang').val() == 'bes') {
        $('#transliteration').prop('disabled', false);
        lang = 'bes'
    }
    else {
        $('#transliteration').prop('disabled', 'disabled');
        lang = 'rus'
    }

});
});

$(function() {showEntry();});

$(function() {
    $("#submit_button").click(function(event) {
        $.ajax({
            type: "GET",
            url: "/handler/",
            data: { word: $('input[id="dict_search"]').val(), lang: lang, trans: $('#transliteration').val()},
            dataType: "json",
            success: function(data) {
                $("#button").html(data.divButton);
                $("#recently").html(data.recently);
                if (data.entryAmount == 1) {
                    $("#lemmas").html(data.entries);
                    $("#entry").html(data.entryHtml);
                    showEntry();
                }
                else {
                    $("#lemmas").html(data.entries);
                    showEntry();
                    //alert(data.entries);
                }
            }
        });
        event.preventDefault();
    });
});


$(function () {
    $('[data-toggle="popover"]').popover({
        html: true,
        content: $('#udm').html()
});
});

// Allow Bootstrap dropdown menus to have forms/checkboxes inside,
// and when clicking on a dropdown item, the menu doesn't disappear.
$(document).on('click', '.dropdown-menu.dropdown-menu-form', function(e) {
    e.stopPropagation();
});