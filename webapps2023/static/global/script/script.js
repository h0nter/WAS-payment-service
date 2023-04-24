let DOC_READY = false;

$(document).ready(function () {
    DOC_READY = true;
});

const notificationsOpen = function () {
    $('#notifications-bar').css("transform", "translate(0%, 0)")
    if (DOC_READY) document.body.style.overflow = 'hidden';
}

const notificationsClose = function (el) {
    $(el).parent().parent().css("transform", "translate(100%, 0)");
    if (DOC_READY) document.body.style.overflowY = 'auto';
}