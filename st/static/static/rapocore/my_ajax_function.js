function get_members_in_queue() {
    new Ajax.Request('/getmembersinqueue/', { 
    method: 'post',
    parameters: $H({'book':$('id_book').getValue()}),
    onSuccess: function(transport) {
        var e = $('id_to_member')
        if(transport.responseText)
            e.update(transport.responseText)
    }
    }); // end new Ajax.Request
}
