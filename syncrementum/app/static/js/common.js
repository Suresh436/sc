//account menu setting Javascript Start here
$( document ).ready(function() {
$('#expiry_date').mask("00/0000", {placeholder: "MM/YYYY"});

get_count = 0;
target_user = []
var search_target_users = new autoComplete({
        selector: '#search-target-users',
        minChars: 3,
        cache: 0,
        source: function(term, suggest){
          $.getJSON(search_user_url, { q: term }, function(data){
               $('.search-target-input').removeClass('loader');
              term = term.toLowerCase();
              if(data.status == 'error'){
                location = exists_url
              }
              var choices = data.list
              var suggestions = [];
              for (i=0;i<choices.length;i++)
                  suggestions.push(choices[i])
              suggest(suggestions);
          });
        },
        renderItem: function (item, search){
            search = search.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&amp;');
            var re = new RegExp("(" + search.split(' ').join('|') + ")", "gi");
            return '<div class="autocomplete-suggestion" insta_id="'+item.pk+'" user_name="'+item.username+
                      '" profile_image="'+item.profile_pic+'"> '
                    +item.username+'</div>';
        },
        onSelect: function(e, term, item){

            if(get_count >= 4)
                var added=false;
                $.map(target_user, function(elementOfArray, indexInArray) {
                if (elementOfArray.insta_id == item.getAttribute('insta_id')) {
                   added = true;
                 }
                });
                if (!added) {
                    target_user[get_count] = {}
                    target_user[get_count]['insta_id'] =item.getAttribute('insta_id')
                    target_user[get_count]['username'] =item.getAttribute('user_name')
                    target_user[get_count]['profile_image'] =item.getAttribute('profile_image')
                    var get_page = $('.search-target-input').attr('get_page');
                    if(get_page == 'dashboard'){
                         html = '<li>\
                        <a href="javascript:void(0);" onclick="return confirm(\'Are you sure to delete?\')?delete_acc( \'target_user\', this):false;" class="closeAcc">x</a> \
                         <div><img src="'+item.getAttribute('profile_image')+'"></div>\
                         <p>'+item.getAttribute("user_name")+'</p>\
                         </li>';
                         $('.user-insta-profiles > li:last').after(html)
                         $('.user-insta-profiles > li:first').css('display','none');
                         if(target_user.length >= 4){
                            $('#search-target-users').attr('disabled','disabled');
                        }
                    }else{
                        html = '<div class="col-lg-3 col-md-4 col-sm-6 col-xs-12">\
                        <ul class="account-user"> \
                        <li><img src="'+item.getAttribute('profile_image')+'"></l1>\
                         <li><h4>'+item.getAttribute("user_name")+'</h4></l1> \
                         <li onclick="return confirm(\'Are you sure to delete?\')?delete_acc( \'target_user\', this):false;"><i class="fa fa-times"></i></li>\
                         </ul></div>';
                        $('.insta-profiles > div:last').after(html)
                        if(target_user.length >= 10){
                            $('#search-target-users').attr('disabled','disabled');
                        }
                    }

                    get_count++;
                }
        }
    });
get_loc_count = 0;
target_loc = []
var search_target_locations = new autoComplete({
        selector: '#search-target-location',
        minChars: 3,
        cache: 0,
        source: function(term, suggest){
          $.getJSON(search_location_url, { q: term }, function(data){
            $('.search-target-input').removeClass('loader');
              term = term.toLowerCase();
              if(data.status == 'error'){
                location = exists_url
              }
              var choices = data.list
              var suggestions = [];
              for (i=0;i<choices.length;i++)
                  suggestions.push(choices[i])
              suggest(suggestions);
          });
        },
        renderItem: function (item, search){
            search = search.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&amp;');
            var re = new RegExp("(" + search.split(' ').join('|') + ")", "gi");
            return '<div class="autocomplete-suggestion" insta_loc_id="'+item.pk+'" loc_name="'+item.location_name+
                      '" profile_image="'+item.profile_pic+'"> '
                    +item.location_name+'</div>';
        },
        onSelect: function(e, term, item){

            if(get_loc_count >= 4)
                var added=false;
                $.map(target_loc, function(elementOfArray, indexInArray) {
                if (elementOfArray.insta_id == item.getAttribute('insta_loc_id')) {
                   added = true;
                 }
                });
                if (!added) {
                    target_loc[get_loc_count] = {}
                    target_loc[get_loc_count]['insta_id'] =item.getAttribute('insta_loc_id')
                    target_loc[get_loc_count]['username'] =item.getAttribute('loc_name')
                    var get_page = $('.search-target-input').attr('get_page');
                    if(get_page == 'dashboard'){
                        html = '<li>\
                        <a href="javascript:void(0);" onclick="return confirm(\'Are you sure to delete?\')?delete_acc( \'target_loc\', this):false;" class="closeAcc">x</a> \
                         <div><img src="/static/images/location.jpg"></div>\
                         <p>'+item.getAttribute("loc_name")+'</p>\
                         </li>';
                         $('.loc-insta-profiles > li:last').after(html)
                         $('.loc-insta-profiles > li:first').css('display','none');
                        //$('.location_'+get_loc_count).text(item.getAttribute('loc_name'));
                        if(target_loc.length >= 4){
                            $('#search-target-location').attr('disabled','disabled');
                        }
                    }else{

                        html = '<div class="col-lg-3 col-md-4 col-sm-6 col-xs-12">\
                        <ul class="account-user"> \
                        <li><img src="/static/images/location.jpg"></l1>\
                         <li><h4>'+item.getAttribute("loc_name")+'</h4></l1> \
                         <li onclick="return confirm(\'Are you sure to delete?\')?delete_acc( \'target_loc\', this):false;"><i class="fa fa-times"></i></li>\
                         </ul></div>';
                        $('.insta-profiles > div:last').after(html)
                        if(target_loc.length >= 10){
                            $('#search-target-location').attr('disabled','disabled');
                        }


                        //$('.location_'+get_loc_count).text(item.getAttribute('loc_name'));
                    }
                    get_loc_count++;
                }
        }
    });

$(document).on('keyup', '.search-target-input',function(){
    if($(this).val().length >= 3)
    $(this).addClass('loader');
});
get_hash_count = 0;
target_hash = []
var search_target_hash = new autoComplete({
        selector: '#search-target-hash',
        minChars: 3,
        cache: 0,
        source: function(term, suggest){
        var $this = $(this);
        var $element = $(this.element);
        //var previous_request = $('#search-target-hash').data( "jqXHR" );


        alert('dfgdfg');
        if( typeof previous_request !== 'undefined' ) {
        console.log(previous_request);
        alert('ddddd');
            // a previous request has been made.
            // though we don't know if it's concluded
            // we can try and kill it in case it hasn't
            previous_request.abort();
        }
        previous_request =  $.getJSON(search_hashtag_url, { q: term }, function
        (data){
              $('.search-target-input').removeClass('loader');
              term = term.toLowerCase();
              if(data.status == 'error'){
                location = exists_url
              }
              var choices = data.list
              var suggestions = [];
              for (i=0;i<choices.length;i++)
                  suggestions.push(choices[i])
              suggest(suggestions);
          });
        },
        renderItem: function (item, search){

            search = search.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&amp;');
            var re = new RegExp("(" + search.split(' ').join('|') + ")", "gi");
            return '<div class="autocomplete-suggestion" insta_hash_id="'+item.pk+'" hash_name="'+item.hash_name+
                      '" hash_profile_image="'+item.profile_pic+'"> '
                    +item.hash_name+'</div>';
        },
        onSelect: function(e, term, item){


                var added=false;
                $.map(target_hash, function(elementOfArray, indexInArray) {

                if (elementOfArray.insta_id == item.getAttribute('insta_hash_id')) {
                   added = true;
                 }
                });
                if (!added) {
                    target_hash[get_hash_count] = {}
                    target_hash[get_hash_count]['insta_id'] =item.getAttribute('insta_hash_id')
                    target_hash[get_hash_count]['username'] =item.getAttribute('hash_name')

                    var get_page = $('.search-target-input').attr('get_page');
                    if(get_page == 'dashboard'){
                        html = '<li>\
                        <a href="javascript:void(0);" onclick="return confirm(\'Are you sure to delete?\')?delete_acc( \'target_hash\', this):false;" class="closeAcc">x</a> \
                         <div><img src="/static/images/hashtag.jpg"></div>\
                         <p>'+item.getAttribute("hash_name")+'</p>\
                         </li>';
                         $('.has-insta-profiles > li:last').after(html)
                         $('.has-insta-profiles > li:first').css('display','none');
                        if(target_hash.length >= 4){
                            $('#search-target-hash').attr('disabled','disabled');
                        }

                    }else{

                        html = '<div class="col-lg-3 col-md-4 col-sm-6 col-xs-12">\
                        <ul class="account-user"> \
                        <li><img src="/static/images/hashtag.jpg"></l1>\
                         <li><h4>'+item.getAttribute("hash_name")+'</h4></l1> \
                         <li onclick="return confirm(\'Are you sure to delete?\')?delete_acc( \'target_hash\', this):false;"><i class="fa fa-times"></i></li>\
                         </ul></div>';
                        $('.insta-profiles > div:last').after(html)

                        if(target_hash.length >= 10){
                            $('#search-target-hash').attr('disabled','disabled');
                        }

                    }
                    get_hash_count++;
                }
        }
    });
  
});
post_data = {}
function launch_target(){
    var get_page = $('.search-target-input').attr('get_page');
    switch(get_page){
        case 'profile_target':
            if(target_user.length < 1){
                alert('Please select at least one profile target account');
                return false;
            }
            break;
        case 'location_target':
            if(target_loc.length < 1){
                alert('Please select at least one location target account');
                return false;
            }
            break;
        case 'hash_target':
            if(target_hash.length < 1){
                alert('Please select at least one hashtag target account');
                return false;
            }
            break;

        default:
            if(target_user.length < 1){
                alert('Please select at least one target account');
                return false;
            }
            break;
    }

    post_data['target_user'] = target_user;
    post_data['target_loc'] = target_loc;
    post_data['target_hash'] = target_hash;
    $.ajax({
        type: 'POST',
        url: launch_target_url,
        data: JSON.stringify(post_data),
        contentType: 'application/json; charset=utf-8',
        dataType: 'json',
        success: function(res) {
            if(res.status == 'success'){

                if(get_page == 'dashboard'){
                    location = dashboard_url;
                }else{
                    location = '/targets/'+get_page+adduid;
                }

            }else{
                $('#loading_modal').remove();
            }
        }
    });


}


