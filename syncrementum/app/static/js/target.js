//account menu setting Javascript Start here
$( document ).ready(function() {
    $('.account-target').on('change', function(){
        selected_val = $(this).val();
        switch(selected_val){
            case 'at':
                location = at_url
                break;
            case 'lt' :
                location = lt_url
                break;
            case 'ht' :
                location = ht_url
                break;
            default:
                location = at_url
                break;
        }
    });

    $('.filter-target').on('keyup', function(){
        input_val = $(this).val();
        target_func = $(this).attr('func');
        $.ajax({
            type: 'GET',
            url: '/targets/'+target_func+'?q='+input_val+addquid,
            contentType: 'application/json; charset=utf-8',
            dataType: 'json',
            success: function(res) {
                if(res.status == 'success'){
                    if(res.account != '')
                        $('.target-data').html(res.account);
                    else
                        $('.target-data').html('<h4 style="text-align:center;">No Record Found</h4>');
                }else{
                    //$('.insta-error').text(res.msg);
                    $('#loading_modal').remove();
                }
            }
        });
    });

    $('.send-message').on('click',function(){
        $('#insta_id').val($(this).attr('insta-id'));
        msg = $('#msg-content').val();
        username = $(this).find('h4').text()
        update_msg = msg.replace("{@username}", username);
        $('#msg-box').val(update_msg);
        $('#direct-message-modal').modal('show');
    });

});

function delete_target(del_id, type){
    $.ajax({
            type: 'GET',
            url: '/targets/delete_target?item='+del_id+'&type='+type+addquid,
            contentType: 'application/json; charset=utf-8',
            dataType: 'json',
            success: function(res) {
                if(res.status == 'success'){
                    location.reload();
                }else{
                    //$('.insta-error').text(res.msg);
                    $('#loading_modal').remove();
                }
            }
        });
}

function send_message(){
    post_data['insta_id'] = $('#insta_id').val();
    post_data['message'] = $('#msg-box').val();
    $('#msg-box').addClass('loader');
    $('.send-msg-btn').hide();
    $.ajax({
            type: 'POST',
            url: '/targets/send_message'+adduid,
            data: JSON.stringify(post_data),
            contentType: 'application/json; charset=utf-8',
            dataType: 'json',
            success: function(res) {
                $('#msg-box').removeClass('loader');
                $('.send-msg-btn').show();
                if(res.status == 'success'){
                    alert('Message has been sent');
                    $('#msg-box').val('')
                    $('#direct-message-modal').modal('hide');
                }else{
                    //$('.insta-error').text(res.msg);
                     alert('Message could not sent');
                    $('#loading_modal').remove();
                }
            }
        });
}

