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
            lemma: $( this ).text()
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
$(function() {
    $("#submit_button").click(function(event) {
        $.ajax({
            type: "GET",
            url: "/handler/",
            data: { word: $('input[id="dict_search"]').val() },
            dataType: "json",
            success: function(data) {
                $("#button").html(data.divButton);
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