function validate_email(){
        var email = document.getElementById('email').value.trim()
        if (email == '')
            return;
        action_url = '/user/validate_email/'+ email
        $('#email').next('ul').remove();
        $.getJSON(action_url,
            function(data){
            if (data['status'] == 'True'){
              $('#email').after('<ul> <li class="form-error">'+data['message']+'</li> </ul>')
              $('#email').focus();
              return false;
            }
        });
}
  $('#phone').mask('(000) 000-0000');

  $('input').on('keyup',function(){
   $(this).attr('value', $(this).val());
  });

  function IsNumeric(e) {
        var e = event || evt; // for trans-browser compatibility
        var charCode = e.which || e.keyCode;
        if (charCode == 46)
            return true
        if (charCode > 31 && (charCode < 48 || charCode > 57)){
            return false;
        }

        return true;
    }