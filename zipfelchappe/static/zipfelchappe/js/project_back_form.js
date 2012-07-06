
$(function () {
    $('label[for^="id_reward"]').click(function () {
        var reward_text = $(this).find('.radio_text:first');
        var reward_minimum = parseInt(reward_text.data('minimum'));
        if (!isNaN(reward_minimum)) {
            $('#id_amount').val(reward_minimum);
        }
    });
});
