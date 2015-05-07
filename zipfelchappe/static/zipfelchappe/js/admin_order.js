$(document).ready(function() {
    // Set this to the name of the column holding the position
    var pos_field = 'position';

    // Determine the column number of the position field
    var pos_col = null;
    var $resultList = $('#result_list');
    var $tbody = $resultList.find('tbody');
    var $thead = $resultList.find('thead');
    var cols = $('tr:first', $tbody).children();

    for (var i = 0; i < cols.length; i++) {
        var inputs = $(cols[i]).find('input[name*=' + pos_field + ']');

        if (inputs.length > 0) {
            // Found!
            pos_col = i;
            break;
        }
    }

    if (pos_col == null) {
        return;
    }

    // Some visual enhancements
    var header = $('tr', $thead).children()[pos_col];
    $(header).css('width', '1em');
    $(header).children('a').text('#');

    // Hide position field
    $('tr', $tbody).each(function(index) {
        var pos_td = $(this).children()[pos_col];
        var input = $(pos_td).children('input').first();
        //input.attr('type', 'hidden')
        input.hide();

        var label = $('<strong>' + input.attr('value') + '</strong>');
        $(pos_td).append(label);
    });

    // Determine sorted column and order
    var sorted = $('th.sorted', $thead);
    var sorted_col = $('th', $thead).index(sorted)
    var sort_order = sorted.hasClass('descending') ? 'desc' : 'asc';

    if (sorted_col != pos_col) {
        // Sorted column is not position column, bail out
        console.info("Sorted column is not %s, bailing out", pos_field);
        return;
    }

    $('tr', $tbody).css('cursor', 'move');

    // Make tbody > tr sortable
    $tbody.sortable({
        axis: 'y',
        items: 'tr',
        cursor: 'move',
        update: function(event, ui) {
            var items = $(this).find('tr').get(),
                input, pos_td, label;

            if (sort_order == 'desc') {
                // Reverse order
                items.reverse();
            }

            $(items).each(function(index) {
                pos_td = $(this).children()[pos_col];
                input = $(pos_td).children('input').first();
                label = $(pos_td).children('strong').first();

                input.attr('value', index+1);
                label.text(index+1);
            });

            // Update row classes
            $(this).find('tr').removeClass('row1').removeClass('row2');
            $(this).find('tr:even').addClass('row1');
            $(this).find('tr:odd').addClass('row2');
        }
    });
});
