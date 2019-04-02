let vote_elements = $("[data-action$='vote']");
vote_elements.each(function () {
    $(this).attr('disabled', true);
});
