
$(function() {
    var reserved, delete_field, reserved_val;
    $('#rewards-group').find('.inline-related').each(function (i, e) {
        reserved = $(this).find('.field-reserved');
        delete_field = $(this).find('.delete');
        reserved_val = reserved.find('p').text();

        reserved.hide();
        if(reserved_val > 0) {
            delete_field.text('Reserved ' + reserved_val + ' times');
        }
    });
});
