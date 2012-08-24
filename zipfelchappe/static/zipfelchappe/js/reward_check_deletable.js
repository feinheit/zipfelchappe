
$(function() {
    $('#rewards-group .inline-related').each(function (i, e) {
        var reserved = $(this).find('.field-reserved');
        var delete_field = $(this).find('.delete');
        var reserved_val = reserved.find('p').text();

        reserved.hide();
        if(reserved_val > 0) {
            delete_field.text('Reserved ' + reserved_val + ' times');
        }
    });
});
