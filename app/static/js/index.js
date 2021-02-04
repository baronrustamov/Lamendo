const MAX_POST_LENGTH = 1_500;
const MIN_POST_LENGTH = 4;
const MAX_MB = 3;
const MAX_FILE_SIZE = MAX_MB * 1024 * 1024;

function validate(e, text_field, img_field, feedback_field, post=false, reply=false, report=false){
    if(!post && !reply && !report){
        e.preventDefault();
        alert('Unknown form recieved.');
    }
    
    let text = $(text_field).val().replace(/\s/g, '');
    let files = $(img_field).prop('files');
    let feedback = $(feedback_field);

    let msg = undefined;

    if(post){
        if(files.length !== 1){
            msg = 'Image needed.'
        }
    }

    if(post || reply){
        if(text.length < MIN_POST_LENGTH){
            msg = `Min character count (${MIN_POST_LENGTH}).`
        }
        
        if(text.length > MAX_POST_LENGTH){
            msg = `Max character count (${MAX_POST_LENGTH}).`
        }
    }

    if(report){
        if(text === ''){
            msg = 'Why do you want to report this?'
        }
    }

    if(msg !== undefined){
        e.preventDefault();
        feedback.html(msg);
    }
}

$('#reply_form').submit(function(e){
    let text_field = "#reply_form [name='form_text']";
    let img_field = "#reply_form [name='form_img']";
    let feedback_field = "#feedback_reply";
    validate(e, text_field, img_field, feedback_field, false, true, false);
});

$('#post_form').submit(function(e){
    let text_field = "#post_form [name='form_text']";
    let img_field = "#post_form [name='form_img']";
    let feedback_field = "#feedback_post";
    validate(e, text_field, img_field, feedback_field, true, false, false);
});

$('#report_form').submit(function(e){
    let text_field = "#report_form [name='form_text']";
    let img_field = undefined;
    let feedback_field = "#feedback_report";
    validate(e, text_field, img_field, feedback_field, false, false, true);
});

function validate_img_size(feedback_field, this_obj){
    $(feedback_field).html('');
    if(this_obj.files[0].size > MAX_FILE_SIZE){
        let msg = `File size must be less than ${MAX_FILE_SIZE / 1024 / 1024} MB.`
        $(feedback_field).html(msg);
        this_obj.value = null;
    };
}

$('#form_img_post').change(function() {
    let feedback_field = '#feedback_post';
    validate_img_size(feedback_field, this);
});

$('#form_img_reply').change(function() {
    let feedback_field = "#feedback_reply";
    validate_img_size(feedback_field, this);
});
