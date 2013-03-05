$(function () {
    $('.nav-tabs a').click(function (e) {
      document.location.hash = $(this).attr('href');
      $(this).tab('show');
      return false;
    });

    if (document.location.hash === '') {
        var $first = $('.nav-tabs a:first');
        document.location.hash = $first.attr('href');
        $first.tab('show');
    } else {
        $('.nav-tabs a[href="'+window.location.hash+'"]').tab('show');
    }
});