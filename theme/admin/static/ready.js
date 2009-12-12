// the purpose of this whole file is to run once the DOM is ready
// so all of this stuff is quite generic

$(function() {

    // stripe any tables and add a hover (which is IE compatible over td:hover)
    // From: http://15daysofjquery.com/examples/zebra/
    $('.striped tr:odd').addClass('odd');
    $('.striped tr:even').addClass('even');

    $('.striped tr')
        .mouseover( function() { $(this).addClass('hover'); } )
        .mouseout( function() { $(this).removeClass('hover'); } );

});
