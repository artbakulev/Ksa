let input = $('#tags'),
    tags_overflow_field = $('#tags_overflow_field');
input.bind('input', function () {
    if ($(this).val()[$(this).val().length - 1] === ' ') {
        if ($(this).val().split(' ').length > 3) {
            tags_overflow_field.html('<span class="badge badge-danger badge-pill">Three tags max!</span>')
        } else {
            tags_overflow_field.html('');
        }
    }
});

