odoo.define('dashboard_member12.member_payment', function (require) {
    'use strict';

    var core = require('web.core');
    var publicWidget = require('web.public.widget');
    var _t = core._t;

    publicWidget.registry.OnlineAppointment = publicWidget.Widget.extend({
        selector: '#payment_per_year',
        init: function () {
            this._super.apply(this, arguments);
        },
        start: function () {
            var self = this;

            $("#payment_years").on('change', function() {
                self._update_payment();
            });

            self._update_payment();
        },

        _update_payment: function () {
            console.log("payment found in widget")
            console.log($("#payment_years").val())
            var self = this;
            this._rpc({
                route: '/yearly/payments',
                params: {
                    'year': $("#payment_years").val()
                },
            }).then(function(result) {
                var options = [];
                var payment_of_the_year_member = result.payments;
                console.log("PAYMENTS")
                console.log(result.payments)
                for (var i = 0; i < payment_of_the_year_member.length; i++) {
                    options.push('<td><span t-field="', payment_of_the_year_member[i].member_id, '"/></td>')
                    options.push('<td><span t-field="', payment_of_the_year_member[i].year, '"/></td>')
                    options.push('<td><span t-field="', payment_of_the_year_member[i].month, '"/></td>')
                    options.push('<td><span t-field="', payment_of_the_year_member[i].fee_amount, '"/></td>')
                    options.push('<td><span t-field="', payment_of_the_year_member[i].amount_remaining, '"/></td>')
                    options.push('<td><span t-field="', payment_of_the_year_member[i].amount_paid, '"/></td>')
                    options.push('<td><span t-field="', payment_of_the_year_member[i].traced_member_payment, '"/></td>')
                    options.push('<td><span t-field="', payment_of_the_year_member[i].id_payment, '"/></td>')
                    options.push('<td><span t-field="', payment_of_the_year_member[i].state, '"/></td>')

                }
                $("#payment_member_body").html(options.join(''));

                var options = [];
                var payment_of_the_year_league = result.league_payments;
                for (var i = 0; i < payment_of_the_year_league.length; i++) {
                    options.push('<td><span t-field="', payment_of_the_year_league[i].league_id, '"/></td>')
                    options.push('<td><span t-field="', payment_of_the_year_league[i].year, '"/></td>')
                    options.push('<td><span t-field="', payment_of_the_year_league[i].month, '"/></td>')
                    options.push('<td><span t-field="', payment_of_the_year_league[i].fee_amount, '"/></td>')
                    options.push('<td><span t-field="', payment_of_the_year_league[i].amount_remaining, '"/></td>')
                    options.push('<td><span t-field="', payment_of_the_year_league[i].amount_paid, '"/></td>')
                    options.push('<td><span t-field="', payment_of_the_year_league[i].traced_member_payment, '"/></td>')
                    options.push('<td><span t-field="', payment_of_the_year_league[i].id_payment, '"/></td>')
                    options.push('<td><span t-field="', payment_of_the_year_league[i].state, '"/></td>')

                }
                $("#payment_league_body").html(options.join(''));

            });
        },

    })
});
