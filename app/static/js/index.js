const MAX_POST_LENGTH = 1_500;
const MIN_POST_LENGTH = 4;
const MAX_MB = 3;
const MAX_FILE_SIZE = MAX_MB * 1024 * 1024;

function output_error_msg(msg){
    $('#reply_form div[feedback]').html(msg);
}

function cancel_and_feedback(e, msg){
    e.preventDefault();
    output_error_msg(msg);
}

$('form').submit(function(e){

    const is_post = this.id === 'post_form';
    const is_reply = this.id === 'reply_form';
    const is_report = this.id === 'report_form';
    
    // if post or reply form
    if(is_post !== is_reply){
        let text = $("#reply_form [name='form_text']").val().replace(/\s/g, '');
        let files = $("#reply_form [name='form_img']").prop('files');

        alert(text.length)

        if(is_post && (text === '' || files.length !== 1)){
            let msg = 'Posts require text and an image.'
            cancel_and_feedback(e, msg);
            return;
        }
        
        if(text.length < MIN_POST_LENGTH){
            let msg = `Post too short. ${MIN_POST_LENGTH} characters is the min.`
            cancel_and_feedback(e, msg);
            return;
        }
        
        if(text.length > MAX_POST_LENGTH){
            let msg = `Post too long. ${MAX_POST_LENGTH} characters is the max.`
            cancel_and_feedback(e, msg);
            return;
        }
    }
    else if(is_report){
        let text = $("#report_form [name='form_text']").val().replace(/\s/g, '');
        if(text === ''){
            let msg = 'Enter a reason for reporting this post.'
            e.preventDefault();
            $('#report_form div[feedback]').html(msg);
            return;
        }
    }
    else{
        e.preventDefault();
        alert('Unknown form.');
    }

});

$('#form_img').change(function() {
    $('.postform #feedback').html('');

    if(this.files[0].size > MAX_FILE_SIZE){
        let msg = `File size must be less than ${MAX_FILE_SIZE / 1024 / 1024} MB.`
        $('.postform #feedback').html(msg);
        this.value = null;
    };
});
