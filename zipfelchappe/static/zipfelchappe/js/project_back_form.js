$(function () {
    var $expl = $('#paypal-expl');

    // disable unavailable rewards
    $('.unavailable').siblings('input').attr('disabled','disabled');

    $('input[name=reward]:radio').on('change', function(){
        // get minimal amount for choosen reward
        var minimum_amount = $(this).parent().find('.radio-text').data('minimum');
        if (minimum_amount) {
            minimum_amount = parseInt(minimum_amount, 10);  // chop off decimal places
        } else {
            minimum_amount = 0;
        }

        // get user intended donation amount or set it if undefined
        var intended_amount = $('#id_amount').val();
        if (!intended_amount || intended_amount <= 0 ) {
            intended_amount = 1;
            $('#id_amount').val(intended_amount);
        }

        // raise donation amount if the choosen reward requires a higher donation
        if (intended_amount < minimum_amount) {
            $('#id_amount').val(minimum_amount);
        }
    });

    // toggle the class on the explanation box
    $('input[name=provider]:radio').on('change', function(){
        $expl.find('p').addClass('hidden hide');
        $expl.find('.'+$(this).val()).removeClass('hidden hide');
    }).trigger('change');

});
