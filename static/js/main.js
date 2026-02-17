(function () {
  function getCookie(name) {
    var match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
    return match ? match[2] : null;
  }

  window.addToCart = function (productId, quantity) {
    quantity = quantity || 1;
    var body = JSON.stringify({ product_id: productId, quantity: quantity });
    var csrf = typeof csrfToken !== 'undefined' ? csrfToken : getCookie('csrftoken');
    var url = typeof addToCartUrl !== 'undefined' ? addToCartUrl : '/cart/add/';
    fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrf,
        'X-Requested-With': 'XMLHttpRequest'
      },
      body: body
    })
      .then(function (r) { return r.json(); })
      .then(function (data) {
        if (data.success) {
          var el = document.getElementById('cart-count');
          if (el) el.textContent = data.cart_total;
          alert(data.message);
        }
      })
      .catch(function (err) { console.error(err); });
  };

  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.qty-plus').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var wrap = this.closest('.qty-control');
        var input = wrap && wrap.querySelector('input[type="number"]');
        if (input) {
          var v = parseInt(input.value, 10) || 0;
          input.value = Math.min(99, v + 1);
        }
      });
    });
    document.querySelectorAll('.qty-minus').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var wrap = this.closest('.qty-control');
        var input = wrap && wrap.querySelector('input[type="number"]');
        if (input) {
          var v = parseInt(input.value, 10) || 1;
          input.value = Math.max(1, v - 1);
        }
      });
    });

    document.querySelectorAll('.add-to-cart-form').forEach(function (form) {
      form.addEventListener('submit', function (e) {
        var productId = form.querySelector('input[name="product_id"]');
        var quantity = form.querySelector('input[name="quantity"]');
        if (productId && quantity && typeof addToCartUrl !== 'undefined') {
          e.preventDefault();
          window.addToCart(parseInt(productId.value, 10), parseInt(quantity.value, 10) || 1);
        }
      });
    });
  });
})();
