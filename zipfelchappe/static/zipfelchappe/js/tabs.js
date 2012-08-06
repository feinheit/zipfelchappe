$(function () {
    $('.nav-tabs a').click(function (e) {
      window.location.hash = $(this).attr('href');
      $(this).tab('show');
    })

    if (window.location.hash === '') {
        $('.nav-tabs a:first').tab('show');
    } else {
        $('.nav-tabs a[href="'+window.location.hash+'"]').tab('show');
    }
});
