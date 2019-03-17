base_ajax_url = '/ajax_urls/';
$.ajaxSetup({
    beforeSend: function (xhr, settings) {
        function getCookie(name) {
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                let cookies = document.cookie.split(';');
                for (let i = 0; i < cookies.length; i++) {
                    let cookie = jQuery.trim(cookies[i]);
                    // Does this cookie string begin with the name we want?
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }

        if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
            // Only send the token to relative URLs i.e. locally.
            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
        }
    }
});


// function getCookie(name) {
//     let cookieValue = null;
//     if (document.cookie && document.cookie !== '') {
//         let cookies = document.cookie.split(';');
//         for (let i = 0; i < cookies.length; i++) {
//             let cookie = jQuery.trim(cookies[i]);
//             // Does this cookie string begin with the name we want?
//             if (cookie.substring(0, name.length + 1) === (name + '=')) {
//                 cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
//                 break;
//             }
//         }
//     }
//     return cookieValue;
// }

$('.vote').on('click', function (e) {
    let elem = e.target;
    if (elem !== this) {
        elem = elem.parentNode;
    }
    let object = elem.getAttribute('data-object');
    let action = elem.getAttribute('data-action');
    let user_id = elem.getAttribute('data-user');
    let object_id = elem.getAttribute('data-id');
    let datastring = {'object': object, 'action': action, 'user_id': user_id, 'object_id': object_id};
    $.ajax({
            url: base_ajax_url + "vote/",
            type: 'POST',
            data: datastring,
            success: function (response) {
                $('#vote'+object_id).html(response);
            }
        }
    );
});
