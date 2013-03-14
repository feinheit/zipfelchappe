
$(function () {

    $('#mail_templates-group').delegate('.send_test', 'click', function (e) {
        e.preventDefault();
        var $button = $(this);
        var $fieldset = $(this).parents('fieldset');

        var project = parseInt(document.location.pathname.split('/')[4], 10);
        var action = $fieldset.find('select[id$="action"]').val();
        var subject = $fieldset.find('input[id$="subject"]').val();
        var template = $fieldset.find('textarea[id$="template"]').val();
        var recipient = $fieldset.find('input[type="email"]').val();

        // Try to get action from fk select on translation page
        if (action === undefined) {
            var selected = $fieldset.find('select[id$="translation_of"] option:selected');
            action = selected.text().split(' ')[0];
        }

        if (isNaN(project)) {
            alert('Please save project before testing mails');
            return;
        }

        if (action && subject && template && recipient) {
            $.ajax({
                type: 'POST',
                url: '../send_test_mail/',
                data: {
                    'project': project,
                    'action': action,
                    'subject': subject,
                    'template': template,
                    'recipient': recipient
                },
                dataType: "json",
                success: function(data) {
                    if(data.success) {
                        var val = $button.attr('value');
                        $button.attr('value', 'Mail sent successfully');
                        $button.attr('disabled', 'disabled');
                        setTimeout(function () {
                            $button.attr('value', val);
                            $button.removeAttr('disabled');
                        }, 3000);
                    } else {
                        alert('Mail was not sent successfully');
                    }
                }
            });
        } else {
            alert('Please fill out all fields before sending test mail');
            return;
        }
    });

});
