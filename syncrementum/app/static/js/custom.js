//account menu setting Javascript Start here
$( document ).ready(function() {
  $('.add .fa-bars').on("click", function(){
       $('.acccount-menu').toggle(600);
  });
  
  // Last Account Active list javascript
  $('.alg-rgt b').on("click", function(){
       $('.last-days').toggle(600);
  });
  
  // Last Account Active list javascript of tooltip
  
     $('[data-toggle="tooltip"]').tooltip({'placement': 'top'});  
  
});