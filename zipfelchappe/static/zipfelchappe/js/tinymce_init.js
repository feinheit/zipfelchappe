
$(function () {
    tinyMCE.init({
        mode: "specific_textareas",
        editor_selector : "tinymce",
        theme: "advanced",
        language: "en",
        theme_advanced_toolbar_location: "top",
        theme_advanced_toolbar_align: "left",
        theme_advanced_statusbar_location: "bottom",
        theme_advanced_buttons1: "fullscreen,|,formatselect,|,bold,italic,|,sub,sup,|,bullist,numlist,|,anchor,link,unlink,|,code",
        theme_advanced_buttons2: "",
        theme_advanced_buttons3: "",
        theme_advanced_path: false,
        theme_advanced_blockformats: "p,h2,h3",
        theme_advanced_resizing: true,
        width: '680',
        height: '300',
        plugins: "fullscreen,paste",
        paste_auto_cleanup_on_paste: true,
        relative_urls: false
    });

    // Remove tinymce from empty forms
    setTimeout(function () {
        $('.tinymce[id*="__prefix__"]').each(function() {
            res = tinyMCE.execCommand('mceRemoveControl', true, this.id);
        });
    }, 200);

    // Add tinymce on newly added instances
    $(".add-row a").click(function () {
        $('.tinymce:not([id*="__prefix__"]):last').each(function() {
            tinyMCE.execCommand('mceRemoveControl', true, this.id);
            tinyMCE.execCommand('mceAddControl', true, this.id);
        });
    });
})
