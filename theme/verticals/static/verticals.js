$(function () {

    // there doesn't seem to be any space below the textarea on comment forms
    // in Firefox so add a few extra pixels underneath it
    if ( $.browser.mozilla ) {
        $('.form textarea').css('margin-bottom', '4px');
    }

});
