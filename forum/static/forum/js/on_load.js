let up_vote_buttons = $('*[data-action="up-vote"]'),
    down_vote_buttons = $('*[data-action="down-vote"]');

function check_up_vote() {
    if (this.classList.contains('btn-light')) {
        this.classList.remove('btn-light');
        this.classList.add('btn-success');
        this.classList.add('disabled');
    }
}

function check_down_vote() {
    let parent = this.parentNode;
    let up_vote_button = parent.childNodes[1];
    if (up_vote_button.classList.contains('btn-success')) {
        up_vote_button.classList.remove('btn-success');
        up_vote_button.classList.remove('disabled');
        up_vote_button.classList.add('btn-light');
    }
}


up_vote_buttons.each(function () {
    $(this).on('click', check_up_vote)
});


down_vote_buttons.each(function () {
    $(this).on('click', check_down_vote)
});


