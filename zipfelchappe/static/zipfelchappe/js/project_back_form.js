
(function(a){function d(b){var c=b||window.event,d=[].slice.call(arguments,1),e=0,f=true,g=0,h=0;b=a.event.fix(c);b.type="mousewheel";if(c.wheelDelta){e=c.wheelDelta/120}if(c.detail){e=-c.detail/3}h=e;if(c.axis!==undefined&&c.axis===c.HORIZONTAL_AXIS){h=0;g=-1*e}if(c.wheelDeltaY!==undefined){h=c.wheelDeltaY/120}if(c.wheelDeltaX!==undefined){g=-1*c.wheelDeltaX/120}d.unshift(b,e,g,h);return(a.event.dispatch||a.event.handle).apply(this,d)}var b=["DOMMouseScroll","mousewheel"];if(a.event.fixHooks){for(var c=b.length;c;){a.event.fixHooks[b[--c]]=a.event.mouseHooks}}a.event.special.mousewheel={setup:function(){if(this.addEventListener){for(var a=b.length;a;){this.addEventListener(b[--a],d,false)}}else{this.onmousewheel=d}},teardown:function(){if(this.removeEventListener){for(var a=b.length;a;){this.removeEventListener(b[--a],d,false)}}else{this.onmousewheel=null}}};a.fn.extend({mousewheel:function(a){return a?this.bind("mousewheel",a):this.trigger("mousewheel")},unmousewheel:function(a){return this.unbind("mousewheel",a)}})})(jQuery)

$(function () {
    $('input[name="reward"]').change(function () {
        var amount = $('#id_amount');
        var amount_val = parseInt(amount.val());
        var reward_text = $(this).parent().find('.radio_text:first');
        var reward_minimum = parseInt(reward_text.data('minimum'));

        if (reward_text.hasClass('unavailable')) { return; }

        if (!isNaN(reward_minimum) && (isNaN(amount_val) ||
                amount_val < reward_minimum)) {
            amount.val(reward_minimum);
        }
    });

    $("#id_amount").mousewheel( function(event, delta) {
        if (delta > 0) {
            this.value = parseInt(this.value) + 1;
        } else {
            if (parseInt(this.value) > 0) {
                this.value = parseInt(this.value) - 1;
            }
        }
        return false;
     });


    $('label .available').each(function (i, label) {
        $(this).parent().addClass('available');
    });

    $('label .unavailable').each(function () {
        $(this).parent().addClass('unavailable');
        $(this).parent().find('input').prop('disabled', true);
    });
});
