
$(function () {
    $('label[for^="id_reward"]').click(function () {
        var reward_text = $(this).find('.radio_text:first');
        if (reward_text.hasClass('unavailable')) {
            return;
        } else {
            var reward_minimum = parseInt(reward_text.data('minimum'));
            if (!isNaN(reward_minimum)) {
                $('#id_amount').val(reward_minimum);
            }
        }
    });

    $('label .available').each(function (i, label) {
        $(this).parent().addClass('available');
    });

    $('label .unavailable').each(function () {
        $(this).parent().addClass('unavailable');
        $(this).parent().find('input').prop('disabled', true);
    });

    $('form').submit(function () {
        startLoading();
        return true;
    });

});
