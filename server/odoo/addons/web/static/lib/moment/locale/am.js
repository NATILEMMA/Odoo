//! moment.js locale configuration
//! locale : English (Australia) [am_ET]
//! author : Jared Morse : https://github.com/jarcoal

;(function (global, factory) {
    typeof exports === 'object' && typeof module !== 'undefined'
        && typeof require === 'function' ? factory(require('../moment')) :
    typeof define === 'function' && define.amd ? define(['../moment'], factory) :
    factory(global.moment)
 }(this, (function (moment) { 'use strict';

 var symbolMap = {
    '1': '፩',
    '2': '፪',
    '3': '፫',
    '4': '፬',
    '5': '፭',
    '6': '፮',
    '7': '፯',
    '8': '፰',
    '9': '፱',
    '0': '0'
};
var numberMap = {
    '፩': '1',
    '፪': '2',
    '፫': '3',
    '፬': '4',
    '፭': '5',
    '፮': '6',
    '፯': '7',
    '፰': '8',
    '፱': '9',
    '0': '0'
};
var pluralForm = function (n) {
    return n === 0 ? 0 : n === 1 ? 1 : n === 2 ? 2 : n % 100 >= 3 && n % 100 <= 10 ? 3 : n % 100 >= 11 ? 4 : 5;
};

 
 var amET = moment.defineLocale('am_ET', {
     months : 'ጥር_የካቲት_መጋቢት_ሚያዝያ_ግንቦት_ሰኔ_ሐምሌ_ነሐሴ_ጳጉሜ_መስከረም_ጥቅምት_ኅዳር_ታህሣሥ'.split('_'),
     monthsShort : 'ጥር_የካቲት_መጋቢት_ሚያዝያ_ግንቦት_ሰኔ_ሐምሌ_ነሐሴ_መስከረም_ጥቅምት_ኅዳር_ታህሣሥ'.split('_'),
     weekdays : 'እሑድ_ሰኞ_ማክሰኞ_ረቡዕ_ሐሙስ_ዓርብ_ቅዳሜ'.split('_'),
     weekdaysShort : 'እሑድ_ሰኞ_ማክሰኞ_ረቡዕ_ሐሙስ_ዓርብ_ቅዳሜ'.split('_'),
     weekdaysMin : 'እሑ_ሰኞ_ማክ_ረቡ_ሐሙ_ዓር_ቅዳ'.split('_'),
     longDateFormat : {
         LT : 'h:mm A',
         LTS : 'h:mm:ss A',
         L : 'DD/MM/YYYY',
         LL : 'D MMMM YYYY',
         LLL : 'D MMMM YYYY h:mm A',
         LLLL : 'dddd, D MMMM YYYY h:mm A'
     },
     calendar : {
         sameDay : '[ዛሬ በ] LT',
         nextDay : '[ነገ በ] LT',
         nextWeek : 'dddd [በ] LT',
         lastDay : '[ትናንት በ] LT',
         lastWeek : '[የመጨረሻ] dddd [በ] LT',
         sameElse : 'L'
     },
     relativeTime : {
         future : 'in %s',
         past : '%s ago',
         s : 'a few seconds',
         m : 'a minute',
         mm : '%d minutes',
         h : 'an hour',
         hh : '%d hours',
         d : 'a day',
         dd : '%d days',
         M : 'a month',
         MM : '%d months',
         y : 'a year',
         yy : '%d years'
     },
     ordinalParse: /\d{1,2}(st|nd|rd|th)/,
     ordinal : function (number) {
         var b = number % 10,
             output = (~~(number % 100 / 10) === 1) ? 'th' :
             (b === 1) ? 'st' :
             (b === 2) ? 'nd' :
             (b === 3) ? 'rd' : 'th';
         return number + output;
     },
     week : {
         dow : 1, // Monday is the first day of the week.
         doy : 4  // The week that contains Jan 4th is the first week of the year.
     }
 });
 
 return amET;
 
 })));
 