(function($){

    function add_inline_tab(name, fieldset) {
        var id_name = name.toLowerCase();
        var tab_id = id_name + '_tab';

        $('#main_wrapper .navi_tab:last').after(
            '<div class="navi_tab" id="'+tab_id+'">'+name+'</div>'
        );

        var body_id = id_name + '_body';
        $('#main').append('<div id="'+body_id+'" class="panel"></div>');

        var body_panel = $('#'+body_id);

        fieldset.find('h2').hide();

        body_panel.append(fieldset);

        var tab = $('#'+tab_id);
        tab.click(function() {
            var elem = $(this);
            $("#main_wrapper > .navi_tab").removeClass("tab_active");
            elem.addClass("tab_active");
            $("#main > div:visible, #main > fieldset:visible").hide();

            var tab_str = elem.attr("id").substr(0, elem.attr("id").length-4);
            $('#'+tab_str+'_body').show();
            ACTIVE_REGION = REGION_MAP.indexOf(tab_str);

            window.location.replace('#tab_'+tab_str);
        });
    }

    // This is stupid, should ask mk about another way
    setTimeout(function() {
        add_inline_tab('Rewards', $('#rewards-group'));
        add_inline_tab('Payments', $('#payment_set-group'));
    }, 10);

})(feincms.jQuery);
