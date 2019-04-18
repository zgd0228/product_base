/**
 * Created by zgd on 2019/4/13.
 */
$('.title').click(function () {
        $(this).next('.body2').toggleClass('hide')
    });
    $('.img').click(function(){
        $('.user_info').slideDown(1000)
    });
    $('.state').click(function(){
        $(this).next().slideDown(1000)
    });