let autocomplete;

function initAutoComplete(){
autocomplete = new google.maps.places.Autocomplete(
    document.getElementById('id_address'),
    {
        types: ['geocode', 'establishment'],
        //default in this app is "IN" - add your country code
        componentRestrictions: {'country': ['in']},
    })
// function to specify what should happen when the prediction is clicked
autocomplete.addListener('place_changed', onPlaceChanged);
}

function onPlaceChanged (){
    var place = autocomplete.getPlace();

    // User did not select the prediction. Reset the input field or alert()
    if (!place.geometry){
        document.getElementById('id_address').placeholder = "Start typing...";
    }
    else{
        // console.log('place name=>', place.name)
    }
    
    // get the address components and assign them to the fields
    var geocoder = new google.maps.Geocoder()
    var address = document.getElementById('id_address').value
    geocoder.geocode({'address': address}, function(results, status){
        if(status == google.maps.GeocoderStatus.OK){
            var latitude = results[0].geometry.location.lat()
            var longitude = results[0].geometry.location.lng()
            $('#id_latitude').val(latitude)
            $('#id_longitude').val(longitude)
            $('#id_address').val(address)
        }
    })

    for(i=0; i<place.address_components.length; i++){
        for(j=0; j<place.address_components[i].types.length; j++){
            
            if(place.address_components[i].types[j] == 'country'){
                $('#id_country').val(place.address_components[i].long_name)
            }
            if(place.address_components[i].types[j] == 'administrative_area_level_1'){
                $('#id_state').val(place.address_components[i].long_name)
            }
            if(place.address_components[i].types[j] == 'locality'){
                $('#id_city').val(place.address_components[i].long_name)
            }
            if(place.address_components[i].types[j] == 'postal_code'){
                $('#id_pin_code').val(place.address_components[i].long_name)
            }
        }
    }    
}


$(document).ready(function(){
    $('.add_to_cart').on('click', function(e){
        e.preventDefault()
        food_id = $(this).attr('data-id')
        url = $(this).attr('data-url')

        data = {'food_id': food_id}

        $.ajax({
            type: 'GET',
            url: url,
            data: data,
            success: function(response){
                if(response.status == 'login_required'){
                    swal(response.message, '', 'info').then(function(){
                        window.location = '/login'
                    });
                }else if( response.status == 'Failed'){
                    swal(response.message, '', 'error')
                }else if(response.status=='Success'){
                    $('#cart_counter').html(response.cart_counter['cart_count'])
                    $('#qty-'+food_id).html(response.qty)

                    // subtotal, tax and grand_total
                    applyCartAmount(
                        response.cart_amount['subtotal'], 
                        response.cart_amount['tax_dict'], 
                        response.cart_amount['grand_total']
                    )

                }
            }
        })
    })

    $('.decrease_cart').on('click', function(e){
        e.preventDefault()
        food_id = $(this).attr('data-id')
        url = $(this).attr('data-url')
        cart_id = $(this).attr('data-cart-id')
        data = {'food_id': food_id}

        $.ajax({
            type: 'GET',
            url: url,
            data: data,
            success: function(response){
                if(response.status == 'login_required'){
                    swal(response.message, '', 'info').then(function(){
                        window.location = '/login'
                    });
                }else if( response.status == 'Failed'){
                    swal(response.message, '', 'error')
                }else if(response.status=='Success'){
                    $('#cart_counter').html(response.cart_counter['cart_count'])
                    $('#qty-'+food_id).html(response.qty)
                    applyCartAmount(
                        response.cart_amount['subtotal'], 
                        response.cart_amount['tax_dict'], 
                        response.cart_amount['grand_total']
                        )
                    if(window.location.pathname == '/market-place/food/cart/'){
                        removeCartItem(response.qty,cart_id)
                        checkEmptyCart()
                    }
                }
            }
        })
    })


    $('.item-qty').each(function(){
        var the_id = $(this).attr('id')
        var qty = $(this).attr('data-qty')
        $('#' + the_id).html(qty)
    })

    // delete cart item

    $('.delete_cart').on('click', function(e){
        e.preventDefault()
        cart_id = $(this).attr('data-id')
        url = $(this).attr('data-url')
        $.ajax({
            type: 'GET',
            url: url,
            success: function(response){
                if( response.status == 'Failed'){
                    swal(response.message, '', 'error')
                }else if(response.status=='Success'){
                    $('#cart_counter').html(response.cart_counter['cart_count'])
                    applyCartAmount(
                        response.cart_amount['subtotal'], 
                        response.cart_amount['tax_dict'], 
                        response.cart_amount['grand_total']
                        )
                    removeCartItem(0, cart_id)
                    checkEmptyCart()
                }
            }
        })
    })

    // delete the cart element if the qty is zero
    function removeCartItem(quantity, cart_id){
        if(quantity <= 0){
            document.getElementById("cart-item-"+cart_id).remove()
        }
    }

    function checkEmptyCart(){
        var cart_counter = document.getElementById("cart_counter")
        if(cart_counter.innerHTML == '0'){
            document.getElementById('empty-cart').style.display = "block"
        }
    }

    // appy cart amount
    function applyCartAmount(subtotal, tax_dict, grand_total){
        if(window.location.pathname == '/market-place/food/cart/'){
            $('#subtotal').html(subtotal)
            $('#total').html(grand_total)
            
            for(tax_type in tax_dict){
                for(percentage in tax_dict[tax_type]){
                    tax_amount = tax_dict[tax_type][percentage]
                    $(`#tax-${tax_type}`).html(tax_amount)
                }
            }
        }   
    }

    // add opeming hour
    $('.add_hours').on('click', function(e){
        e.preventDefault()
        var day = document.getElementById('id_day').value
        var from_hour = document.getElementById('id_from_hour').value
        var to_hour = document.getElementById('id_to_hour').value
        var is_closed = document.getElementById('id_is_closed').checked
        var csrf_token = $('input[name=csrfmiddlewaretoken]').val()
        var url = $(this).attr('data-url')
        data = {
            'day': day, 'from_hour': from_hour, 'to_hour': to_hour, 'is_closed': is_closed, 'csrfmiddlewaretoken': csrf_token,
        }
        if(is_closed){
            is_closed = 'True',
            condition = "day != ''"
        }else{
            is_closed = 'False',
            condition = "day != '' && from_hour != '' && to_hour != ''"
        }

        if(eval(condition)){
            $.ajax({
                type: 'POST',
                url : url,
                data : data,
                success: function(response){
                    
                    if(response.status == 'success'){
                        url = url.replace('/add',  '/remove/' + response.id)
                        if(response.is_closed == 'Closed'){
                            html = `<tr id="hour-${response.id}"><td><b>${response.day}</b></td><td>Closed</td><td><a href=${url} data-url=${url}>Remove</a></td></tr>`
                        }else{
                            html = `<tr id="hour-${response.id}"><td><b>${response.day}</b></td><td>${response.from_hour} - ${response.to_hour } </td><td><a href=${url} class="remove_hours" data-url=${url}>Remove</a></td></tr>`
                        }
                        $(".opening_hours").append(html)
                        document.getElementById('opening_hours').reset()
                    }else{
                        swal(response.message, '', 'error')
                    }
                }
            })
        }else{
            swal('Please fill all the fields','', 'info')
        }
    })

    // remove opeming hour
    $(document).on('click', '.remove_hours', function(e){
        e.preventDefault()  
        var url = $(this).attr('data-url')
        $.ajax({
            type: 'GET',
            url: url,
            success: function(response){
                if(response.status == 'success'){
                    document.getElementById("hour-"+response.id).remove()

                }
            }
        })
    })
})


