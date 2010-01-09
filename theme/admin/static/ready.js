// the purpose of this whole file is to run once the DOM is ready
// so all of this stuff is quite generic

$(function() {

    // stripe any tables and add a hover (which is IE compatible over td:hover)
    // From: http://15daysofjquery.com/examples/zebra/
    $('.striped tr:odd').addClass('odd');
    $('.striped tr:even').addClass('even');

    $('.striped tr')
        .mouseover( function() { $(this).addClass('hover'); } )
        .mouseout( function() { $(this).removeClass('hover'); } )
    ;

    $('.section-filter')
        .change( function() {
            var pathname = window.location.pathname;
            window.location = pathname + '?section=' + $(this).val();
        })
    ;

    // for tables which have a 'select-all' checkbox, make it select all the
    // 'keys' checkboxes from the table it is in
    $('.select-all')
        .click( function() {
            var checked = this.checked;
            // find all the '.keys' in the parent 'table'
            $(".keys", $(this).closest('table')).each(function() {
                this.checked = checked;
            });
        })
    ;
});
