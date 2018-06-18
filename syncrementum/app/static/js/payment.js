//account menu setting Javascript Start here
function valid_card_detail(){
    cr_type = $('#type').val();
    cr_type_name = $('#type option:selected').text();
    expiry_date = $('#expiry_date').val();
    var elems = expiry_date.split("/");
    result = (elems.length == 2);
    if (!result){
        alert('Not a valid format of date. Please use mm/yyyy format');
        return false;
    }
    switch(cr_type){
        case 'visa':
            var validate_card = /^(?:4[0-9]{12}(?:[0-9]{3})?)$/;
            break;
        case 'mastercard':
            var validate_card = /^(?:5[1-5][0-9]{14})$/;
            break;
        case 'amex':
            var validate_card = /^(?:3[47][0-9]{13})$/;
            break;
        case 'discover':
            var validate_card = /^(?:6(?:011|5[0-9][0-9])[0-9]{12})$/;
            break;
        case 'jcb':
            var validate_card = /^(?:(?:2131|1800|35\d{3})\d{11})$/;
            break;
        default:
            var validate_card = /^(?:4[0-9]{12}(?:[0-9]{3})?)$/;
            break;
    }
    cr_number = $('#card_number').val();

    if(cr_number.match(validate_card)){
        return true
    }else{
        alert("Not a valid "+cr_type_name+" card number!");
    }
    return false;
}

