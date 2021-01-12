const MAX_POST_LENGTH = 1_000;
const MIN_POST_LENGTH = 12;
const MAX_MB = 3;
const MAX_FILE_SIZE = MAX_MB * 1024 * 1024;

function output_error_msg(msg){
    $('#feedback').html(msg);
}

function cancel_and_feedback(e, msg){
    e.preventDefault();
    output_error_msg(msg);
}

$('form').submit(function(e){

    const is_post = this.id === 'post_form';
    const is_reply = this.id === 'reply_form';
    
    if(is_post !== is_reply){
        let text = $('#form_text').val().replace(/\s/g, '');
        let files = $('#form_img').prop('files');

        if(is_post && (text === '' || files.length !== 1)){
            let msg = 'Posts require text and an image.'
            cancel_and_feedback(e, msg);
            return;
        }
        
        if(text.length < MIN_POST_LENGTH){
            let msg = 'Post text doesn\'t have enough quality. Add some substance.'
            cancel_and_feedback(e, msg);
            return;
        }
        
        if(text.length > MAX_POST_LENGTH){
            let msg = `Post require fewer than ${MAX_POST_LENGTH} characters.`
            cancel_and_feedback(e, msg);
            return;
        }
    }
    else{
        e.preventDefault();
        alert('Unknown form.');
    }

});

$('#form_img').change(function() {
    if(this.files[0].size > MAX_FILE_SIZE){
    msg = `File size must be less than ${MAX_FILE_SIZE / 1024 / 1024} MB.`
    this.value = null;
    output_error_msg(msg);
    };
});
