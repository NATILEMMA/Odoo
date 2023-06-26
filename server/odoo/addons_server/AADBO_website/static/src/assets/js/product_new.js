odoo.define('AADBO.product_new', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');
    const {_t, qweb} = require('web.core');

    publicWidget.registry.registrationDetails = publicWidget.Widget.extend({

        selector: '.registration_details',
        read_events: {
            'change select[name="subcity_id"]': '_subcityChange',
        },

         start: function () {
            var def = this._super.apply(this, arguments);
            this.$wereda = this.$('select[name="wereda_id"]');
            this.$weredaOptions = this.$wereda.filter(':enabled').find('option:not(:first)');
            this._weredaChange();
            return def;
         },

         _weredaChange: function() {
             var $subcity = this.$('select[name="subcity_id"]');
             var subcityID = ($subcity.val() || 0);
             this.$weredaOptions.detach();
             var $displayedState = this.$weredaOptions.filter('[data-parent_id=' + subcityID + ']');
             var nb = $displayedState.appendTo(this.$wereda).show().length;
             this.$wereda.parent().toggle(nb >= 1);
         },

         _subcityChange: function() {
             this._weredaChange();
         },
    });

    publicWidget.registry.registrationDetailsOnPortal = publicWidget.Widget.extend({

        selector: '.o_portal_details',
        read_events: {
            'change select[name="subcity_id"]': '_subcityChange',
        },

         start: function () {
            var def = this._super.apply(this, arguments);
            this.$wereda = this.$('select[name="wereda_id"]');
            this.$weredaOptions = this.$wereda.filter(':enabled').find('option:not(:first)');
            this._weredaChange();
            return def;
         },

         _weredaChange: function() {
             var $subcity = this.$('select[name="subcity_id"]');
             var subcityID = ($subcity.val() || 0);
             this.$weredaOptions.detach();
             var $displayedState = this.$weredaOptions.filter('[data-parent_id=' + subcityID + ']');
             var nb = $displayedState.appendTo(this.$wereda).show().length;
             this.$wereda.parent().toggle(nb >= 1);
         },

         _subcityChange: function() {
             this._weredaChange();
         },
    });

    publicWidget.registry.registrationLivelihoodDetails = publicWidget.Widget.extend({

        selector: '.registration_details',
        read_events: {
            'change select[name="livelihood"]': '_livelihoodChange',
        },

        start: function () {
            var def = this._super.apply(this, arguments);
            return def;
        },

         _companyChange: function() {
            var $livelihood = this.$('select[name="livelihood"]');
            var livelihoodValue = ($livelihood.val() || 0);
            var livelihood = document.getElementById('livelihood')
            var livelihood1 = document.getElementById('livelihood1')
            if (livelihoodValue === 'stay at home') {
                livelihood.style.display = 'none';
                livelihood1.style.display = 'none';
            } else if (livelihoodValue === 'governmental') {
                livelihood.style.display = 'block';
                livelihood1.style.display = 'block';
            } else if (livelihoodValue === 'private') {
                livelihood.style.display = 'block';
                livelihood1.style.display = 'block';
            } else if (livelihoodValue === 'individual') {
                livelihood.style.display = 'block';
                livelihood1.style.display = 'block';
            }
        },

         _livelihoodChange: function() {
             this._companyChange();
         },
    });


    publicWidget.registry.registrationfieldofStudyDetails = publicWidget.Widget.extend({

        selector: '.registration_details',
        read_events: {
            'change select[name="field_of_study_id"]': '_studyChange',
        },

        start: function () {
            var def = this._super.apply(this, arguments);
            return def;
        },

         _userChange: function() {
            var $study = this.$('select[name="field_of_study_id"]');
            var studyValue = ($study.val() || 0);
            console.log(studyValue)
            var user = document.getElementById('userinput')
            if (studyValue == 101) {
                console.log("Found")
                user.style.display = 'block';
            } else {
                console.log("Not Found")
                user.style.display = 'none';
            }
        },

         _studyChange: function() {
             this._userChange();
         },
    });
});