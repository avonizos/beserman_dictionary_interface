// Show/hide verb's argument structure
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

// Login admin panel
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

// Reset search input form
$(function()  {
    $('#reset_button').click(function() {
        $('input[id="dict_search"]').val('');
    });
});

// Return all lemmas after clicking on the "Return all" button
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

// Get a particular entry for the lemma
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

$(function() {showEntry();});


// Hidden page for the corpus transliteration
$(document).ready(function () {
    if (window.location.href.indexOf("/hidden") > -1) {
        $('#corpus_trans').show();
        $('#transliteration').val('corpus')
    }
});

// Get the current direction
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

// Action after submit search query
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

// Show the keyboard
$(function () {
    $('[data-toggle="popover"]').popover({
        html: true,
        content: $('#udm').html()
    });
});

// Keyboard disappears when clicking anywhere
$(function () {
    $('body').click(function (e) {
        $('[data-toggle="popover"]').each(function () {
            //the 'is' for buttons that trigger popups
            //the 'has' for icons within a button that triggers a popup
            if (!$(this).is(e.target) && $(this).has(e.target).length === 0 && $('.popover').has(e.target).length === 0) {
                $(this).popover('hide');
            }
        });
    });
});
