import { MONTHSGREGDAYS, MONTHSGREG, MONTHSETH, MONTHSGREGSHORT, MONTHSETHSHORT } from "./CalanderConstants";
import CalendarConverter from "./CalendarConverter";

/* return the number of days for Gregorian months */
export const getGregMonthDaysCount = (month, year) => {
    if (month !== 1) {
        return MONTHSGREGDAYS[month];
    } else {
        return ((year % 4 === 0 && year % 100 !== 0) || year % 400 === 0) ? 29 : 28;
    }
}

/* return the number of days for Ethiopic months */
export const getEthMonthDaysCount = (month, year) => {
    if (month !== 12) {
        return 30; // all months except the 13th month has 30 days
    } else {
        return ((year + 1) % 4 === 0) ? 6 : 5; //13th month has 5/6 days depending on the leap year      
    }
}


export const getMonthName = (isGregorian, month) => {

    return isGregorian ? MONTHSGREG[month] : MONTHSETH[month]
}

export const getShortMonthName = (isGregorian, month) => {
    return isGregorian ? MONTHSGREGSHORT[month] : MONTHSETHSHORT[month]
}
// get the index of the week day for a given Gregorian Date
export const getGregDateWeekDay = (year, month, day) => {
    const gregDate = new Date(year, month, day);
    gregDate.setFullYear(year)
    const weekDay = gregDate.getDay()
    return weekDay;
}

/* Get the month days for Gregorian month and year */

export const getMonthDaysGreg = (month, year) => {
    const firstDayOfMonth = new Date(year, month, 1).getDay()
    let currentDay = 0 - firstDayOfMonth
    let weekDay;
    const monthDays = new Array(6).fill([]).map(() => {
        weekDay = 0
        return new Array(7).fill(null).map(() => {
            currentDay++
            return {
                day: new Date(year, month, currentDay).getDate(),
                dayMonth: new Date(year, month, currentDay).getMonth(),
                dayYear: new Date(year, month, currentDay).getFullYear(),
                dayIndex: currentDay,
                weekDay: weekDay++
            }
        })
    })
    return monthDays
}


/* Get the month days for Ethiopian month and year */

export const getMonthDaysEthiopic = (month, year) => {

    let pagumeDays; //get the number of days for 13th month of the year
    if (month !== 0) {
        pagumeDays = getEthMonthDaysCount(12, year); // takes the same year as the specified month
    } else {
        pagumeDays = getEthMonthDaysCount(12, year - 1); // takes the previous year of the specified month
    }
    const extraDays = 30 + pagumeDays;
    // get the week day for the first day of a given month and year
    const calendarConverter = new CalendarConverter();
    const firstDayOfMonth = calendarConverter.getETMonthStartDay(year, month + 1);
    let currentDay = 0 - firstDayOfMonth;
    let weekDay;

    // generate two dimensional array containing 6 rows
    // each row contains a date referring to the current, previous or next month

    const monthDays = new Array(6).fill([]).map(() => {
        weekDay = 0; // the week day (Ehud, Segno,...) for a given date of the month                           
        return new Array(7).fill(null).map(() => {
            currentDay++;
            if (month === 0) {
                // display days of the previous month for Meskerem
                if (currentDay < 1) {
                    let prevDays = pagumeDays + currentDay
                    // display days of the 13th month (Pagume)
                    if (prevDays > 0) {
                        return { day: prevDays, dayMonth: 12, dayYear: year - 1, dayIndex: currentDay, weekDay: weekDay++ };
                    }
                    // display days of the 12th month (Nehase)
                    return { day: 30 - prevDays, dayMonth: 11, dayYear: year - 1, dayIndex: currentDay, weekDay: weekDay++ };
                }
                // display days of the next month 
                if (currentDay > 30) {
                    return { day: currentDay - 30, dayMonth: month + 1, dayYear: year, dayIndex: currentDay, weekDay: weekDay++ };
                }
                // display days of the current month (Meskerem)      
                return { day: currentDay, dayMonth: month, dayYear: year, dayIndex: currentDay, weekDay: weekDay++ };

            } else if (month === 11) {
                // display days of the previous month for Nehase (12th month)
                if (currentDay < 1) {
                    return { day: 30 + currentDay, dayMonth: month - 1, dayYear: year, dayIndex: currentDay, weekDay: weekDay++ };
                }
                // display days of the next month
                if (currentDay > 30) {
                    // check if the days count go to next month or first month of next year
                    if (currentDay <= extraDays) {
                        // display days of the 13th month (Pagume)
                        return { day: currentDay - 30, dayMonth: month + 1, dayYear: year, dayIndex: currentDay, weekDay: weekDay++ };
                    }
                    // display days of the first month of next year (Meskerem)    
                    return { day: currentDay - extraDays, dayMonth: 0, dayYear: year + 1, dayIndex: currentDay, weekDay: weekDay++ };
                }
                // display days of the current month (Nehase)
                return { day: currentDay, dayMonth: month, dayYear: year, dayIndex: currentDay, weekDay: weekDay++ };
            } else if (month === 12) {
                // display days of the previous month for Pagume (13th month)
                if (currentDay < 1) {
                    // display days of the 12th month (Nehase)
                    return { day: 30 + currentDay, dayMonth: month - 1, dayYear: year, dayIndex: currentDay, weekDay: weekDay++ };
                }
                if (currentDay > pagumeDays) {
                    // check if the days count go to the 1st month or 2nd month of next year
                    if (currentDay <= extraDays) {
                        // display days of the 1st month of next year (Meskerem)
                        return { day: currentDay - pagumeDays, dayMonth: 0, dayYear: year + 1, dayIndex: currentDay, weekDay: weekDay++ };
                    }
                    // display days of the 2nd month of next year (Tikimt)
                    return { day: currentDay - extraDays, dayMonth: 1, dayYear: year + 1, dayIndex: currentDay, weekDay: weekDay++ };
                }
                // display days of the current month (Pagume)
                return { day: currentDay, dayMonth: month, dayYear: year, dayIndex: currentDay, weekDay: weekDay++ };
            } else {
                // display the month days for any other month

                // display days of the previous month
                if (currentDay < 1) {
                    return { day: 30 + currentDay, dayMonth: month - 1, dayYear: year, dayIndex: currentDay, weekDay: weekDay++ };
                }
                // display days of the next month    
                if (currentDay > 30) {
                    return { day: currentDay - 30, dayMonth: month + 1, dayYear: year, dayIndex: currentDay, weekDay: weekDay++ };
                }
                // display days of the current month      
                return { day: currentDay, dayMonth: month, dayYear: year, dayIndex: currentDay, weekDay: weekDay++ };
            }
        })
    })
    return monthDays;
}

// get the week for the selected date for Gregorian or Ethiopic
export const getSelectedWeek = (selectedDate, isGregorian) => {
    const { selectedDay, selectedMonth, selectedYear } = selectedDate;
    const selectedMonthDays = isGregorian ?
        getMonthDaysGreg(selectedMonth, selectedYear) :
        getMonthDaysEthiopic(selectedMonth, selectedYear)
    let i, j;
    for (i = 0; i < selectedMonthDays.length; i++) {
        let week = selectedMonthDays[i]
        //all weeks have 7 days
        for (j = 0; j < 7; j++) {
            // identify the week where the selected date is located
            if (week[j].day === selectedDay && week[j].dayMonth === selectedMonth && week[j].dayYear === selectedYear) {
                return {
                    week,
                    weekIndex: i
                }
            }
        }
    }
}