function delete_acc(type, elem){
    jelem = jQuery(elem);
    var get_page = $('.search-target-input').attr('get_page');

    if(get_page == 'dashboard'){
        jelem.parent('li').remove();
        get_index = jelem.parent('li').index() - 1;
        max_limit = 4;
    }else{
        jelem.parent('.account-user').parent('div').remove();
        get_index = jelem.parent('.account-user').parent('div').index() - 1;
        max_limit = 10;
    }


    switch(type){
        case 'target_hash':
            target_hash.splice(get_index, 1);
            get_hash_count--;
            if(target_hash.length < max_limit){
                $('#search-target-hash').removeAttr('disabled');
            }
            if(target_hash.length == 0 && get_page == 'dashboard'){
                $('.has-insta-profiles > li:first').css('display','block');
            }
            break;

        case 'target_loc':
            target_loc.splice(get_index, 1);
            get_loc_count--;
            if(target_loc.length < max_limit){
                $('#search-target-location').removeAttr('disabled');
            }
            if(target_loc.length == 0 && get_page == 'dashboard'){
                $('.loc-insta-profiles > li:first').css('display','block');
            }
            break;

        case 'target_user':
            target_user.splice(get_index, 1);
            get_count--;
            if(target_user.length < max_limit){
                $('#search-target-users').removeAttr('disabled');
            }
            if(target_user.length == 0 && get_page == 'dashboard'){
                $('.user-insta-profiles > li:first').css('display','block');
            }
            break;
        default:
            break;

    }



}
