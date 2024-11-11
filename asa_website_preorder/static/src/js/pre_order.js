/** @odoo-module **/
//This JavaScript function handles the cancellation of a sale order on the website.
//The function checking for there is a valid reason for cancelling the order
var publicWidget = require('web.public.widget');
var ajax = require('web.ajax');
publicWidget.registry.WebsitePreOrder = publicWidget.Widget.extend({
     selector: '.confirmorderform',
     events: {
            'click #confirm_preorder': '_onConfirm',
        },
        _onConfirm: function (e) {
            var sisaorder = this.$("#sisaorder").val();
            var partner =this.$("#partner").val();
            var product_id =this.$("#product_id").val();
            var qty_preorder =this.$("#qty_preorder").val();

            console.log("Testtttt oekekekekeekek=================",sisaorder, qty_preorder)

            if (qty_preorder > sisaorder ){
                    alert("Qty tidak boleh menlebihi Stock Pre Order");
                    e.preventDefault();
                }
            else{
              ajax.jsonRpc("/preorder/confirmation/submit", 'call', {
                   'partner': partner,
                   'product_id': product_id,
                   'qty_preorder': qty_preorder
              }).then(function() {
                 location.reload();
            });
            }
        }
    });
    var WebsitePreOrder = new publicWidget.registry.WebsitePreOrder(this);
    WebsitePreOrder.appendTo($(".confirmorderform"));
    return publicWidget.registry.WebsitePreOrder;
